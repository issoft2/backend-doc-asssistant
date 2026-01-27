FROM python:3.11-slim

WORKDIR /app

ENV PIP_ONLY_BINARY=:all:

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
      --index-url https://pypi.org/simple \
      --extra-index-url https://download.pytorch.org/whl/cpu \
      -r requirements.txt

COPY . .

RUN mkdir -p /app/chromadb_multi_tenant

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
