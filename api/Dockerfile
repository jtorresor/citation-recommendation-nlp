FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HF_HOME=/opt/huggingface

COPY requirements-api.txt .

RUN pip install --no-cache-dir \
    torch==2.14.0 \
    --index-url https://download.pytorch.org/whl/cpu
    
RUN pip install --no-cache-dir -r requirements-api.txt

# Download the Qwen base model into the Docker image.
# This prevents runtime downloads from Hugging Face.
RUN python - <<'PY'
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="Qwen/Qwen2.5-1.5B-Instruct"
)
PY

# Runtime must use only the model already packaged in the image.
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1

COPY api ./api
COPY src ./src
COPY models ./models

ENV PYTHONPATH=/app/src

EXPOSE 8001

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]