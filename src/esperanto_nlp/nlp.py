"""Análisis lingüístico de Esperanto mediante reglas gramaticales."""

import re


ESPERANTO_STOPWORDS = {
    "la", "kaj", "de", "en", "al", "estas", "esti",
    "estis", "estos", "por", "kun", "per", "sur",
    "pri", "sed", "ĉar", "ke", "ne", "kiel", "tiu",
    "tiuj", "tiun", "tiujn", "kiu", "kiuj", "kiun",
    "kiujn", "mi", "vi", "li", "ŝi", "ĝi", "ili",
    "ni", "oni", "sia", "sian", "siaj", "siajn",
    "ankaŭ", "nur", "jam", "pli", "plej", "tre",
    "tro", "ĉe", "post", "dum"
}

# Algunas palabras frecuentes necesitan una etiqueta conocida,
# porque no se pueden clasificar solo por su terminación.

PALABRAS_FUNCION = {
    "la": ("la", "DET"),

    "kaj": ("kaj", "CCONJ"),
    "sed": ("sed", "CCONJ"),
    "ĉar": ("ĉar", "SCONJ"),
    "ke": ("ke", "SCONJ"),

    "de": ("de", "ADP"),
    "en": ("en", "ADP"),
    "al": ("al", "ADP"),
    "por": ("por", "ADP"),
    "kun": ("kun", "ADP"),
    "per": ("per", "ADP"),
    "sur": ("sur", "ADP"),
    "pri": ("pri", "ADP"),
    "ĉe": ("ĉe", "ADP"),
    "post": ("post", "ADP"),
    "dum": ("dum", "ADP"),

    "ne": ("ne", "PART"),

    "kiel": ("kiel", "ADV"),
    "jam": ("jam", "ADV"),
    "ankaŭ": ("ankaŭ", "ADV"),
    "nur": ("nur", "ADV"),

    "mi": ("mi", "PRON"),
    "vi": ("vi", "PRON"),
    "li": ("li", "PRON"),
    "ŝi": ("ŝi", "PRON"),
    "ĝi": ("ĝi", "PRON"),
    "ili": ("ili", "PRON"),
    "ni": ("ni", "PRON"),
    "oni": ("oni", "PRON"),

    "tiu": ("tiu", "DET"),
    "tiuj": ("tiu", "DET"),
    "tiun": ("tiu", "DET"),
    "tiujn": ("tiu", "DET"),

    "kiu": ("kiu", "PRON"),
    "kiuj": ("kiu", "PRON"),
    "kiun": ("kiu", "PRON"),
    "kiujn": ("kiu", "PRON"),
}


class Token:
    """Representa un token con su lema y propiedades gramaticales."""

    def __init__(self, text, lemma, pos, is_stop, is_punct):
        self.text = text
        self.lemma_ = lemma
        self.pos_ = pos
        self.is_stop = is_stop
        self.is_punct = is_punct

    def __repr__(self):
        return (
            f"Token(text={self.text!r}, lemma={self.lemma_!r}, "
            f"pos={self.pos_!r}, stop={self.is_stop}, "
            f"punct={self.is_punct})"
        )


class Doc:
    """Agrupa los tokens y permite recorrerlos o recuperar sus lemas."""

    def __init__(self, tokens, original_text):
        self._tokens = tokens
        self._text = original_text

    def __iter__(self):
        return iter(self._tokens)

    def __len__(self):
        return len(self._tokens)

    def __getitem__(self, index):
        return self._tokens[index]

    @property
    def text(self):
        return self._text

    def lemmatized_text(
        self,
        remove_stopwords=True,
        remove_punct=True
    ):
        lemmas = []

        for token in self._tokens:

            if remove_punct and token.is_punct:
                continue

            if remove_stopwords and token.is_stop:
                continue

            lemmas.append(token.lemma_)

        return " ".join(lemmas)


class EsperantoNLP:
    """Pipeline aproximado basado en reglas para texto en Esperanto."""

    def __init__(self, stopwords=None):
        self.stopwords = (
            set(ESPERANTO_STOPWORDS)
            if stopwords is None
            else set(stopwords)
        )

    def _morphological_analysis(self, word):
        w = word.lower()

        # Las palabras funcionales se consultan antes de aplicar sufijos.
        if w in PALABRAS_FUNCION:
            return PALABRAS_FUNCION[w]

        # Terminaciones habituales de los verbos en Esperanto.
        for ending in ("as", "is", "os", "us"):

            if w.endswith(ending) and len(w) > len(ending):
                return w[:-len(ending)] + "i", "VERB"

        if w.endswith("u") and len(w) > 2:
            return w[:-1] + "i", "VERB"

        if w.endswith("i") and len(w) > 2:
            return w, "VERB"

        # Quitamos marcas de plural (-j) y acusativo (-n) cuando procede.
        base = w

        if (
            len(w) > 3
            and w.endswith("jn")
            and w[:-2].endswith(("o", "a"))
        ):
            base = w[:-2]

        elif (
            len(w) > 2
            and w.endswith("n")
            and w[:-1].endswith(("o", "a"))
        ):
            base = w[:-1]

        elif (
            len(w) > 2
            and w.endswith("j")
            and w[:-1].endswith(("o", "a"))
        ):
            base = w[:-1]

        # La última letra ayuda a reconocer sustantivos, adjetivos y adverbios.
        if base.endswith("o") and len(base) > 1:
            return base, "NOUN"

        if base.endswith("a") and len(base) > 1:
            return base, "ADJ"

        if base.endswith("e") and len(base) > 1:
            return base, "ADV"

        return w, "X"

    def __call__(self, text):

        if not isinstance(text, str):
            raise TypeError(
                "EsperantoNLP espera una cadena de texto."
            )

        # La expresión regular separa palabras y signos de puntuación.
        raw_tokens = re.findall(
            r"\w+|[^\w\s]",
            text,
            flags=re.UNICODE
        )

        doc_tokens = []

        for raw in raw_tokens:

            is_punct = bool(
                re.fullmatch(
                    r"[^\w\s]",
                    raw,
                    flags=re.UNICODE
                )
            )

            lower_raw = raw.lower()

            if is_punct:
                lemma, pos = raw, "PUNCT"
            else:
                lemma, pos = self._morphological_analysis(raw)

            token = Token(
                text=raw,
                lemma=lemma,
                pos=pos,
                is_stop=lower_raw in self.stopwords,
                is_punct=is_punct
            )

            doc_tokens.append(token)

        return Doc(doc_tokens, text)
