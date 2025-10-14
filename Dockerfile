FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libgpiod3 \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=2.1.2
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-interaction

COPY . .

ENV MEASURE_INTERVAL_SECONDS=20 \
    DISPLAY_SWITCH_INTERVAL=10 \
    LOG_LVL=INFO

CMD ["poetry", "run", "python", "src/main.py"]