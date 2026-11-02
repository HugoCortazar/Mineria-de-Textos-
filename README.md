# Minería de Textos en Esperanto

Práctica de Minería de Textos de CUNEF centrada en la clasificación de
textos científicos escritos en Esperanto.

## Entrega actual

El notebook [`MTPracticaFinal.ipynb`](MTPracticaFinal.ipynb) incluye:

- **Fase 1:** descarga de artículos desde Wikipedia, limpieza de párrafos,
  creación del dataset y validación de las clases `biologio`, `kemio` y
  `fiziko`.
- **Fase 2:** tokenización, lematización aproximada, etiquetado gramatical,
  detección de *stop-words* y pruebas básicas del modelo.

## Ejecución

1. Abrir `MTPracticaFinal.ipynb` en Google Colab.
2. Ejecutar las celdas en orden desde una sesión limpia.
3. Mantener `DESCARGAR_DESDE_WIKIPEDIA = True` para generar el dataset.
4. Comprobar al final el número de párrafos de cada categoría y el resultado
   de las pruebas del modelo.

La generación necesita conexión a Internet y puede tardar varios minutos
porque las peticiones a Wikipedia se realizan de forma espaciada.

## Estado conocido

La última ejecución obtuvo 1.031 párrafos válidos. La categoría `biologio`
quedó por debajo de la recomendación de 300 párrafos, por lo que se revisará
en una mejora posterior antes de cerrar la entrega.
