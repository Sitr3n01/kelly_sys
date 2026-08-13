# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Seleciona o conjunto de dependências: 'production' (default) ou 'development'.
# O docker-compose.yml de dev passa REQUIREMENTS=development.
ARG REQUIREMENTS=production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ca-certificates: TLS de saída (Sentry/SMTP). psycopg[binary] já embute libpq.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências primeiro para aproveitar cache de camada.
COPY requirements/ requirements/
RUN pip install -r requirements/${REQUIREMENTS}.txt

# Usuário não-root.
RUN useradd -m -u 1000 appuser

# Código da aplicação. O .dockerignore garante que .env/.venv/.git NUNCA entrem na imagem.
COPY --chown=appuser:appuser . .

# Compila estáticos (WhiteNoise CompressedManifest). SECRET_KEY dummy só para esta etapa,
# não é persistido como env da imagem e não é um segredo real.
RUN SECRET_KEY=build-only-not-a-secret \
    DB_NAME=build_only \
    DB_USER=build_only \
    DB_PASSWORD=build_only \
    DB_HOST=localhost \
    DB_PORT=5432 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    python manage.py collectstatic --noinput

USER appuser

EXPOSE 8000

# Liveness probe. /healthz/ é isento de redirect HTTPS (ver config/settings/production.py).
HEALTHCHECK --interval=60s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz/', timeout=4).status == 200 else 1)"

# Espelha o `command` de docker/docker-compose.prod.yml — a justificativa de cada flag
# está nos comentários de lá. --preload compartilha o grafo de imports (Django+Wagtail)
# entre os workers via copy-on-write; --max-requests/-jitter reciclam o worker e
# devolvem memória ao SO.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--preload", "--max-requests", "800", "--max-requests-jitter", "200", "--timeout", "60", "--graceful-timeout", "30", "--error-logfile", "-"]
