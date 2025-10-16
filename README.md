# 🧠 Raspberry Pi Temperature & Humidity Monitor

This project collects temperature and humidity data from multiple sensors connected to a Raspberry Pi — including one **DHT22** and one or more **DS18B20** sensors.  
The application runs inside a lightweight **Docker container** built with **Python 3.13 slim** and managed using **Poetry**.

All sensor readings are periodically collected, logged, and printed to the console.  
Each DS18B20 is uniquely identified by its 1-Wire address, allowing you to label them (e.g., *inside* / *outside*) without needing multiple GPIO pins.

---

## ✨ Features

- 📡 Reads temperature and humidity from a DHT sensor (DHT11 or DHT22)
- 🌡️ Supports multiple DS18B20 sensors on a single GPIO pin
- ⚙️ Configurable via environment variables (`DHT_PIN`, `DS18_PIN`, `INTERVAL`, etc.)
- 🐳 Dockerized with Poetry for reproducible builds
- 🔁 Automatically restarts and maintains GPIO access via `docker-compose`

---

## 🧩 Hardware Setup

- **Raspberry Pi** (any model with GPIO support)
- **1× DHT11 or DHT22** sensor
- **2× DS18B20** temperature sensors
- **1× 10 kΩ pull-up resistor** between the DS18B20 data line and 3.3 V
- All DS18B20 sensors share:
  - the same GPIO data pin (default: GPIO17)
  - the same 3.3 V and GND connections