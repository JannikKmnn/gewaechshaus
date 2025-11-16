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

ENV MEASURE_INTERVAL_SECONDS=60 \
    LOG_LVL=INFO \
    TEMPERATURE_OUTSIDE_SENSOR_ID=000000b47976 \
    TEMPERATURE_INSIDE_SENSOR_ID=000000b998e3 \
    SOIL_MOISTURE_SENSOR_CHANNEL_BACK=23 \
    SOIL_MOISTURE_SENSOR_CHANNEL_FRONT=24 \
    LCD_COLUMNS=16 \
    LCD_ROWS=2

CMD ["poetry", "run", "python", "-m", "src.services.sensor_reader.main"]