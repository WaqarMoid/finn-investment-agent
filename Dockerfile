# Multi-stage Dockerfile for FINN
# Stage 1: Build React Vite SPA
FROM node:20-slim AS frontend-builder
WORKDIR /app/web
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

# Stage 2: Python FastAPI Production Runtime
FROM python:3.12-slim-bookworm AS runner
WORKDIR /app

# Install Python requirements
COPY apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --no-compile -r requirements.txt

# Copy backend code
COPY apps/api/finn ./finn
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Copy built frontend assets from stage 1
COPY --from=frontend-builder /app/web/dist /app/web/dist

# Render overrides PORT. The default matches Render's documented web-service port
# and also makes the image runnable without platform-specific configuration.
RUN mkdir -p /tmp/finn-data
ENV DATA_DIR=/tmp/finn-data
ENV DATABASE_PATH=/tmp/finn-data/finn.db
ENV PORT=10000
ENV HOST=0.0.0.0

EXPOSE 10000

CMD ["sh", "-c", "python -m uvicorn finn.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
