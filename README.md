# IntenCite - Citation Function Classification

**Clasificación automática de la función semántica de citas en artículos académicos**

**Proyecto de Desarrollo de Soluciones - Micro-proyecto**  
Maestría en Inteligencia Artificial · Universidad de los Andes

IntenCite es un prototipo de procesamiento de lenguaje natural que identifica la función con la que una referencia es utilizada dentro de un texto académico escrito en inglés.

El sistema clasifica cada contexto de citación en una de cinco categorías:

- **Background**
- **Gap**
- **Application**
- **Improvement**
- **Comparison**

La solución incluye preparación y versionamiento de datos, experimentación con diferentes modelos de NLP, seguimiento mediante MLflow, una API de inferencia desarrollada con FastAPI, una interfaz web, contenedores Docker y despliegue automatizado en AWS mediante GitHub Actions y Terraform.

## Documentación

La documentación del proyecto se encuentra publicada en GitHub Pages:

https://jtorresor.github.io/citation-recommendation-nlp/

Incluye:

- Manual de usuario.
- Manual de instalación.
- Descripción de los modelos disponibles.
- Arquitectura local y en AWS.
- Instrucciones de despliegue y operación.

---

## Problema

Cuando un investigador revisa literatura científica, saber que una fuente fue citada no es suficiente. También resulta útil identificar con qué propósito fue utilizada.

Una referencia puede:

- Proporcionar antecedentes.
- Evidenciar una necesidad o vacío.
- Aportar un método utilizado por el trabajo actual.
- Ser extendida o modificada.
- Ser comparada con el enfoque propuesto.

La identificación manual de estas funciones requiere revisar cada contexto de citación individualmente.

IntenCite aborda este problema mediante modelos supervisados capaces de clasificar automáticamente el propósito de una referencia a partir del texto que la rodea.

---

## Pregunta de negocio

> ¿Es posible identificar automáticamente, a partir de un contexto de cita en inglés, la función con la que fue empleada una referencia y entregar ese resultado mediante una plataforma accesible que muestre la predicción y su nivel de confianza?

Durante el proyecto también se estudiaron las siguientes preguntas:

1. ¿Cómo cambia el desempeño cuando se amplía la ventana de contexto frente a utilizar únicamente la oración que contiene la cita?
2. ¿Qué ventajas ofrecen modelos preentrenados frente a una línea base clásica basada en TF-IDF?
3. ¿Qué efecto tiene adaptar un modelo de lenguaje mediante LoRA para esta tarea?
4. ¿Qué categorías presentan mayor dificultad de clasificación?

---

## Datos

El proyecto utiliza **MultiCite**, presentado por Lauscher et al. en NAACL 2022.

Repositorio original:

https://github.com/allenai/multicite

MultiCite contiene aproximadamente **12.6K contextos de citación** provenientes de más de **1.2K artículos de lingüística computacional**, e incluye contextos multi-oración y multi-etiqueta.

El conjunto se distribuye bajo licencia **CC BY-NC 2.0**.

Las etiquetas originales relevantes se transformaron a cinco categorías de trabajo:

| Categoría IntenCite | Etiqueta MultiCite | Descripción |
|---|---|---|
| **Background** | Background | La referencia aporta información de contexto sobre el dominio. |
| **Gap** | Motivation | La referencia motiva el trabajo al evidenciar una necesidad no resuelta. |
| **Application** | Uses | El trabajo citante utiliza una idea, método o herramienta del trabajo citado. |
| **Improvement** | Extends | El trabajo citante extiende o modifica una idea o método previo. |
| **Comparison** | Similarities + Differences | El texto señala semejanzas o diferencias respecto al trabajo citado. |

La categoría `Future Work` se excluyó de la clasificación final.

Como MultiCite permite múltiples etiquetas por contexto, durante la preparación de los datos se aplicó una regla de transformación a una única clase de trabajo.

---

## Corpus preparado

El conjunto final utilizado por IntenCite contiene:

| Métrica | Valor |
|---|---:|
| Contextos de citación | 3,491 |
| Pares artículo citante-citado | 1,046 |
| Categorías | 5 |
| Entrenamiento | 2,491 |
| Validación | 483 |
| Prueba | 517 |

La distribución final es aproximadamente balanceada:

```text
Background   700
Gap          700
Comparison   700
Application  700
Improvement  691
```

La separación se realizó a nivel del par entre artículo citante y artículo citado para evitar que un mismo par apareciera simultáneamente en entrenamiento, validación y prueba.

Los datos se versionan mediante **DVC**.

---

## Modelos experimentados

Durante el proyecto se evaluaron diferentes estrategias de clasificación.

| Modelo | Contexto | Accuracy validación | F1 macro validación |
|---|---|---:|---:|
| TF-IDF + Logistic Regression | Contexto preparado | 0.5135 | 0.5125 |
| SciBERT fine-tuning | Una oración | 0.6563 | 0.6455 |
| SciBERT frozen encoder | 3 contextos | 0.5300 | 0.5304 |
| Qwen2.5 1.5B + LoRA | 3 contextos | **0.6832** | **0.6822** |

