---
layout: default
title: IntenCite
---

# IntenCite

**Clasificación automática de la función semántica de citas en artículos académicos**

IntenCite es un prototipo basado en procesamiento de lenguaje natural que identifica el propósito con el que una referencia es utilizada dentro de un texto académico escrito en inglés.

La solución integra:

- Un modelo supervisado de clasificación.
- Una API de inferencia desarrollada con FastAPI.
- Un tablero web para interactuar con el modelo.
- Contenedores Docker para la API y la interfaz.
- Despliegue automatizado en AWS mediante GitHub Actions y Terraform.

![Interfaz principal de IntenCite](assets/user/01-interfaz-principal.png)

## Documentación

### [Manual de Usuario](manual-usuario.html)

Guía para utilizar la interfaz de IntenCite, ingresar un contexto de citación, ejecutar una clasificación e interpretar la predicción, la confianza y la distribución de probabilidades.

### [Manual de Instalación](manual-instalacion.html)

Guía para ejecutar IntenCite localmente mediante Docker Compose y desplegar la solución en AWS utilizando GitHub Actions, Terraform, Amazon ECR, ECS/Fargate y un Application Load Balancer.

## Funciones de citación

IntenCite clasifica cada contexto en una de cinco categorías:

| Categoría | Descripción |
|---|---|
| **Application** | Utiliza métodos, herramientas o ideas de un trabajo previo. |
| **Background** | Proporciona antecedentes o conocimiento general. |
| **Comparison** | Presenta similitudes o diferencias con trabajos anteriores. |
| **Gap** | Identifica limitaciones, necesidades o problemas no resueltos. |
| **Improvement** | Extiende, adapta o modifica una idea o método existente. |

## Modelo disponible

La versión actual utiliza:

```text
TF-IDF + Logistic Regression
```

El modelo está empaquetado con la API y puede utilizarse tanto desde el tablero como mediante el endpoint de predicción.

## Proyecto académico

Proyecto desarrollado para el curso **Proyecto de Desarrollo de Soluciones** de la Maestría en Inteligencia Artificial de la Universidad de los Andes.