# ── STAGE 1: Build ──
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# Setup virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Install dependencies into virtualenv (AI requirements excluded)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── STAGE 2: Lightweight Production Runtime ──
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app

# Copy compiled packages from builder
COPY --from=builder /opt/venv /opt/venv
COPY . .

# Zoho AppSail default port
EXPOSE 9000

# Using absolute path for uvicorn to guarantee AppSail finds it
CMD ["/opt/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000", "--workers", "1"]