Los resultados muestran que aumentar la cantidad de contexto no garantiza automáticamente un mejor desempeño.

El experimento con SciBERT de tres contextos utiliza el encoder congelado como extractor de características y no corresponde a un fine-tuning completo.

El conjunto de prueba se mantuvo separado durante el desarrollo de los modelos.

---

## Modelos disponibles en la aplicación

La API desplegada permite seleccionar entre dos modelos.

### TF-IDF + Logistic Regression

Modelo clásico utilizado como línea base.

Artefacto:

```text
models/tfidf_logreg_baseline_v1.joblib
```

Identificador de API:

```text
tfidf-logreg-baseline-v1
```

### Qwen2.5 1.5B + LoRA

Modelo basado en:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

adaptado mediante **LoRA (Low-Rank Adaptation)**.

El adaptador se encuentra en:

```text
models/lora_adapter/
```

Identificador de API:

```text
qwen2.5-1.5b-lora-3ctx
```

La inferencia no se realiza mediante generación libre de texto.

Para cada contexto, el sistema evalúa las cinco etiquetas posibles utilizando la media de las log-probabilidades de sus tokens:

```text
Application
Background
Comparison
Gap
Improvement
```

La categoría con mayor puntuación se utiliza como predicción.

La implementación reutiliza el estado del prompt mediante **KV cache**, reduciendo el procesamiento repetido durante la evaluación de las etiquetas.

---

## Arquitectura

### Ejecución local

La solución local utiliza Docker Compose:

```text
Browser
   |
   v
Nginx Gateway :8080
   /          \
  /            \
App            API
Nginx        FastAPI
              :8001
```

El gateway local reproduce el comportamiento de enrutamiento utilizado posteriormente por AWS.

Las rutas principales son:

```text
/          -> frontend
/api/*     -> FastAPI
/health    -> FastAPI
```

El frontend conserva la misma responsabilidad en ambos ambientes: servir únicamente los archivos estáticos de la interfaz.

### AWS

En producción, el gateway local es reemplazado por un **Application Load Balancer**:

```text
Browser
   |
   v
Application Load Balancer
       /          \
      /            \
ECS App          ECS API
Nginx           FastAPI
```

La solución utiliza:

- Amazon ECR para almacenar las imágenes Docker.
- Amazon ECS.
- AWS Fargate.
- Application Load Balancer.
- Amazon CloudWatch Logs.
- Amazon S3 para el estado remoto de Terraform.
- Terraform para infraestructura como código.
- GitHub Actions para CI/CD.

La API desplegada utiliza actualmente:

```text
2 vCPU
8 GiB RAM
```

mientras que el frontend utiliza una tarea Fargate significativamente más pequeña.

---

## Estructura del repositorio

```text
citation-recommendation-nlp/
├── .github/
│   └── workflows/
│       ├── deploy.yml
│       └── destroy.yml
│
├── api/
│   ├── Dockerfile
│   ├── main.py
│   ├── routes.py
│   └── schemas.py
│
├── app/
│   ├── Dockerfile
│   ├── index.html
│   ├── nginx.conf
│   └── static/
│
├── gateway/
│   └── nginx.conf
│
├── infra/
│   ├── intencite/
│   └── mlflow-server/
│
├── models/
│   ├── lora_adapter/
│   └── tfidf_logreg_baseline_v1.joblib
│
├── notebooks/
│
├── src/
│   └── intencite/
│       ├── config.py
│       ├── predict.py
│       └── predict_lora.py
│
├── docs/
├── data.dvc
├── docker-compose.intencite.yml
├── docker-compose.yml
├── pyproject.toml
├── requirements-api.txt
├── uv.lock
└── README.md
```

---

## Herramientas utilizadas

El proyecto utiliza:

- Python 3.12
- uv
- DVC
- MLflow
- scikit-learn
- PyTorch
- Transformers
- PEFT / LoRA
- Qwen2.5
- SciBERT
- FastAPI
- Nginx
- Docker
- Docker Compose
- GitHub Actions
- Terraform
- Amazon ECR
- Amazon ECS
- AWS Fargate
- Application Load Balancer
- Amazon CloudWatch
- Amazon S3

---

## Configuración del entorno Python

### Requisitos

- Git
- Python 3.12
- uv

La versión esperada de Python se encuentra definida en:

```text
.python-version
```

Clone el repositorio:

```bash
git clone https://github.com/jtorresor/citation-recommendation-nlp.git
cd citation-recommendation-nlp
```

Instale las dependencias:

```bash
uv sync
```

---

## Descarga de datos con DVC

Los datos utilizados durante los experimentos se administran mediante DVC.

Para colaboradores autorizados se requiere:

1. Acceso al almacenamiento remoto de DVC.
2. Acceso a la aplicación OAuth configurada para Google Drive.
3. `GDRIVE_CLIENT_ID`.
4. `GDRIVE_CLIENT_SECRET`.

Las credenciales nunca deben almacenarse en Git.

Configure localmente:

```bash
uv run dvc remote modify --local gdrive gdrive_client_id <EL_CLIENT_ID>
uv run dvc remote modify --local gdrive gdrive_client_secret <EL_CLIENT_SECRET>
```

