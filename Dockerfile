# Multi-stage Build for Job Required Application

# --- Stage 1: Build Frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Production Python Backend ---
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies for SQLite FTS5
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies
COPY backend/pyproject.toml backend/requirements.txt* /app/backend/
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir fastapi uvicorn sqlalchemy pydantic httpx pyjwt bcrypt python-dotenv

# Copy backend application
COPY backend/ /app/backend/

# Copy built frontend assets to static distribution folder
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose server port
EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0

# Initialize database and start FastAPI server
CMD ["sh", "-c", "python -m app.database.init_db && python -m uvicorn app.api.main:app --host 0.0.0.0 --port $PORT"]
