FROM python:3.11

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    gcc \
    g++ cmake python3-dev \
    && rm -rf /var/lib/apt/lists/*

# UPGRADE PIP + setuptools + wheel FIRST
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install deps with pip cache mount and override index-url for torch
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
      --index-url https://pypi.org/simple \
      --extra-index-url https://download.pytorch.org/whl/cpu \
      -r requirements.txt


# Copy code
COPY . .

RUN mkdir -p /app/chromadb_multi_tenant

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
