# Manual de Instalación — IntenCite

## 1. Introducción

Este manual describe los procedimientos necesarios para instalar, ejecutar, desplegar y detener IntenCite.

La solución está compuesta por dos servicios principales:

- **IntenCite App:** interfaz web estática servida mediante Nginx.
- **IntenCite API:** API desarrollada con FastAPI que carga el modelo supervisado y sirve las predicciones.

El modelo actualmente desplegado es:

```text
tfidf_logreg_baseline_v1.joblib
```

IntenCite puede ejecutarse de dos formas:

1. Localmente mediante Docker Compose.
2. En AWS mediante GitHub Actions, Terraform, ECR, ECS/Fargate y un Application Load Balancer.

## 2. Arquitectura de la solución

En el despliegue local, el navegador accede directamente a los puertos publicados por Docker:

- Tablero web: puerto `8080`.
- API: puerto `8001`.

En AWS, el usuario accede a un Application Load Balancer. El balanceador utiliza reglas de enrutamiento para enviar cada solicitud al servicio correspondiente:

| Ruta | Destino |
|---|---|
| `/` | Interfaz web en Nginx |
| `/api/*` | API de inferencia en FastAPI |
| `/health` | Verificación de salud de la API |

Los contenedores se ejecutan mediante Amazon ECS utilizando AWS Fargate. Las imágenes se almacenan en repositorios privados de Amazon ECR.

![Arquitectura de IntenCite en AWS](diagrams/02-arquitectura-aws.svg)

## 3. Estructura relevante del repositorio

```text
citation-recommendation-nlp/
├── .github/
│   └── workflows/
│       ├── deploy.yml
│       └── destroy.yml
├── api/
│   ├── Dockerfile
│   ├── main.py
│   ├── routes.py
│   └── schemas.py
├── app/
│   ├── Dockerfile
│   ├── index.html
│   ├── nginx.conf
│   └── static/
├── infra/
│   ├── intencite/
│   │   ├── alb.tf
│   │   ├── ecr.tf
│   │   ├── ecs.tf
│   │   ├── network.tf
│   │   ├── outputs.tf
│   │   ├── providers.tf
│   │   └── variables.tf
│   └── mlflow-server/
├── models/
│   └── tfidf_logreg_baseline_v1.joblib
├── src/
│   └── intencite/
├── docker-compose.intencite.yml
├── docker-compose.yml
├── requirements-api.txt
└── README.md
```

Los dos archivos de Docker Compose cumplen funciones diferentes:

- `docker-compose.intencite.yml` ejecuta el tablero y la API de IntenCite.
- `docker-compose.yml` ejecuta la infraestructura separada de MLflow y PostgreSQL.

Para utilizar el producto localmente debe emplearse `docker-compose.intencite.yml`.

## 4. Requisitos previos

### 4.1 Para la ejecución local

Se requiere:

- Git.
- Docker Desktop o Docker Engine.
- Docker Compose v2.
- Un navegador web.
- Al menos 2 GB de memoria disponible para Docker.

Verifique las instalaciones:

```bash
git --version
docker --version
docker compose version
```

Docker debe estar iniciado antes de construir los contenedores.

### 4.2 Para el despliegue en AWS

Se requiere:

- Acceso al repositorio en GitHub.
- Acceso a un laboratorio de AWS Academy.
- Permiso para configurar GitHub Actions Secrets.
- Una sesión activa de AWS Academy.
- Credenciales temporales vigentes.
- Permisos disponibles a través del rol `LabRole`.

No es necesario instalar Terraform ni AWS CLI en el computador del usuario para utilizar el despliegue automatizado, porque GitHub Actions ejecuta estas herramientas dentro del runner.

## 5. Instalación y ejecución local

### 5.1 Clonar el repositorio

```bash
git clone https://github.com/jtorresor/citation-recommendation-nlp.git
cd citation-recommendation-nlp
```

Si ya tiene el repositorio, actualice la rama correspondiente:

```bash
git pull
```

### 5.2 Verificar los archivos requeridos

Antes de construir la solución, compruebe que existen:

```bash
test -f api/Dockerfile
test -f app/Dockerfile
test -f docker-compose.intencite.yml
test -f models/tfidf_logreg_baseline_v1.joblib
```

También puede verificar el modelo mediante:

