FROM python:3.12-slim

WORKDIR /app

COPY requirements-api.txt .

RUN pip install --no-cache-dir -r requirements-api.txt

COPY api ./api
COPY src ./src
COPY models ./models

ENV PYTHONPATH=/app/src

EXPOSE 8001

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]