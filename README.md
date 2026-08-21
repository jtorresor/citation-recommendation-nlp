# Recomendación local de citas y clasificación de su función en artículos académicos

**Proyecto de Desarrollo de Soluciones — Micro-proyecto**
Maestría en Inteligencia Artificial · Universidad de los Andes

## Descripción

Este proyecto aborda la comprensión automática de citas académicas en inglés mediante dos tareas de Procesamiento del Lenguaje Natural (PLN):

1. **Recuperación local de citas**: dado un contexto de cita, identificar los fragmentos más similares dentro del artículo citado, usando recuperación densa basada en SciBERT.
2. **Clasificación de la función de cita**: categorizar el propósito retórico de cada cita (por ejemplo, si fundamenta un método, compara un resultado o señala una limitación) dentro de un esquema de 9 categorías.

## Pregunta de negocio

> ¿Es posible construir un sistema automático que, a partir de un contexto de cita dentro de un artículo científico en inglés, recupere los fragmentos más relevantes del documento citado y clasifique la función retórica que cumple dicha cita, apoyándose en encoders especializados en literatura científica y en modelos de lenguaje de gran escala?

## Objetivos

- Extraer y procesar un corpus de documentos científicos en inglés a partir de **arXiv** (formatos PDF/LaTeX), con énfasis en el área de computación.
- Implementar una estrategia de recuperación densa basada en **SciBERT** para extraer el Top 3 de párrafos más similares dentro del artículo citado para cada contexto de cita.
- Construir y curar, con apoyo de un pre-etiquetado automático (esquema de jueces con modelos de pesos abiertos), un dataset balanceado con al menos 2.000 ejemplos por categoría, validando manualmente un 15% del total.
- Ajustar (fine-tuning) clasificadores supervisados basados en encoders especializados en literatura científica (SciBERT, SPECTER).
- Evaluar modelos de lenguaje comerciales vía API (GPT-4o/5, Gemini) en modo inferencia, comparando estrategias de prompting.
- Desarrollar un demostrador interactivo que integre el flujo completo de recuperación de fragmentos y clasificación de funciones de cita.

## Datos

El dataset se construye a partir del corpus arXiv y se versiona con **DVC**, en un repositorio separado de este. Aquí solo se conservan los archivos `.dvc` de referencia.

## Instalación

```bash
git clone https://github.com/<usuario-o-equipo>/<nombre-del-repositorio>.git
cd <nombre-del-repositorio>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Nota académica

Proyecto desarrollado con fines académicos como parte del curso Proyecto de Desarrollo de Soluciones, Maestría en Inteligencia Artificial, Universidad de los Andes.