```bash
ls -lh models/
```

La API no podrá iniciar correctamente si el artefacto del modelo no está disponible.

### 5.3 Construir las imágenes

Desde la raíz del repositorio, ejecute:

```bash
docker compose -f docker-compose.intencite.yml build
```

Este comando construye:

- `intencite-api`, utilizando `api/Dockerfile`.
- `intencite-app`, utilizando `app/Dockerfile`.

Durante la construcción de la API se instalan las dependencias de `requirements-api.txt` y se copian el código, el módulo de predicción y el modelo entrenado.

### 5.4 Iniciar la aplicación

```bash
docker compose -f docker-compose.intencite.yml up -d
```

La opción `-d` permite ejecutar los contenedores en segundo plano.

### 5.5 Verificar los contenedores

```bash
docker compose -f docker-compose.intencite.yml ps
```

También puede utilizar:

```bash
docker ps
```

Los contenedores esperados son:

```text
intencite-app
intencite-api
```

### 5.6 Consultar los registros

Para consultar los registros de ambos servicios:

```bash
docker compose -f docker-compose.intencite.yml logs
```

Para seguirlos en tiempo real:

```bash
docker compose -f docker-compose.intencite.yml logs -f
```

Para consultar únicamente la API:

```bash
docker compose -f docker-compose.intencite.yml logs -f api
```

Para consultar únicamente el tablero:

```bash
docker compose -f docker-compose.intencite.yml logs -f app
```

### 5.7 Acceder a la aplicación

Abra el tablero en:

```text
http://localhost:8080
```

La API se encuentra disponible en:

```text
http://localhost:8001
```

La documentación interactiva de FastAPI puede abrirse en:

```text
http://localhost:8001/docs
```

### 5.8 Verificar la API

Compruebe el endpoint de salud:

```bash
curl http://localhost:8001/health
```

Respuesta esperada:

```json
{
  "status": "ok"
}
```

Consulte los modelos disponibles:

```bash
curl http://localhost:8001/api/v1/models
```

Respuesta esperada:

```json
{
  "models": [
    {
      "id": "tfidf-logreg-baseline-v1",
      "name": "TF-IDF + Logistic Regression"
    }
  ]
}
```

Realice una predicción de prueba:

```bash
curl -X POST "http://localhost:8001/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "We use the parser introduced by Smith et al. (2020) to preprocess all documents in our corpus.",
    "model": "tfidf-logreg-baseline-v1"
  }'
```

La respuesta debe incluir:

- Modelo utilizado.
- Categoría predicha.
- Confianza.
- Probabilidad de cada categoría.

### 5.9 Detener la aplicación

Para detener y eliminar los contenedores:

```bash
docker compose -f docker-compose.intencite.yml down
```

Este comando no elimina las imágenes construidas.

Para volver a iniciar la solución:

```bash
docker compose -f docker-compose.intencite.yml up -d
```

### 5.10 Reconstruir después de modificar el código

```bash
docker compose -f docker-compose.intencite.yml up -d --build
```

Si se sospecha que Docker está utilizando una capa almacenada en caché:

```bash
docker compose -f docker-compose.intencite.yml build --no-cache
docker compose -f docker-compose.intencite.yml up -d
```

## 6. Despliegue automatizado en AWS

El despliegue en la nube se realiza mediante:

```text
.github/workflows/deploy.yml
```

La eliminación de la infraestructura se realiza mediante:

```text
.github/workflows/destroy.yml
```

Ambos workflows utilizan credenciales temporales de AWS Academy almacenadas como GitHub Actions Secrets.

![Flujo automatizado de despliegue y destrucción](diagrams/01-flujo-github-actions.svg)

## 7. Configuración de AWS Academy

### 7.1 Iniciar el laboratorio

1. Ingrese a AWS Academy.
2. Abra el laboratorio correspondiente.
3. Presione **Start Lab**.
4. Espere hasta que la sesión se encuentre activa.
5. Abra la sección que muestra las credenciales para AWS CLI.
6. Copie los siguientes valores:

```text
aws_access_key_id
aws_secret_access_key
aws_session_token
```

Estas credenciales son temporales.

> Nunca copie estas credenciales dentro de archivos del repositorio, archivos Terraform, Dockerfiles, commits, documentación pública o variables visibles en el código.

