# ---------------------------------------------------------------------------
# Servidor de tracking de MLflow para desplegar en EC2
# Backend store: PostgreSQL | Artifact store: volumen local servido por proxy
# ---------------------------------------------------------------------------
FROM python:3.11-slim

# Manten esta version alineada con la que instalas en Colab.
# Cliente y servidor con versiones distintas => errores raros de API.
ARG MLFLOW_VERSION=3.16.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MLFLOW_HOME=/mlflow

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# mlflow[auth] trae Flask-WTF, necesario si activas basic-auth (MLFLOW_AUTH_ENABLED=true).
# psycopg2-binary para el backend PostgreSQL.
# boto3 solo se necesita si mueves los artefactos a S3 (ARTIFACTS_DESTINATION=s3://...).
RUN pip install --no-cache-dir \
        "mlflow[auth]==${MLFLOW_VERSION}" \
        "psycopg2-binary==2.9.10" \
        "boto3==1.35.99"

WORKDIR ${MLFLOW_HOME}
RUN mkdir -p ${MLFLOW_HOME}/artifacts ${MLFLOW_HOME}/auth

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8080

# /health es un endpoint nativo del servidor de MLflow.
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=5 \
    CMD curl -fsS http://127.0.0.1:8080/health || exit 1

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
