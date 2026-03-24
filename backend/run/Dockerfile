FROM python:3.12-slim AS base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Moscow

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists \
    rm -f /var/lib/apt/lists/lock /var/cache/apt/archives/lock /var/lib/dpkg/lock-frontend && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ca-certificates libpq5 libstdc++6 curl && \
    rm -rf /var/lib/apt/lists/*

FROM base AS builder

RUN curl -LsSf https://astral.sh/uv/install.sh | \
    env UV_INSTALL_DIR=/usr/local/bin sh

WORKDIR /build

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project --no-editable --compile-bytecode --link-mode=copy

COPY src/app /build/src/app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --frozen --no-dev --no-editable --compile-bytecode --link-mode=copy

RUN sed -i -r "s#!/build/.venv/bin/python#! /usr/local/bin/python#g" .venv/bin/*
RUN mv .venv /opt/venv

FROM base AS runtime

LABEL org.opencontainers.image.title="itc2026-server" \
      org.opencontainers.image.description="REST API server for project" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.source="https://github.com/ParkieV/itc2026.git" \
      org.opencontainers.image.licenses="MIT"

RUN useradd -u 10001 -m appuser

COPY --from=builder /run/private_key.pem /run/private_key.pem
COPY --from=builder /run/public_key.pem /run/public_key.pem
COPY --from=builder /build/src/app /home/app
COPY --from=builder /opt/venv/bin /opt/venv/bin
COPY --from=builder /opt/venv/lib/python3.12/site-packages/ /opt/venv/lib

RUN rm -rf /opt/venv/lib/app

ENV PATH="/opt/venv/bin/:$PATH"
ENV PYTHONPATH="/opt/venv/lib/:/home/src/:/home/"

ARG GIT_COMMIT=dev
ARG IMAGE_TAG=dev

ENV GIT_COMMIT=$GIT_COMMIT
ENV IMAGE_TAG=$IMAGE_TAG

RUN touch /~build.rev.${GIT_COMMIT}.txt && touch /~build.tag.${IMAGE_TAG}.txt && \
    touch /~build.date.`date '+%F_%H:%M:%S'`.txt

RUN echo "Built rev: ${GIT_COMMIT}"

ENTRYPOINT ["python", "home/app/main.py"]