### 7.2 Crear los GitHub Actions Secrets

En GitHub:

1. Abra el repositorio.
2. Ingrese a **Settings**.
3. Abra **Secrets and variables**.
4. Seleccione **Actions**.
5. Presione **New repository secret**.
6. Cree los siguientes tres secrets:

| GitHub Secret | Valor obtenido de AWS Academy |
|---|---|
| `AWS_ACCESS_KEY_ID` | `aws_access_key_id` |
| `AWS_SECRET_ACCESS_KEY` | `aws_secret_access_key` |
| `AWS_SESSION_TOKEN` | `aws_session_token` |

Los nombres deben escribirse exactamente como aparecen en la tabla.

No se requiere guardar manualmente el ID de la cuenta de AWS. El workflow lo obtiene durante la ejecución mediante:

```bash
aws sts get-caller-identity --query Account --output text
```

La región configurada para el proyecto es:

```text
us-east-1
```

### 7.3 Renovar las credenciales

Las credenciales de AWS Academy dejan de funcionar cuando la sesión expira o cuando el laboratorio genera una sesión nueva.

Antes de ejecutar nuevamente `Deploy IntenCite` o `Destroy IntenCite`:

1. Confirme que el laboratorio esté iniciado.
2. Obtenga las credenciales actuales.
3. Actualice los tres GitHub Secrets.
4. Ejecute el workflow.

No es necesario crear nuevos secrets. Deben actualizarse los valores de los tres secrets existentes.

## 8. Ejecutar el despliegue desde GitHub Actions

### 8.1 Iniciar el workflow

1. Abra la pestaña **Actions** del repositorio.
2. Seleccione el workflow de despliegue definido en `deploy.yml`.
3. Presione **Run workflow**.
4. Seleccione la rama que contiene la versión que desea desplegar.
5. Confirme la ejecución.
6. Abra la ejecución para observar cada etapa.

### 8.2 Proceso realizado por el workflow

El proceso automatizado ejecuta conceptualmente las siguientes etapas:

1. Descarga el contenido del repositorio.
2. Configura las credenciales temporales de AWS.
3. Verifica la identidad activa mediante AWS STS.
4. Obtiene dinámicamente el ID de la cuenta.
5. Construye el nombre del bucket de estado:

```text
intencite-tfstate-<AWS_ACCOUNT_ID>
```

6. Crea o reutiliza el bucket temporal de estado de Terraform.
7. Inicializa Terraform con el backend remoto en S3.
8. Crea los repositorios de Amazon ECR.
9. Inicia sesión en ECR.
10. Construye las imágenes Docker de la API y del tablero.
11. Publica las imágenes en ECR.
12. Ejecuta `terraform apply`.
13. Crea o actualiza la infraestructura de IntenCite.
14. Obtiene la dirección pública del Application Load Balancer.
15. Muestra los outputs del despliegue.

El backend de Terraform utiliza:

```text
Bucket: intencite-tfstate-<AWS_ACCOUNT_ID>
Key:    intencite/terraform.tfstate
Region: us-east-1
```

La inicialización corresponde conceptualmente a:

```bash
terraform init \
  -backend-config="bucket=${STATE_BUCKET}" \
  -backend-config="key=intencite/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="use_lockfile=true"
```

El bucket se genera a partir de la cuenta activa para que el despliegue pueda realizarse utilizando las credenciales de AWS Academy de cualquier integrante, profesor o monitor autorizado.

## 9. Recursos creados en AWS

Terraform crea o administra los siguientes componentes:

### 9.1 Amazon ECR

Se crean dos repositorios de imágenes:

```text
intencite-api
intencite-app
```

El primero almacena la imagen de FastAPI y el segundo la imagen del tablero servido mediante Nginx.

### 9.2 Amazon ECS

Se crea el clúster:

```text
intencite-cluster
```

En el clúster se ejecutan dos servicios:

```text
intencite-api
intencite-app
```

Cada servicio utiliza una definición de tarea compatible con Fargate y el modo de red `awsvpc`.

La configuración actual utiliza por tarea:

```text
CPU:     256
Memoria: 512 MiB
```

### 9.3 Application Load Balancer

El Application Load Balancer recibe el tráfico HTTP y lo dirige a los target groups correspondientes.

Las reglas principales son:

