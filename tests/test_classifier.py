import unittest

from esperanto_nlp.classifier import build_classifier, lemmatize
from esperanto_nlp.web import WebPage, classify_web_page, parse_wikipedia_page


class ClassifierTests(unittest.TestCase):
    def setUp(self):
        texts = [
            "Ĉeloj enhavas genojn.", "La genoj regas la ĉelojn.",
            "Acidoj havas molekulojn.", "La molekuloj aperas en acidoj.",
            "Fortoj movas korpojn.", "La korpoj ricevas fortojn.",
        ]
        labels = ["biologio"] * 2 + ["kemio"] * 2 + ["fiziko"] * 2
        self.model = build_classifier().fit(texts, labels)

    def test_uses_the_esperanto_lemmatizer(self):
        self.assertEqual(lemmatize("La grandaj ĉeloj."), "granda ĉelo")
        self.assertIn("ĉelo", self.model.named_steps["tfidf"].vocabulary_)
        self.assertEqual(self.model.predict(["La ĉeloj havas genojn."])[0], "biologio")

    def test_web_prediction_checks_provenance_and_returns_probabilities(self):
        text = "La ĉeloj havas genojn."
        page = WebPage(page_id=20, paragraphs=(text, "La genoj estas studataj en ĉeloj."))
        count, probabilities = classify_web_page(self.model, page, {10}, {text})
        self.assertEqual(count, 1)
        self.assertEqual(set(probabilities), {"biologio", "kemio", "fiziko"})
        self.assertAlmostEqual(sum(probabilities.values()), 1.0)
        with self.assertRaisesRegex(ValueError, "corpus"):
            classify_web_page(self.model, page, {20}, set())


class ScrapingTests(unittest.TestCase):
    def test_extracts_esperanto_article_body_and_removes_references(self):
        html = """<html lang="eo"><head><meta property="mw:pageId" content="123"></head>
        <body><aside><p>Teksto kiu estas ekster la ĉefa parto de ĉi tiu artikolo.</p></aside>
        <div class="mw-parser-output">
        <p>La ĉelo estas la baza funkcia kaj struktura unuo de multaj vivantaj organismoj.
        <sup class="reference">[1]</sup></p>
        <h2>Referencoj</h2><p>Ĉi tiu frazo apartenas al la sekcio pri la referencoj kaj fontoj.</p>
        </div></body></html>"""
        page = parse_wikipedia_page(html)
        self.assertEqual(page.page_id, 123)
        self.assertEqual(
            page.paragraphs,
            ("La ĉelo estas la baza funkcia kaj struktura unuo de multaj vivantaj organismoj.",),
        )
        with self.assertRaisesRegex(ValueError, "idioma"):
            parse_wikipedia_page(html.replace('lang="eo"', 'lang="es"'))
