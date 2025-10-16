# 🧠 Raspberry Pi Temperature & Humidity Monitor

This project collects temperature and humidity data inside my little garden greenhouse from multiple sensors connected to a Raspberry Pi 4 — including one **DHT22** and multiple **DS18B20** sensors.  
The application runs inside a lightweight **Docker container** built with **Python 3.13 slim**. Dependency management is done with **Poetry**.

All sensor readings are periodically collected, logged, and printed to the console.  
Each DS18B20 is uniquely identified by its 1-Wire address, allowing you to label them (e.g., *inside* / *outside*) without needing multiple GPIO pins.

---

## ✨ Features

- 📡 Reads temperature and humidity from a DHT11 sensor
- 🌡️ Supports multiple DS18B20 sensors on a single GPIO pin
- ⚙️ Configurable via environment variables
- 🐳 Dockerized with Poetry for reproducible builds
- 🔁 Automatically restarts and maintains GPIO access via `docker-compose`

---

## 🧩 Hardware Setup

- **Raspberry Pi** (any model with GPIO support, I use Pi 4 Model B)
- **1× DHT11** sensor
- **2× DS18B20** temperature sensors, water resistant
- **1× 10 kΩ pull-up resistor** between the DS18B20 data line and 3.3 V
- All DS18B20 sensors share:
  - the same GPIO data pin (default: GPIO17)
  - the same 3.3 V and GND connections