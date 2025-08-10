FROM python:3.13.6-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.8.8 /uv /uvx /bin/

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vim

COPY ./uv.lock /app/

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
     uv sync --frozen --no-dev

COPY . /app

ENTRYPOINT ["uv", "run", "python", "/app/main.py"]
