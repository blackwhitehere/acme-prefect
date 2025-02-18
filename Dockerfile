# Based on https://github.com/astral-sh/uv-docker-example
# Using multi-stage image builds to create a final image without uv and any build tools.

# Use a Python image with uv pre-installed
FROM python:3.12 AS builder

# Install anything needed to build the project
RUN pip install uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Then, use a final image without uv
FROM python:3.12
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11`
# will fail.

# Copy the application from the builder
# TODO: prefect expects to see `src` dir in the root directory based on the deployment e.g. `python src/acme_prefect/deploy/fetch_yahoo_data_ecs_fargate.py`
# check if there is a way to change how it looks up path to the script
COPY --from=builder --chown=app:app /app /

# Place executables in the environment at the front of the path
ENV PATH="/.venv/bin:$PATH"

# Run the example command
CMD ["ap", "--help"]