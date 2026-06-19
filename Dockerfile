FROM python:3.14-slim-bookworm AS builder

ENV HOME_DIR="/app" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR $HOME_DIR


RUN pip install uv
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-cache

FROM python:3.14-slim-bookworm

ENV HOME_DIR="/app" \
    APP_DIR="/app/src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

RUN groupadd -r fastapi && useradd -r -g fastapi fastapi

WORKDIR $HOME_DIR

COPY --from=builder $HOME_DIR/.venv $HOME_DIR/.venv
COPY --chown=fastapi:fastapi . .

USER fastapi

CMD ["uvicorn", "src.main:app", "--workers", "2", "--port", "8080", "--host", "0.0.0.0"]
