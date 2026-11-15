"""Artículos semilla y secciones excluidas del corpus."""

CATEGORIAS = {
    "biologio": [
        "Biologio", "Ĉelo", "Genetiko", "Evoluismo",
        "Fotosintezo", "Zoologio", "Botaniko",
        "Mikrobiologio", "Ekologio", "DNA",
        "Anatomio", "Biodiverseco", "Metabolo"
    ],
    "kemio": [
        "Kemio", "Atomo", "Perioda tabelo", "Kemia ligo",
        "Organika kemio", "Neorganika kemio",
        "Kemia reakcio", "Acido", "Molekulo", "Katalizilo"
    ],
    "fiziko": [
        "Fiziko", "Klasika mekaniko", "Termodinamiko",
        "Elektromagnetismo", "Kvantuma mekaniko",
        "Relativeco", "Optiko", "Kinetika energio",
        "Partikla fiziko", "Astrofiziko", "Gravito",
        "Akustiko", "Nuklea fiziko"
    ]
}

SECCIONES_RUIDOSAS = {
    "referencoj",
    "referencoj kaj notoj",
    "eksteraj ligiloj",
    "vidu ankaŭ",
    "vidu ankau",
    "bibliografio",
    "literaturo",
    "notoj",
    "fontoj"
}
