FROM python:3.12-bookworm AS base
WORKDIR /app
RUN \
  --mount=type=cache,target=/root/.cache/pip \
  pip install poetry==2.0.1
COPY README.md ./pyproject.toml ./poetry.lock* ./
RUN \
  --mount=type=cache,target=/root/.cache/pypoetry \
  poetry config virtualenvs.create false \
  && poetry install --no-root
COPY src/planer_bot src/planer_bot
RUN poetry install


FROM python:3.12-slim-bookworm AS runner
ENV PORT=8000 READINESS_CHECK_PATH=/healthz
RUN \
  apt-get update && apt-get install --no-install-recommends -y \
  curl \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
USER nobody
WORKDIR /app
COPY --from=base \
  --chown=user:nobody:nogroup \
  /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY src/planer_bot src/planer_bot
WORKDIR /app/src/planer_bot
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://0.0.0.0:8000/healthz || exit 1
ENTRYPOINT ["sh", "-c", "exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
