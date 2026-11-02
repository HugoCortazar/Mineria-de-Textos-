# Minería de Textos · Textos científicos en Esperanto

Práctica grupal de **Minería de Textos (CUNEF Universidad)**. Nuestro objetivo es construir un sistema que permita clasificar textos escritos en Esperanto según tres temáticas científicas: **biología (`biologio`)**, **química (`kemio`)** y **física (`fiziko`)**.

Elegimos estas categorías porque pertenecen a un mismo ámbito y comparten parte del vocabulario, pero también presentan términos específicos. Esto nos permite plantear un problema de clasificación con cierta dificultad y estudiar posteriormente los errores del modelo.

**Estado actual: entrega intermedia — fases 1 y 2.** Hemos preparado el dataset y desarrollado un procesador NLP propio. La vectorización, el entrenamiento y la clasificación de páginas web corresponden a la entrega final.

[Abrir el notebook en Google Colab](https://colab.research.google.com/github/HugoCortazar/Mineria-de-Textos-/blob/main/MTPracticaFinal.ipynb)

## 1. Construcción del dataset

Recuperamos artículos mediante la **API de Wikipedia en Esperanto**. Seleccionamos artículos relacionados con cada temática, extraemos su texto y lo dividimos en párrafos. Cada párrafo recibe la etiqueta temática del artículo de origen.

Aplicamos después varias reglas de limpieza: eliminación de referencias, enlaces y marcas HTML; exclusión de apartados bibliográficos; normalización de espacios; sustitución del carácter `;`; y descarte de fragmentos de menos de 60 caracteres. También eliminamos duplicados y párrafos idénticos que aparezcan con etiquetas contradictorias.

El resultado se guarda en `esperanto_scienco_dataset.csv`, respetando el contrato de datos del enunciado: **codificación UTF-8, separador `;`, cabecera `text;class` y una fila por párrafo**.

### Resultados de la última ejecución

| Categoría | Párrafos válidos |
|---|---:|
| Biología (`biologio`) | 406 |
| Química (`kemio`) | 431 |
| Física (`fiziko`) | 353 |
| **Total** | **1.190** |

Las tres clases superan los 300 párrafos recomendados en el enunciado.

Durante la recogida y limpieza consideramos **2.659 bloques no vacíos** y descartamos **1.465** por las reglas de filtrado (**55,10 %**). Esta cifra mide descartes durante la limpieza, **no errores en las etiquetas**. La cantidad final de filas también refleja las comprobaciones de duplicados y etiquetas contradictorias.

## 2. Procesamiento del lenguaje natural

Implementamos un procesador propio de Esperanto, **basado en reglas y sin utilizar librerías de NLP preexistentes** para las funciones lingüísticas. Su interfaz se inspira en la forma de trabajar de spaCy, con tres componentes principales:

- **`Token`**: representa cada palabra o signo e incorpora su texto, lema, categoría gramatical (`pos_`) e indicadores de *stopword* y puntuación.
- **`Doc`**: agrupa los tokens, permite recorrerlos y generar una versión lematizada del texto.
- **`EsperantoNLP`**: realiza tokenización Unicode, lematización aproximada, etiquetado gramatical mediante terminaciones y consulta de palabras funcionales frecuentes.

Aprovechamos regularidades del Esperanto para reconocer, por ejemplo, el plural de sustantivos (`ĉeloj → ĉelo`) o formas verbales (`legis → legi`). Estas reglas son interpretables, pero no resuelven todos los casos morfológicos ni las ambigüedades de contexto.

El cuaderno incluye ejemplos y **pruebas con `assert`** sobre lemas, etiquetas POS, *stopwords*, puntuación, caracteres propios del Esperanto y entradas no válidas.

## 3. Archivos de esta entrega

| Archivo | Contenido |
|---|---|
| [`MTPracticaFinal.ipynb`](MTPracticaFinal.ipynb) | Descarga, limpieza y validación del dataset; implementación y pruebas del NLP. |
| [`esperanto_scienco_dataset.csv`](esperanto_scienco_dataset.csv) | Dataset etiquetado, listo para utilizarse en la fase de clasificación. |
| `README.md` | Objetivo, metodología, resultados e instrucciones de ejecución. |

## 4. Cómo ejecutar el notebook

1. Abrimos [`MTPracticaFinal.ipynb`](MTPracticaFinal.ipynb) en **Google Colab**.
2. En la primera celda de código elegimos el valor de `DESCARGAR_DESDE_WIKIPEDIA`:
   - `True`: recuperamos los artículos y reconstruimos el CSV. Necesita conexión a Internet y puede tardar varios minutos; espaciamos las peticiones e incorporamos reintentos ante fallos temporales.
   - `False`: utilizamos el CSV ya generado. El cuaderno busca primero el archivo en el entorno de Colab y, si no está disponible, intenta descargarlo desde la rama `main` del repositorio.
3. Seleccionamos **Entorno de ejecución → Ejecutar todas**.
4. Revisamos los recuentos por clase, las comprobaciones de formato, el ejemplo de análisis lingüístico y el mensaje final de las pruebas.

Para reproducir rápidamente la entrega intermedia **una vez que el CSV esté publicado en `main`**, recomendamos `DESCARGAR_DESDE_WIKIPEDIA = False` en una sesión nueva de Colab. El código de generación se conserva en el propio cuaderno.

## 5. Comprobaciones y limitaciones

Validamos que el dataset contiene las columnas y clases esperadas, que no hay valores vacíos ni duplicados exactos, y que los textos no incluyen el separador `;`. Utilizamos una muestra reproducible de párrafos para facilitar su **inspección manual**, sin presentarla como una medición del ruido ya realizada.

La principal limitación del dataset es que **heredamos la etiqueta del artículo**: algunos párrafos pueden ser genéricos o referirse a varias disciplinas. Asimismo, el lematizador y el etiquetador gramatical se basan en reglas aproximadas; evaluaremos su utilidad al construir el clasificador.

## 6. Continuación del proyecto

En la fase final utilizaremos nuestro NLP para vectorizar los textos, entrenaremos y evaluaremos un clasificador (incluyendo *accuracy*, F1 macro y matriz de confusión) y probaremos sus predicciones con texto extraído de páginas web reales en Esperanto.

Además, estamos organizando el desarrollo mediante **Git, ramas y Pull Requests** para optar al extra de arquitectura de software. La **librería instalable con `pip`, sus tests independientes y la documentación del paquete** son objetivos de la continuación del proyecto; no se presentan como completados en este punto de control.

### Uso de herramientas de IA

Utilizamos herramientas de IA como apoyo para consultar dudas técnicas, revisar código y mejorar la claridad de las explicaciones. Contrastamos las propuestas con el enunciado, el temario y las pruebas del cuaderno, manteniendo las decisiones de diseño y su justificación como responsabilidad del equipo.
