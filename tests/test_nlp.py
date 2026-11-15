import unittest

from esperanto_nlp import Doc, EsperantoNLP, Token


class EsperantoNLPTests(unittest.TestCase):
    def setUp(self):
        self.nlp = EsperantoNLP()

    def test_morphology_and_stopwords(self):
        expected_tokens = {
            "kaj": ("kaj", "CCONJ", True),
            "kun": ("kun", "ADP", True),
            "en": ("en", "ADP", True),
            "ĉeloj": ("ĉelo", "NOUN", False),
            "ĉelojn": ("ĉelo", "NOUN", False),
            "grandajn": ("granda", "ADJ", False),
            "domojn": ("domo", "NOUN", False),
            "legis": ("legi", "VERB", False),
            "iras": ("iri", "VERB", False),
            "estas": ("esti", "VERB", True),
            "rapide": ("rapide", "ADV", False),
        }
        for word, expected in expected_tokens.items():
            with self.subTest(word=word):
                token = self.nlp(word)[0]
                self.assertEqual((token.lemma_, token.pos_, token.is_stop), expected)

    def test_doc_exposes_original_text_and_unicode_tokens(self):
        text = "Ĉeloj, ĝardenoj!"
        doc = self.nlp(text)
        self.assertIsInstance(doc, Doc)
        self.assertEqual(doc.text, text)
        self.assertEqual(len(doc), 4)
        self.assertEqual([token.text for token in doc], ["Ĉeloj", ",", "ĝardenoj", "!"])
        self.assertIsInstance(doc[0], Token)
        self.assertTrue(doc[1].is_punct)

    def test_can_keep_stopwords_and_punctuation(self):
        doc = self.nlp("La ĉeloj.")
        self.assertEqual(doc.lemmatized_text(), "ĉelo")
        self.assertEqual(doc.lemmatized_text(remove_stopwords=False), "la ĉelo")
        self.assertEqual(doc.lemmatized_text(remove_punct=False), "ĉelo .")

    def test_custom_stopwords_and_empty_input(self):
        self.assertTrue(EsperantoNLP({"ĉeloj"})("Ĉeloj")[0].is_stop)
        self.assertFalse(EsperantoNLP(set())("kaj")[0].is_stop)
        self.assertEqual(len(self.nlp("")), 0)
        with self.assertRaises(TypeError):
            self.nlp(42)