```text
/               → servicio intencite-app
/api/*          → servicio intencite-api
/health         → servicio intencite-api
```

### 9.4 Red

El despliegue utiliza la VPC disponible en la cuenta de AWS Academy y las subredes seleccionadas por Terraform.

Los grupos de seguridad permiten el tráfico necesario hacia:

- Puerto `80` del tablero.
- Puerto `8001` de la API.
- Puerto `80` del Application Load Balancer para acceso desde el navegador.

### 9.5 IAM

Las tareas ECS utilizan el rol disponible en AWS Academy:

```text
LabRole
```

Este rol permite que ECS descargue las imágenes desde ECR y escriba registros en CloudWatch.

### 9.6 CloudWatch Logs

Los registros de los contenedores se envían a Amazon CloudWatch, desde donde pueden revisarse errores de inicialización, carga del modelo y ejecución de la API.

### 9.7 Amazon S3

El workflow crea un bucket temporal para conservar el estado remoto de Terraform:

```text
intencite-tfstate-<AWS_ACCOUNT_ID>
```

Este estado permite que el workflow de destrucción identifique los recursos creados previamente.

## 10. Verificación del despliegue

### 10.1 Obtener la dirección

Al terminar el workflow, consulte los outputs de Terraform o el resumen de la ejecución.

La dirección tendrá una estructura similar a:

```text
http://<nombre-del-alb>.us-east-1.elb.amazonaws.com
```

La dirección no es permanente, porque el DNS puede cambiar al destruir y reconstruir la infraestructura.

La siguiente imagen muestra una ejecución exitosa del workflow y la URL generada para acceder a la aplicación:

![Despliegue exitoso mediante GitHub Actions](assets/installation/01-deploy-github-actions.png)

La dirección se genera durante la ejecución y puede cambiar cuando la infraestructura se destruye y se vuelve a crear.

### 10.2 Abrir el tablero

Abra en un navegador:

```text
http://<DNS_DEL_ALB>
```

### 10.3 Verificar la API

```bash
curl "http://<DNS_DEL_ALB>/health"
```

Respuesta esperada:

```json
{
  "status": "ok"
}
```

Consulte los modelos:

```bash
curl "http://<DNS_DEL_ALB>/api/v1/models"
```

También puede realizar una predicción:

```bash
curl -X POST "http://<DNS_DEL_ALB>/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "We use the parser introduced by Smith et al. (2020) to preprocess all documents in our corpus.",
    "model": "tfidf-logreg-baseline-v1"
  }'
```

Después de crear los servicios, ECS puede tardar algunos minutos en iniciar las tareas y registrarlas como saludables en el balanceador.

## 11. Actualizar una versión desplegada

Cuando se modifica la API, el tablero, el modelo o la infraestructura:

1. Guarde los cambios.
2. Cree un commit.
3. Envíe la rama a GitHub.
4. Actualice los secrets si la sesión de AWS Academy cambió.
5. Ejecute nuevamente el workflow de despliegue.

Ejemplo:

```bash
git add .
git commit -m "feat: update IntenCite application"
git push
```

El workflow construirá imágenes nuevas y volverá a aplicar la configuración de Terraform.

## 12. Destruir la infraestructura

Para evitar el consumo innecesario de recursos de AWS Academy, la infraestructura debe destruirse cuando no esté siendo utilizada.

### 12.1 Ejecutar el workflow de destrucción

1. Confirme que la sesión de AWS Academy esté activa.
2. Actualice los tres GitHub Secrets si las credenciales cambiaron.
3. Abra **Actions**.
4. Seleccione el workflow definido en `destroy.yml`.
5. Presione **Run workflow**.
6. Seleccione la rama correspondiente.
7. Confirme la ejecución.
8. Espere hasta que todos los pasos finalicen correctamente.

### 12.2 Proceso de destrucción

El workflow:

1. Configura las credenciales temporales.
2. Obtiene el ID de la cuenta mediante AWS STS.
3. Reconstruye el nombre del bucket de estado.
4. Inicializa Terraform utilizando el estado remoto existente.
5. Ejecuta `terraform destroy`.
6. Elimina los recursos administrados por Terraform.
7. Vacía el bucket temporal de estado.
8. Elimina el bucket `intencite-tfstate-<AWS_ACCOUNT_ID>`.

