# ============================
# Stage 1: Builder
# ============================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# ============================
# Stage 2: Runtime
# ============================
FROM python:3.11-slim

WORKDIR /app

# Fix: Ensure cron can import modules
ENV PYTHONPATH="/app"

# Set timezone to UTC
ENV TZ=UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron tzdata && \
    ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

# Copy python packages from builder
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app files
COPY app/ /app/app/
COPY crypto_utils.py /app/
COPY student_private.pem /app/
COPY student_public.pem /app/
COPY instructor_public.pem /app/
COPY scripts/ /app/scripts/

# Copy cron job
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# Create volume directories
RUN mkdir -p /data /cron && chmod -R 755 /data /cron

# Configure cron permissions and register
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron

EXPOSE 8080

# NEW FIXED CMD — This is the correct one
CMD ["sh", "-c", "cron -f & uvicorn app.main:app --host 0.0.0.0 --port 8080"]
