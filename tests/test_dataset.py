from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from esperanto_nlp.dataset import (
    Article, clean_paragraphs, collect_dataset, fetch_article, read_dataset,
)


class DatasetTests(unittest.TestCase):
    def test_filters_references_sections_and_short_fragments(self):
        raw = """Ĉi tio estas teksto[1]; kun <b>etikedo</b> kaj https://example.org.
mallonga
== Referencoj ==
Tiu teksto devas esti forigita.
== Ĉefa sekcio ==
Tiu ĉi teksto restas en la datumbazo."""
        self.assertEqual(
            list(clean_paragraphs(raw, minimum_length=15)),
            [
                "Ĉi tio estas teksto , kun etikedo kaj",
                "Tiu ĉi teksto restas en la datumbazo.",
            ],
        )

    @patch("esperanto_nlp.dataset.time.sleep")
    @patch("esperanto_nlp.dataset.urlopen", side_effect=TimeoutError)
    def test_fetch_skips_article_after_retries(self, open_url, sleep):
        with self.assertLogs("esperanto_nlp.dataset", "WARNING"):
            self.assertIsNone(fetch_article("Biologio", attempts=2))
        self.assertEqual(open_url.call_count, 2)
        sleep.assert_called_once()

    def test_collection_skips_failed_article_and_keeps_aligned_sources(self):
        shared = "La suno aperas super la montoj dum la hela mateno en ĉi tiu loko."
        texts = {
            "Ĉelo": Article(1, "Ĉelo", 101, f"{shared}\n" + "La ĉelo enhavas genojn. " * 4),
            "Atomo": Article(2, "Atomo", 102, f"{shared}\n" + "La atomo havas kernon. " * 4),
            "Lumo": Article(3, "Lumo", 103, "La lumo atingas la okulon. " * 4),
        }
        categories = {"biologio": ["Mankanta", "Ĉelo"], "kemio": ["Atomo"], "fiziko": ["Lumo"]}
        data, origins = collect_dataset(categories, fetch=texts.get, pause=0, minimum_per_class=1)
        self.assertEqual(list(data.columns), ["text", "class"])
        self.assertEqual(list(data["class"]), ["biologio", "kemio", "fiziko"])
        self.assertNotIn(shared, set(data["text"]))

        with TemporaryDirectory() as folder:
            csv = Path(folder) / "data.csv"
            sources = Path(folder) / "sources.csv"
            data.to_csv(csv, sep=";", index=False)
            origins.to_csv(sources, sep=";", index=False)
            self.assertEqual(list(read_dataset(csv, sources)["article_id"]), [1, 2, 3])
            origins.iloc[::-1].to_csv(sources, sep=";", index=False)
            with self.assertRaisesRegex(ValueError, "fila a fila"):
                read_dataset(csv, sources)

    def test_incomplete_regeneration_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "insuficientes"):
            collect_dataset({"biologio": ["Mankanta"]}, fetch=lambda _: None, pause=0)