El objetivo es dejar limpia la cuenta utilizada para el despliegue.

> No elimine manualmente el bucket de estado antes de ejecutar `destroy.yml`. Terraform necesita ese estado para identificar correctamente los recursos que debe destruir.

## 13. MLflow

El archivo ubicado en la raíz:

```text
docker-compose.yml
```

corresponde a la infraestructura separada de MLflow y PostgreSQL utilizada para el seguimiento de experimentos.

Esta infraestructura no es necesaria para ejecutar el tablero ni para realizar predicciones con el modelo ya empaquetado.

Para ejecutar MLflow se requiere crear `.env` a partir de:

```text
.env.example
```

La ejecución se realiza mediante:

```bash
docker compose up -d
```

Esta operación no debe confundirse con la ejecución de IntenCite:

```bash
docker compose -f docker-compose.intencite.yml up -d
```

## 14. Solución de problemas

### Docker no está disponible

Compruebe que Docker Desktop o Docker Engine esté iniciado:

```bash
docker info
```

### El puerto ya está ocupado

Compruebe qué proceso utiliza los puertos:

```bash
sudo lsof -i :8080
sudo lsof -i :8001
```

Detenga el proceso o modifique temporalmente el puerto publicado en `docker-compose.intencite.yml`.

### La API no encuentra el modelo

Verifique:

```bash
ls -lh models/tfidf_logreg_baseline_v1.joblib
```

Después reconstruya la API:

```bash
docker compose -f docker-compose.intencite.yml build --no-cache api
docker compose -f docker-compose.intencite.yml up -d
```

### La aplicación local no responde

Revise:

```bash
docker compose -f docker-compose.intencite.yml ps
docker compose -f docker-compose.intencite.yml logs
```

### GitHub Actions no puede autenticarse en AWS

Las credenciales de AWS Academy probablemente expiraron o fueron copiadas desde una sesión anterior.

1. Inicie nuevamente el laboratorio.
2. Obtenga las credenciales actuales.
3. Actualice `AWS_ACCESS_KEY_ID`.
4. Actualice `AWS_SECRET_ACCESS_KEY`.
5. Actualice `AWS_SESSION_TOKEN`.
6. Vuelva a ejecutar el workflow.

### Error `ExpiredToken`

Actualice los tres secrets con credenciales de la sesión activa de AWS Academy.

### Error `AccessDenied`

Compruebe:

- Que el laboratorio esté iniciado.
- Que las tres credenciales pertenezcan a la misma sesión.
- Que el workflow utilice `us-east-1`.
- Que el rol `LabRole` esté disponible.
- Que el servicio solicitado esté permitido por AWS Academy.

### La URL del ALB devuelve `503 Service Temporarily Unavailable`

Un `503` indica que el ALB todavía no tiene targets saludables.

Revise:

1. El estado de los servicios en ECS.
2. Las tareas detenidas.
3. Los health checks de los target groups.
4. Los registros de CloudWatch.
5. Que la API escuche en el puerto `8001`.
6. Que el tablero escuche en el puerto `80`.
7. Que la imagen esperada exista en ECR.

Después de desplegar, espere algunos minutos antes de repetir la prueba.

### El bucket de estado ya existe

El workflow está diseñado para crear o reutilizar:

```text
intencite-tfstate-<AWS_ACCOUNT_ID>
```

Si el bucket pertenece a la misma cuenta y contiene el estado del proyecto, no debe eliminarse manualmente antes de ejecutar la destrucción.

### El workflow de destrucción no encuentra el estado

Compruebe que:

- Se estén utilizando credenciales de la misma cuenta usada durante el despliegue.
- El bucket de estado todavía exista.
- La clave sea `intencite/terraform.tfstate`.
- La región sea `us-east-1`.

## 15. Validación final

La instalación puede considerarse correcta cuando se cumplen estas condiciones:

- Los contenedores locales aparecen activos.
- El tablero abre correctamente.
- `/health` devuelve `{"status":"ok"}`.
- `/api/v1/models` muestra el modelo disponible.
- `/api/v1/predict` devuelve una predicción.
- El workflow de despliegue termina correctamente.
- ECS mantiene activas las tareas del tablero y la API.
- Los target groups aparecen saludables.
- El DNS del ALB permite usar el tablero.
- El workflow de destrucción elimina los recursos creados.