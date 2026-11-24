"""Vectorización y clasificación de textos científicos en Esperanto."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from .nlp import EsperantoNLP

_NLP = EsperantoNLP()


def lemmatize(text):
    """Normaliza un texto con las reglas del equipo para usarlo como entrada a TF-IDF."""
    return _NLP(text).lemmatized_text()


def build_classifier(use_nlp=True, seed=42):
    """Configura un pipeline sin ajustar, con o sin lematización propia."""
    representation = (
        {"preprocessor": lemmatize, "tokenizer": str.split, "token_pattern": None}
        if use_nlp else {}
    )
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, **representation)),
        ("classifier", LogisticRegression(max_iter=1000, random_state=seed)),
    ])
