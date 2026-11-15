# Minería de Textos · Clasificación en Esperanto

Práctica de Minería de Textos de CUNEF Universidad. Clasificamos textos científicos en
**biología** (`biologio`), **química** (`kemio`) y **física** (`fiziko`). Las tres
disciplinas comparten vocabulario y permiten estudiar errores entre categorías cercanas.

## Ejecutar la práctica

[Abrir el cuaderno final en Google Colab](https://colab.research.google.com/github/HugoCortazar/Mineria-de-Textos-/blob/main/MTPracticaFinal.ipynb)
y seleccionar **Entorno de ejecución → Ejecutar todas** con CPU. El cuaderno instala la
librería y carga el corpus publicado. El entrenamiento se realiza durante la ejecución.
Para reproducir una revisión concreta, abrir el cuaderno de ese commit y usar el mismo
SHA en la variable `REF` de la primera celda.

| Ruta | Contenido |
|---|---|
| [MTPracticaFinal.ipynb](MTPracticaFinal.ipynb) | Corpus, demostración del NLP, evaluación, entrenamiento y predicción de páginas. |
| [MTPracticaFinal_intermedia.ipynb](MTPracticaFinal_intermedia.ipynb) | Versión histórica de las fases 1 y 2. |
| [src/esperanto_nlp/](src/esperanto_nlp/) | Librería de NLP y módulos de datos, clasificación y scraping. |
| [esperanto_scienco_dataset.csv](esperanto_scienco_dataset.csv) | Corpus UTF-8 con cabecera `text;class`. |
| [esperanto_scienco_fuentes.csv](esperanto_scienco_fuentes.csv) | Procedencia de cada párrafo, vinculada por su SHA-256. |
| [scripts/generar_dataset.py](scripts/generar_dataset.py) | Generación de ambos CSV. |
| [tests/](tests/) | Pruebas independientes de las webs externas. |

## Instalar y usar el NLP

Python 3.11 o posterior. Instalación desde GitHub:

```bash
python -m pip install "mineria-textos-esperanto @ git+https://github.com/HugoCortazar/Mineria-de-Textos-.git"
```

```python
from esperanto_nlp import EsperantoNLP

doc = EsperantoNLP()("La grandaj ĉeloj dividiĝas.")
for token in doc:
    print(token.text, token.lemma_, token.pos_, token.is_stop)

print(doc.lemmatized_text())  # granda ĉelo dividiĝi
```

`EsperantoNLP(stopwords=None)` devuelve un `Doc` al recibir una cadena. El documento
admite iteración e indexación y conserva el texto original en `doc.text`. Cada `Token`
expone `text`, `lemma_`, `pos_`, `is_stop` e `is_punct`. Se puede conservar la
puntuación o las palabras funcionales con los argumentos `remove_punct=False` y
`remove_stopwords=False` de `lemmatized_text()`. El NLP usa reglas aproximadas y carece
de desambiguación por contexto.

Para instalar el proyecto completo y ejecutar las pruebas desde un clon:

```bash
python -m pip install ".[proyecto]"
python -m unittest discover -s tests -v
```

GitHub Actions ejecuta el mismo comando de pruebas al actualizar una rama o un pull request.

## Corpus y regeneración

| Clase | Párrafos | Artículos |
|---|---:|---:|
| Biología | 399 | 13 |
| Química | 431 | 10 |
| Física | 349 | 13 |
| **Total** | **1.179** | **36** |

Consultamos la API de Wikipedia en Esperanto. Limpiamos y filtramos fragmentos y asignamos
a cada párrafo la etiqueta del artículo. En la evaluación usamos el identificador de
Wikipedia como grupo. El fichero de fuentes indica el título y la revisión de cada
artículo. Se puede localizar la revisión y su historial de autores en
`https://eo.wikipedia.org/wiki/Special:PermanentLink/ID_DE_REVISION`. El texto del corpus
procede de Wikipedia y se ha recortado y limpiado. Se distribuye conforme a la licencia
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

```bash
python scripts/generar_dataset.py
```

El generador registra los fallos por artículo y continúa con los demás. Comprueba la
cobertura de las clases antes de escribir los CSV. Como Wikipedia puede cambiar, el
cuaderno usa por defecto la versión publicada. Al regenerar el corpus, confirmad los
recuentos y guardad ambos ficheros en el mismo commit.

## Evaluación y clasificación web

Comparamos TF-IDF directo y TF-IDF con el NLP propio mediante regresión logística.
La validación cruzada agrupa por artículo para evitar que párrafos de la misma página
se repartan entre entrenamiento y prueba. Cada partición ajusta su propio TF-IDF.
El cuaderno incluye *accuracy*, F1 macro, métricas por clase y matriz de confusión.

Después entrenamos con el corpus completo y clasificamos tres páginas en Esperanto
fuera del corpus. Para cada página, promediamos las probabilidades de sus párrafos
válidos. Si falla una descarga o extracción, se registra la incidencia y se continúa
con las demás páginas. La evaluación y las demos comparten el dominio de Wikipedia.

## Colaboración

Proponed los cambios en una rama y abrid un pull request con el motivo del cambio y la
forma de probarlo. Pedid a otro integrante que lo revise antes de integrar. Para cambios
en los datos, revisad los dos CSV. Para cambios en el modelo, ejecutad todas las celdas y
conservad las salidas del cuaderno final.

## Uso de herramientas de IA

Esta versión de trabajo incorpora asistencia de IA en la revisión del código previo,
la extracción de la librería, la preparación de pruebas y el desarrollo del clasificador.
El equipo debe revisar estas aportaciones conforme al apartado 5.1 del enunciado y
poder explicar el preprocesamiento, las particiones, las métricas y los errores en la defensa.
