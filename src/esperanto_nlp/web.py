"""Extracción de párrafos de páginas de Wikipedia y clasificación de su contenido."""

import re
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from .dataset import USER_AGENT, clean_paragraphs


@dataclass(frozen=True)
class WebPage:
    page_id: int
    paragraphs: tuple[str, ...]


def parse_wikipedia_page(html, lang="eo"):
    """Recoge los párrafos del cuerpo del artículo y su identificador canónico."""
    soup = BeautifulSoup(html, "html.parser")
    root = soup.html
    if root is None or root.get("lang") != lang:
        raise ValueError(f"El documento no declara el idioma {lang}")
    article = soup.select_one("#mw-content-text .mw-parser-output") or soup.select_one(".mw-parser-output")
    identifier = soup.find("meta", property="mw:pageId")
    if identifier is not None:
        page_id = int(identifier["content"])
    else:
        # La vista estándar de MediaWiki declara el ID en su configuración.
        config = re.search(r'"wgArticleId"\s*:\s*(\d+)', str(soup.head))
        page_id = int(config[1]) if config else 0
    if article is None or page_id <= 0:
        raise ValueError("No se encontró cuerpo de artículo con identificador de Wikipedia")

    for element in article.select(
        "sup.reference, table, figure, .navbox, .infobox, .hatnote, .mw-editsection"
    ):
        element.decompose()

    lines = []
    for element in article.select("h2, h3, h4, h5, h6, p"):
        text = element.get_text(" ", strip=True)
        if element.name == "p":
            lines.append(text)
        else:
            lines.append(f"== {text} ==")
    paragraphs = tuple(dict.fromkeys(clean_paragraphs("\n".join(lines))))
    if not paragraphs:
        raise ValueError("El artículo carece de párrafos utilizables")
    return WebPage(page_id, paragraphs)


def fetch_web_page(url, timeout=12):
    """Descarga HTML y devuelve el texto del artículo, o lanza un error legible."""
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    try:
        with urlopen(request, timeout=timeout) as response:
            html = response.read()
    except (URLError, TimeoutError) as error:
        raise ValueError(f"Error al descargar la página: {error}") from error
    return parse_wikipedia_page(html)


def classify_web_page(model, page, training_article_ids, training_texts):
    """Promedia la probabilidad por clase sobre párrafos ajenos al corpus."""
    if page.page_id in training_article_ids:
        raise ValueError("El artículo forma parte del corpus de entrenamiento")
    paragraphs = [paragraph for paragraph in page.paragraphs if paragraph not in training_texts]
    if not paragraphs:
        raise ValueError("Todos los párrafos utilizables aparecen en el entrenamiento")
    means = model.predict_proba(paragraphs).mean(axis=0)
    return len(paragraphs), dict(zip(model.classes_, means, strict=True))
