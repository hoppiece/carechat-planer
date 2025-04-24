FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm AS runner
ENV PORT=8080
ENV READINESS_CHECK_PATH=/healthz
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8080
WORKDIR /app/src/planer_bot
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://0.0.0.0:8080/healthz || exit 1
ENTRYPOINT ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
