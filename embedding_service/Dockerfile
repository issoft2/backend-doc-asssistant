FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
 
# 2) Upgrade/pin pip (optional, cached with base image)
RUN pip install --no-cache-dir --upgrade pip
 
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt \
    --trusted-host download.pytorch.org \
    --disable-pip-version-check    

COPY main.py .

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
