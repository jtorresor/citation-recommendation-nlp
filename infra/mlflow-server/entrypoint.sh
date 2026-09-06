#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# Variables de entorno esperadas (ver docker-compose.yml / .env)
# ---------------------------------------------------------------------------
BACKEND_STORE_URI="${BACKEND_STORE_URI:?Falta BACKEND_STORE_URI}"
ARTIFACTS_DESTINATION="${ARTIFACTS_DESTINATION:-/mlflow/artifacts}"
MLFLOW_PORT="${MLFLOW_PORT:-8080}"
MLFLOW_WORKERS="${MLFLOW_WORKERS:-2}"
# Host publico (IP elastica o DNS) con el que los clientes llegan al servidor.
MLFLOW_PUBLIC_HOST="${MLFLOW_PUBLIC_HOST:-}"
MLFLOW_AUTH_ENABLED="${MLFLOW_AUTH_ENABLED:-false}"

mkdir -p "${ARTIFACTS_DESTINATION}" /mlflow/auth

# ---------------------------------------------------------------------------
# 1. Esperar a PostgreSQL y aplicar migraciones del esquema
#    (idempotente: en una BD vacia crea el esquema, en una existente lo migra)
# ---------------------------------------------------------------------------
echo "[entrypoint] Esperando al backend store..."
for i in $(seq 1 30); do
    if python -c "
import sys, sqlalchemy
try:
    sqlalchemy.create_engine('${BACKEND_STORE_URI}').connect().close()
except Exception as exc:
    print(exc, file=sys.stderr); sys.exit(1)
" 2>/dev/null; then
        echo "[entrypoint] Backend store disponible (intento ${i})."
        break
    fi
    sleep 2
done

echo "[entrypoint] Ejecutando 'mlflow db upgrade'..."
mlflow db upgrade "${BACKEND_STORE_URI}" \
    || echo "[entrypoint] AVISO: db upgrade fallo; el servidor intentara inicializar el store al arrancar."

# ---------------------------------------------------------------------------
# 2. Validacion del header Host (MLflow >= 3.x)
#    Por defecto MLflow SOLO acepta localhost e IPs privadas. Al exponer el
#    servidor en la IP publica de EC2, Colab manda "Host: <ip>:8080" y el
#    servidor devuelve 403 (Invalid Host header) si esa IP no esta en la lista.
# ---------------------------------------------------------------------------
ALLOWED_HOSTS="localhost,localhost:*,127.0.0.1,127.0.0.1:*"
if [ -n "${MLFLOW_PUBLIC_HOST}" ]; then
    ALLOWED_HOSTS="${ALLOWED_HOSTS},${MLFLOW_PUBLIC_HOST},${MLFLOW_PUBLIC_HOST}:*"
fi
# Permite sobrescribir por completo la lista si lo necesitas (p. ej. un dominio).
ALLOWED_HOSTS="${MLFLOW_ALLOWED_HOSTS_OVERRIDE:-${ALLOWED_HOSTS}}"

# ---------------------------------------------------------------------------
# 2b. Origenes CORS permitidos
#     El navegador manda header 'Origin' tambien en peticiones POST del MISMO
#     origen. MLflow bloquea con 403 "Cross-origin request blocked" cualquier
#     POST con Origin que no sea localhost, salvo que se declare aqui. Sin esto
#     la UI servida en una IP publica no puede buscar, borrar ni renombrar runs.
#     No afecta a los clientes Python (Colab): no envian header Origin.
#     Ojo: el puerto del Origin es el PUBLICADO en el host, no el interno.
# ---------------------------------------------------------------------------
MLFLOW_PUBLIC_PORT="${MLFLOW_PUBLIC_PORT:-${MLFLOW_PORT}}"
CORS_ORIGINS="http://localhost:${MLFLOW_PUBLIC_PORT},http://127.0.0.1:${MLFLOW_PUBLIC_PORT}"
if [ -n "${MLFLOW_PUBLIC_HOST}" ]; then
    CORS_ORIGINS="${CORS_ORIGINS},http://${MLFLOW_PUBLIC_HOST}:${MLFLOW_PUBLIC_PORT},http://${MLFLOW_PUBLIC_HOST}"
fi
CORS_ORIGINS="${MLFLOW_CORS_ORIGINS_OVERRIDE:-${CORS_ORIGINS}}"

SERVER_ARGS=(
    server
    --host 0.0.0.0
    --port "${MLFLOW_PORT}"
    --workers "${MLFLOW_WORKERS}"
    --backend-store-uri "${BACKEND_STORE_URI}"
    --serve-artifacts
    --artifacts-destination "${ARTIFACTS_DESTINATION}"
    --default-artifact-root "mlflow-artifacts:/"
    --allowed-hosts "${ALLOWED_HOSTS}"
    --cors-allowed-origins "${CORS_ORIGINS}"
)

# ---------------------------------------------------------------------------
# 3. Autenticacion basica opcional
#    El puerto tiene que estar abierto a internet para que Colab entre, asi que
#    conviene activarla. Los clientes usan MLFLOW_TRACKING_USERNAME/PASSWORD.
# ---------------------------------------------------------------------------
if [ "$(echo "${MLFLOW_AUTH_ENABLED}" | tr '[:upper:]' '[:lower:]')" = "true" ]; then
    AUTH_INI="/mlflow/auth/basic_auth.ini"
    cat > "${AUTH_INI}" <<EOF
[mlflow]
default_permission = READ
database_uri = sqlite:////mlflow/auth/basic_auth.db
admin_username = ${MLFLOW_AUTH_USERNAME:-admin}
admin_password = ${MLFLOW_AUTH_PASSWORD:?Falta MLFLOW_AUTH_PASSWORD con MLFLOW_AUTH_ENABLED=true}
authorization_function = mlflow.server.auth:authenticate_request_basic_auth
EOF
    chmod 600 "${AUTH_INI}"
    export MLFLOW_AUTH_CONFIG_PATH="${AUTH_INI}"
    SERVER_ARGS+=(--app-name basic-auth)
    echo "[entrypoint] Autenticacion basica ACTIVADA (usuario: ${MLFLOW_AUTH_USERNAME:-admin})."
else
    echo "[entrypoint] Autenticacion basica DESACTIVADA. Restringe el Security Group."
fi

echo "[entrypoint] allowed-hosts = ${ALLOWED_HOSTS}"
echo "[entrypoint] cors-origins  = ${CORS_ORIGINS}"
echo "[entrypoint] artifacts     = ${ARTIFACTS_DESTINATION}"
echo "[entrypoint] Arrancando MLflow en 0.0.0.0:${MLFLOW_PORT}"

exec mlflow "${SERVER_ARGS[@]}"
