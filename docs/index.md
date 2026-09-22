---
layout: default
title: IntenCite
---

# IntenCite

**Clasificación automática de la función semántica de citas en artículos académicos**

IntenCite es un prototipo de procesamiento de lenguaje natural que identifica la función semántica que cumple una referencia dentro de un texto académico escrito en inglés.

A partir de un contexto de citación, la aplicación clasifica la referencia en una de cinco categorías: **Application, Background, Comparison, Gap** o **Improvement**.

La solución integra:

- Dos modelos de clasificación disponibles desde la interfaz.
- Una API de inferencia desarrollada con FastAPI.
- Un tablero web para ingresar contextos de citación y visualizar resultados.
- Contenedores Docker para la API y la interfaz.
- Ejecución local mediante Docker Compose.
- Despliegue automatizado en AWS mediante GitHub Actions y Terraform.
- Amazon ECR para almacenar las imágenes Docker.
- Amazon ECS con AWS Fargate para ejecutar los servicios.
- Un Application Load Balancer para enrutar el tráfico entre la interfaz y la API.
- Amazon CloudWatch para consultar los registros de ejecución.

![Interfaz principal de IntenCite](assets/user/01-interfaz-principal.png)

## Documentación

### [Manual de Usuario](manual-usuario.html)

Guía para utilizar la interfaz de IntenCite, seleccionar un modelo, ingresar un contexto de citación, ejecutar una clasificación e interpretar la categoría predicha, la confianza y la distribución de probabilidades.

### [Manual de Instalación](manual-instalacion.html)

Guía para ejecutar IntenCite localmente mediante Docker Compose y desplegar la solución en AWS utilizando GitHub Actions, Terraform, Amazon ECR, ECS/Fargate y un Application Load Balancer.

## Funciones de citación

IntenCite clasifica cada contexto en una de cinco categorías:

| Categoría | Descripción |
|---|---|
| **Application** | El trabajo citante utiliza métodos, herramientas, recursos o ideas provenientes del trabajo citado. |
| **Background** | La referencia proporciona antecedentes, contexto o conocimiento general sobre el dominio o problema. |
| **Comparison** | El texto establece similitudes o diferencias entre el trabajo actual y el trabajo citado. |
| **Gap** | La referencia evidencia una limitación, necesidad o problema aún no resuelto que motiva el trabajo. |
| **Improvement** | El trabajo citante extiende, adapta o modifica una idea o método presentado previamente. |

## Modelos disponibles

La aplicación permite seleccionar entre dos modelos desde la interfaz.

### TF-IDF + Logistic Regression

Modelo supervisado utilizado como línea base del proyecto.

Utiliza una representación TF-IDF del contexto de citación y una regresión logística multiclase para predecir una de las cinco funciones de citación.

El artefacto del modelo se encuentra empaquetado junto con la API:

```text
models/tfidf_logreg_baseline_v1.joblib
```

### Qwen2.5 1.5B + LoRA

El segundo modelo utiliza como base:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

El modelo fue adaptado al problema de clasificación mediante **LoRA (Low-Rank Adaptation)**.

El adaptador entrenado se encuentra en:

```text
models/lora_adapter/
```

Durante la inferencia, el sistema evalúa las cinco etiquetas posibles utilizando la probabilidad promedio de sus tokens y selecciona la categoría con mayor puntuación.

Para reducir el tiempo de inferencia, la implementación reutiliza el estado calculado para el prompt compartido mediante **KV cache**, evitando procesar nuevamente el mismo contexto completo para cada categoría.

El modelo base Qwen se incluye dentro de la imagen Docker de la API. De esta forma, el contenedor desplegado no necesita descargar el modelo desde Hugging Face durante la primera solicitud.

## Selección del modelo

El modelo activo puede seleccionarse desde el control ubicado en la parte superior derecha de la interfaz.

Los modelos disponibles también pueden consultarse mediante:

```text
GET /api/v1/models
```

Actualmente se encuentran disponibles:

```text
TF-IDF + Logistic Regression
Qwen2.5 1.5B + LoRA
```

