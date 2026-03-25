FROM python:3.10-slim

# Install system dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

CMD ["uv", "run", "python", "main.py"]