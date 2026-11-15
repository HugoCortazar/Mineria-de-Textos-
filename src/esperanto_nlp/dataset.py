"""Construcción y lectura del corpus de párrafos de Wikipedia en Esperanto."""

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from .corpus_config import CATEGORIAS, SECCIONES_RUIDOSAS

DATASET_CSV = "esperanto_scienco_dataset.csv"
SOURCES_CSV = "esperanto_scienco_fuentes.csv"
DATASET_COLUMNS = ["text", "class"]
SOURCE_COLUMNS = ["text_sha256", "article_id", "article_title", "article_revision"]
WIKIPEDIA_API = "https://eo.wikipedia.org/w/api.php"
USER_AGENT = "MineriaTextosEsperanto/1.0 (https://github.com/HugoCortazar/Mineria-de-Textos-/)"
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Article:
    """Texto y procedencia de una página de Wikipedia."""

    page_id: int
    title: str
    revision: int
    text: str


def retry_delay(value, attempt):
    """Lee Retry-After en segundos o en formato de fecha HTTP."""
    fallback = 2 ** (attempt + 1)
    if value is None:
        return fallback
    try:
        return max(fallback, float(value))
    except ValueError:
        try:
            date = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return fallback
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        return max(fallback, (date - datetime.now(timezone.utc)).total_seconds())


def fetch_article(title, attempts=3):
    """Devuelve una página y su revisión, o None al agotar los reintentos."""
    query = urlencode({
        "action": "query", "prop": "extracts|info", "explaintext": 1,
        "redirects": 1, "titles": title, "format": "json", "formatversion": 2,
    })
    request = Request(
        f"{WIKIPEDIA_API}?{query}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )

    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=10) as response:
                payload = json.load(response)
            pages = payload.get("query", {}).get("pages", [])
            if pages and pages[0].get("extract", "").strip():
                page = pages[0]
                return Article(page["pageid"], page["title"], page["lastrevid"], page["extract"])
            LOGGER.warning("Wikipedia no devolvió texto para %s", title)
            return None
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504):
                LOGGER.warning("HTTP %s en %s", error.code, title)
                return None
            wait = retry_delay(error.headers.get("Retry-After"), attempt)
        except (URLError, TimeoutError, ValueError) as error:
            LOGGER.warning("Error al leer %s: %s", title, error)
            wait = retry_delay(None, attempt)

        if attempt + 1 == attempts or wait > 20:
            break
        time.sleep(wait)

    LOGGER.warning("Se omite %s tras un fallo persistente", title)
    return None


def clean_paragraphs(text, minimum_length=60):
    """Extrae párrafos útiles de un extracto de texto de MediaWiki."""
    omit_section = False
    for line in text.splitlines():
        paragraph = line.strip()
        heading = re.fullmatch(r"(={2,})\s*(.*?)\s*\1", paragraph)
        plain_heading = paragraph.lower().strip(" .:")
        if heading:
            title = heading[2].lower()
            omit_section = any(section in title for section in SECCIONES_RUIDOSAS)
            continue
        if plain_heading in SECCIONES_RUIDOSAS:
            omit_section = True
            continue
        if omit_section or not paragraph:
            continue

        paragraph = re.sub(r"\[\d+\]|https?://\S+|<[^>]+>", " ", paragraph)
        paragraph = re.sub(r"\s+", " ", paragraph.replace(";", ",")).strip()
        if len(paragraph) >= minimum_length and "wayback machine" not in paragraph.casefold():
            yield paragraph


def text_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def collect_dataset(categories=CATEGORIAS, fetch=fetch_article, pause=1, minimum_per_class=30):
    """Recoge el corpus y su procedencia, manteniendo los fallos por artículo aislados."""
    rows = []
    for label, titles in categories.items():
        for title in titles:
            article = fetch(title)
            if article is not None:
                rows.extend(
                    (paragraph, label, article.page_id, article.title, article.revision)
                    for paragraph in clean_paragraphs(article.text)
                )
            time.sleep(pause)

    corpus = pd.DataFrame(rows, columns=DATASET_COLUMNS + SOURCE_COLUMNS[1:])
    label_counts = corpus.groupby("text")["class"].transform("nunique")
    corpus = corpus[label_counts == 1].drop_duplicates("text").reset_index(drop=True)
    counts = corpus["class"].value_counts().reindex(categories, fill_value=0)
    if (counts < minimum_per_class).any():
        raise ValueError(f"Párrafos insuficientes para regenerar el corpus: {counts.to_dict()}")

    sources = corpus[SOURCE_COLUMNS[1:]].copy()
    sources.insert(0, "text_sha256", corpus["text"].map(text_hash))
    return corpus[DATASET_COLUMNS], sources


def read_dataset(csv_path, sources_path):
    """Lee el CSV del enunciado y comprueba la correspondencia con su procedencia."""
    data = pd.read_csv(csv_path, sep=";", encoding="utf-8", keep_default_na=False)
    sources = pd.read_csv(sources_path, sep=";", encoding="utf-8", keep_default_na=False)
    if list(data.columns) != DATASET_COLUMNS or list(sources.columns) != SOURCE_COLUMNS:
        raise ValueError("Las cabeceras del corpus o de su fichero de fuentes son incorrectas")
    if data.empty or data["text"].str.strip().eq("").any() or data["text"].duplicated().any():
        raise ValueError("El corpus está vacío o contiene textos vacíos o duplicados")
    if data["text"].str.contains(";", regex=False).any() or set(data["class"]) != set(CATEGORIAS):
        raise ValueError("El corpus contiene separadores o clases no válidas")
    if not data["text"].map(text_hash).equals(sources["text_sha256"]):
        raise ValueError("El corpus y la procedencia no corresponden fila a fila")
    for column in ("article_id", "article_revision"):
        if not pd.api.types.is_integer_dtype(sources[column]) or (sources[column] <= 0).any():
            raise ValueError(f"Identificador inválido en {column}")
    if sources["article_title"].str.strip().eq("").any():
        raise ValueError("Hay artículos de origen sin título")
    return pd.concat([data, sources], axis=1)