Descargue los datos:

```bash
uv run dvc pull
```

Durante la autenticación puede abrirse el navegador para autorizar el acceso a Google Drive.

---

## Ejecución local de IntenCite

La aplicación completa se ejecuta mediante:

```bash
docker compose -f docker-compose.intencite.yml build
docker compose -f docker-compose.intencite.yml up -d
```

Abra:

```text
http://localhost:8080
```

La API también se encuentra disponible directamente en:

```text
http://localhost:8001
```

Swagger:

```text
http://localhost:8001/docs
```

Verifique el estado:

```bash
curl http://localhost:8080/health
```

Consulte los modelos:

```bash
curl http://localhost:8080/api/v1/models
```

Para detener la aplicación:

```bash
docker compose -f docker-compose.intencite.yml down
```

Para instrucciones completas consulte el **Manual de Instalación** publicado en GitHub Pages.

---

## API

### Health check

```text
GET /health
```

### Modelos disponibles

```text
GET /api/v1/models
```

### Clasificación

```text
POST /api/v1/predict
```

Ejemplo:

```bash
curl -X POST "http://localhost:8001/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "We use the method introduced by Smith et al. to preprocess the documents used in our experiments.",
    "model": "tfidf-logreg-baseline-v1"
  }'
```

La respuesta incluye:

```json
{
  "model": "tfidf-logreg-baseline-v1",
  "prediction": "Application",
  "confidence": 0.0,
  "probabilities": {
    "Application": 0.0,
    "Background": 0.0,
    "Comparison": 0.0,
    "Gap": 0.0,
    "Improvement": 0.0
  }
}
```

Los valores mostrados son únicamente representativos de la estructura de respuesta.

---

## Seguimiento de experimentos con MLflow

MLflow se utiliza para registrar y comparar los experimentos del proyecto.

La infraestructura local de MLflow y PostgreSQL se encuentra definida en:

```text
docker-compose.yml
```

y es independiente del Docker Compose utilizado por la aplicación:

```text
docker-compose.intencite.yml
```

Los experimentos registran, entre otros elementos:

- Parámetros.
- Métricas de validación.
- Artefactos.
- Matrices de confusión.
- Información del modelo.
- Adaptadores entrenados.

---

## Despliegue en AWS

El despliegue automatizado se ejecuta mediante:

```text
.github/workflows/deploy.yml
```

El workflow:

1. Configura las credenciales temporales de AWS Academy.
2. Obtiene la cuenta AWS activa.
3. Inicializa el backend remoto de Terraform.
4. Crea o reutiliza los repositorios ECR.
5. Construye las imágenes Docker.
6. Publica las imágenes en ECR.
7. Ejecuta Terraform.
8. Crea o actualiza ECS, Fargate, ALB, redes y logging.
9. Espera a que los servicios estén estables.
10. Publica la URL del Application Load Balancer.

La infraestructura puede eliminarse mediante:

```text
.github/workflows/destroy.yml
```

Las instrucciones completas de despliegue, credenciales de AWS Academy, verificación y solución de problemas se encuentran en el Manual de Instalación.

---

## Interfaz

La aplicación permite:

- Seleccionar el modelo de inferencia.
- Introducir un contexto académico.
- Ejecutar una clasificación.
- Consultar la categoría predicha.
- Consultar el nivel de confianza.
- Visualizar las probabilidades de las cinco categorías.
- Consultar estadísticas del corpus.

La interfaz y el manual completo pueden consultarse en:

https://jtorresor.github.io/citation-recommendation-nlp/

---

## Limitaciones

- El sistema fue desarrollado principalmente con textos académicos en inglés.
- La taxonomía final contiene cinco categorías.
- Un mismo contexto podría expresar más de una intención aunque IntenCite produzca una única clase.
- Los modelos pueden producir resultados diferentes para un mismo texto.
- El desempeño puede disminuir ante dominios o estilos distintos a los utilizados durante el entrenamiento.
- La confianza de una predicción no garantiza que la clasificación sea correcta.
- Qwen2.5 + LoRA requiere más recursos y tiempo de inferencia que el baseline.
- IntenCite es una herramienta de apoyo y no reemplaza la revisión humana.

---

## Equipo

Proyecto desarrollado por estudiantes de la **Maestría en Inteligencia Artificial de la Universidad de los Andes**.

La documentación del proyecto incluye el reporte de trabajo en equipo y la asignación de actividades realizadas durante el micro-proyecto.

---

## Referencia de MultiCite

Anne Lauscher, Brandon Ko, Bailey Kuehl, Sophie Johnson, Arman Cohan, David Jurgens y Kyle Lo.

**MultiCite: Modeling realistic citations requires moving beyond the single-sentence single-label setting.**

Proceedings of NAACL 2022.

Repositorio:

https://github.com/allenai/multicite

---

## Nota académica

Proyecto desarrollado con fines académicos como parte del curso **Proyecto de Desarrollo de Soluciones** de la **Maestría en Inteligencia Artificial de la Universidad de los Andes**.

MultiCite se utiliza de acuerdo con los términos de su licencia **CC BY-NC 2.0**.