La clasificación se realiza mediante:

```text
POST /api/v1/predict
```

La solicitud incluye tanto el contexto de citación como el identificador del modelo seleccionado.

## Resultados de la clasificación

Para cada solicitud, IntenCite presenta:

- La función de citación predicha.
- El nivel de confianza asociado a la predicción.
- La distribución de probabilidades entre las cinco categorías.
- El modelo utilizado para realizar la inferencia.

![Ejemplo de análisis en IntenCite](assets/user/03-ejemplo-analisis.png)

## Estadísticas del corpus

La interfaz incluye una sección con información resumida sobre el conjunto de datos utilizado durante el proyecto.

Actualmente se muestran:

| Métrica | Valor |
|---|---:|
| Contextos de citación | 3,491 |
| Pares citante-citado | 1,046 |
| Clases | 5 |
| Entrenamiento | 2,491 |
| Validación | 483 |
| Prueba | 517 |

![Estadísticas del corpus](assets/user/02-estadisticas-corpus.png)

## Arquitectura de la solución

### Ejecución local

La ejecución local utiliza Docker Compose y tres servicios principales:

```text
Navegador
    |
    v
Nginx Gateway
   /       \
  /         \
App        API
Nginx    FastAPI
```

El gateway local reproduce la responsabilidad de enrutamiento que cumple el Application Load Balancer en AWS.

Las rutas principales son:

```text
/          → interfaz web
/api/*     → API de inferencia
/health    → API de inferencia
```

El contenedor de la interfaz utiliza Nginx únicamente para servir los archivos estáticos del tablero.

### Despliegue en AWS

En AWS, el gateway local es reemplazado por un **Application Load Balancer**:

```text
Navegador
    |
    v
Application Load Balancer
       /           \
      /             \
IntenCite App    IntenCite API
   Nginx           FastAPI
```

Los servicios se ejecutan mediante Amazon ECS utilizando AWS Fargate.

Las imágenes Docker se almacenan en Amazon ECR y la infraestructura se administra mediante Terraform.

La configuración desplegada asigna recursos diferentes a cada servicio. La API que ejecuta Qwen2.5 1.5B + LoRA utiliza una tarea Fargate con:

```text
CPU:     2048
Memoria: 8192 MiB
```

El tablero requiere una cantidad significativamente menor de recursos.

## Despliegue automatizado

El despliegue completo puede iniciarse manualmente desde GitHub Actions.

El workflow:

```text
.github/workflows/deploy.yml
```

realiza las siguientes etapas:

1. Descarga el contenido del repositorio.
2. Configura las credenciales temporales de AWS Academy.
3. Obtiene dinámicamente el identificador de la cuenta AWS.
4. Prepara el backend remoto de Terraform en Amazon S3.
5. Crea o reutiliza los repositorios de Amazon ECR.
6. Construye las imágenes Docker de la API y del tablero.
7. Publica las imágenes en Amazon ECR.
8. Ejecuta Terraform para crear o actualizar la infraestructura.
9. Despliega los servicios en Amazon ECS con AWS Fargate.
10. Espera a que los servicios alcancen un estado estable.
11. Obtiene la dirección pública del Application Load Balancer.
12. Publica la URL de la aplicación en el resumen de GitHub Actions.

La infraestructura también puede eliminarse mediante:

```text
.github/workflows/destroy.yml
```

La URL generada por el Application Load Balancer puede cambiar cada vez que la infraestructura se destruye y se vuelve a crear, por lo que no se almacena una dirección fija dentro de la documentación.

## Tecnologías principales

IntenCite utiliza:

- Python 3.12
- FastAPI
- scikit-learn
- PyTorch
- Transformers
- PEFT
- LoRA
- Qwen2.5-1.5B-Instruct
- Docker
- Docker Compose
- Nginx
- GitHub Actions
- Terraform
- Amazon ECR
- Amazon ECS
- AWS Fargate
- Application Load Balancer
- Amazon CloudWatch
- Amazon S3
- MLflow