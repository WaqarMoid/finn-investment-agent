# Multi-stage Dockerfile for FINN
# Stage 1: Build React Vite SPA
FROM node:20-slim AS frontend-builder
WORKDIR /app/web
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

# Stage 2: Python FastAPI Production Runtime
FROM python:3.12-slim AS runner
WORKDIR /app

# System dependencies for SQLite and PDF handling
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY apps/api/finn ./finn
ENV PYTHONPATH=/app

# Copy built frontend assets from stage 1
COPY --from=frontend-builder /app/web/dist /app/web/dist

# Mountable persistent storage directory
RUN mkdir -p /data
ENV DATA_DIR=/data
ENV DATABASE_PATH=/data/finn.db
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health/live || exit 1

CMD ["sh", "-c", "python -m uvicorn finn.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
