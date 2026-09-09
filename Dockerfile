FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей для psycopg2, curl и корневых сертификатов
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    ca-certificates \
    curl \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Создание непривилегированного пользователя appuser для безопасности
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Настройка прав доступа
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Встроенный healthcheck контейнера
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/healthz || exit 1

# Запуск приложения через Uvicorn
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
