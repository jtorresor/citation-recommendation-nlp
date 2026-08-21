 Clasificación automática de la función de las citas en artículos académicos

**Proyecto de Desarrollo de Soluciones — Micro-proyecto**
Maestría en Inteligencia Artificial · Universidad de los Andes

## Descripción

Cuando un investigador revisa la literatura, no le basta saber que una fuente fue citada:
necesita saber con qué propósito fue invocada. Una referencia que aporta contexto general
no tiene el mismo peso que una cuyo método es efectivamente reutilizado, o que una señalada
como el trabajo que dejó un vacío por resolver. Hoy esa lectura se hace manualmente,
referencia por referencia.

Este proyecto construye un clasificador que, dado un contexto de cita en inglés, predice la
función con la que fue empleada la referencia, y lo expone a través de una API y un tablero
desplegados en contenedores Docker.

## Pregunta de negocio

> ¿Es posible identificar automáticamente, a partir de un contexto de cita en inglés, la
> función con la que fue empleada la referencia, y entregar ese resultado a través de una
> plataforma accesible que muestre la predicción y su nivel de confianza?

Preguntas específicas:

1. ¿Mejora el desempeño de la clasificación cuando se amplía la ventana de contexto que
   recibe el modelo, frente a usar únicamente la oración que contiene la mención de la cita?
2. ¿Qué ganancia aporta un encoder preentrenado en literatura científica frente a una línea
   base clásica de recuperación de información?
3. ¿Qué categorías concentran la mayor confusión entre sí?

## Datos

Se emplea **MultiCite** (Lauscher et al., NAACL 2022), disponible en
[allenai/multicite](https://github.com/allenai/multicite) bajo licencia CC BY-NC 2.0. El
conjunto reúne 12.653 contextos de cita anotados por expertos, provenientes de más de 1.200
artículos de lingüística computacional, y distribuye versiones del corpus con distintos
tamaños de ventana de contexto alrededor de la mención.

Las siete etiquetas nativas se agrupan en cinco categorías de trabajo:

| Categoría del proyecto | Etiqueta MultiCite          | Descripción                                                            |
| ---------------------- | --------------------------- | ---------------------------------------------------------------------- |
| Background             | Background                  | La referencia aporta información de contexto sobre el dominio           |
| Gap                    | Motivation                  | La referencia motiva el trabajo al evidenciar una necesidad no resuelta |
| Application            | Uses                        | El trabajo citante emplea una idea, método o herramienta del citado     |
| Improvement            | Extends                     | El trabajo citante extiende o modifica una idea o método del citado     |
| Comparison             | Similarities y Differences  | El trabajo citante señala semejanzas o diferencias frente al citado     |

La categoría `Future Work` queda excluida. Como MultiCite admite varias etiquetas por
contexto, la regla de reducción a etiqueta única está documentada en `docs/`.

Sobre ese esquema se construye un subconjunto balanceado de **700 ejemplos por categoría**
(aproximadamente 3.500 instancias), con particiones de entrenamiento, validación y prueba
aisladas a nivel de artículo. Los datos se versionan con **DVC**; en este repositorio solo
se conservan los archivos `.dvc` de referencia.

## Objetivos

- Construir el subconjunto balanceado de cinco categorías a partir de MultiCite, con la regla
  de mapeo documentada y reproducible.
- Entrenar una línea base clásica (TF-IDF con clasificador lineal) como referencia.
- Ajustar (fine-tuning) un clasificador supervisado sobre **SciBERT** con cabeza de cinco
  salidas.
- Comparar dos configuraciones de entrada: oración de la cita frente a ventana de contexto
  ampliada.
- Evaluar con precisión, recall y F1-score (macro y micro), y analizar la matriz de confusión.
- Empaquetar el modelo, exponerlo mediante una API y consumirlo desde un tablero, con
  despliegue en contenedores Docker.

## Estructura del repositorio

```
data/         Datos versionados con DVC (contenido no versionado en Git)
notebooks/    Exploración de los datos y experimentos
src/          Preparación, mapeo de categorías y entrenamiento
scripts/      Descarga del dataset y construcción del subconjunto balanceado
models/       Artefactos de modelos entrenados (referenciados por DVC)
api/          Servicio de inferencia y su Dockerfile
dashboard/    Tablero de visualización y su Dockerfile
docs/         Regla de mapeo de etiquetas y documentación
```

## Instalación

```bash
git clone https://github.com/jtorresor/citation-recommendation-nlp.git
cd citation-recommendation-nlp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
dvc pull
```

## Equipo

Ver `docs/` para el reporte de trabajo en equipo y la asignación de actividades.

## Nota académica

Proyecto desarrollado con fines académicos como parte del curso Proyecto de Desarrollo de
Soluciones, Maestría en Inteligencia Artificial, Universidad de los Andes. MultiCite se
emplea bajo los términos de su licencia CC BY-NC 2.0.
