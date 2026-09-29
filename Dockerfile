# WattGuard AI - unified production image
# Builds the React/Vite frontend, then serves it through FastAPI.

FROM node:20-alpine AS frontend-build

WORKDIR /build/web

COPY web/package*.json ./
RUN npm ci

COPY web/ ./
RUN npm run build


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1

WORKDIR /app

# Build tools are needed by a few scientific Python dependencies.
RUN apt-get update     && apt-get install -y --no-install-recommends build-essential gcc g++     && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt

# fastdtw is an older compiled dependency; installing its build prerequisites
# first makes cloud builds more reliable.
RUN python -m pip install --upgrade pip setuptools wheel     && python -m pip install "numpy>=1.26,<2.0" "Cython<3"     && python -m pip install --no-build-isolation fastdtw==0.3.4     && python -m pip install -r ./backend/requirements.txt

COPY backend ./backend
COPY --from=frontend-build /build/web/dist ./web/dist

WORKDIR /app/backend

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
