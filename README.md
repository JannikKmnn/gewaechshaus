# 🧠 Raspberry Pi Temperature & Humidity Monitor

This smart home automation project represents the codebase to collect physical data inside my little garden greenhouse from multiple sensors connected to a Raspberry Pi 4 — including temperature, humidity and soil moisture.  
The application runs inside a lightweight **Docker container** and can be reproduced by following the setup as described below. Dependency management is done with **Poetry**.

All sensor readings are periodically collected, logged, and displayed via a 16x2 lcd display for arduino or raspberry pi.  
Each DS18B20 temperature sensor is uniquely identified by its 1-Wire address, allowing you to label them (e.g., *inside* / *outside*) without needing multiple GPIO pins.

Currently, this MVP includes mainly displaying sensor values on the display to indicate if certain actions on the greenhouse are required (watering, ventilation). The idea is to build a fully automated system to minimize manual work in the greenhouse as well as implementing a full-on web application from scratch to monitor and control every sensor remotely.
---

## ✨ Features

- 📡 Reads temperature and humidity from a DHT11 sensor
- 🌡️ Supports multiple DS18B20 sensors on a single GPIO pin
- 📺 Displays the sensor readings on a 16x2 lcd display 
- ⚙️ Configurable via environment variables
- 🐳 Dockerized with Poetry for reproducible builds
- 🔁 Automatically restarts and maintains GPIO access via `docker-compose`

---

## 🧩 Hardware Setup

- **Raspberry Pi** (any model with GPIO support, I use Pi 4 Model B) with ubuntu 24.04 lts
- **1× DHT11** sensor
- **2× DS18B20** temperature sensors, water resistant
- **1× 10 kΩ pull-up resistor** between the DS18B20 data line and 3.3 V
- All DS18B20 sensors share:
  - the same GPIO data pin (default: GPIO17)
  - the same 3.3 V and GND connections