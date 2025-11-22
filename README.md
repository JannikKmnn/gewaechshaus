# 🧠🌱 Raspberry Pi Greenhouse Automations

This smart home automation project represents the codebase to collect physical data inside my little garden greenhouse from multiple sensors connected to a Raspberry Pi 4 — including temperature, humidity, air pressure and soil moisture.

All sensor readings are periodically collected, logged, displayed inside a little self-made box for the raspi as well as published via MQTT and stored inside an InfluxDB cloud instance. This allows both real time and historical data analysis on the measurements:

![InfluxDB dashboard (this one from winter time... 🧊)](images/influxdb_dashboard.png?raw=true "Sensor Monitoring")

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
- **micro SD card** for ubuntu & storage on Raspberry Pi (I use 32GB)
- **1× DHT11** sensor
- **2× DS18B20** temperature sensors, water resistant
- **1× 10 kΩ pull-up resistor** between the DS18B20 data line and 3.3 V
- **Jumper cables & breadboard** for sensor connections
- **Case for raspberry & main case for display & cables** however you want, just DIY

## </> OS & Software Setup

### 1. Install ubuntu (desktop)

Follow the instructions on https://ubuntu.com/tutorials/how-to-install-ubuntu-desktop-on-raspberry-pi-4#1-overview to install ubuntu (24.04) on the micro SD card. It's not necessary to use ubuntu desktop (shh also possible), but this way I can implement/control everything directly on the raspberry.

### 2. OS setup

The pi is running on ubuntu 25.10 (desktop version)

First, install python & i2c tools for the lcd display:

```sudo apt update && sudo apt upgrade -y```
```sudo apt install -y python3 python3-pip python3-venv git curl i2c-tools```

Then, activate SPI, i2c and 1-wire for the temperature sensors:

```echo "i2c-bcm2835" | sudo tee -a /etc/modules```
```echo "i2c-dev" | sudo tee -a /etc/modules```
```echo "w1-gpio" | sudo tee -a /etc/modules```
```echo "w1-therm" | sudo tee -a /etc/modules```

Activate in boot config:

```echo "dtparam=i2c_arm=on" | sudo tee -a /boot/firmware/config.txt```
```echo "dtoverlay=w1-gpio,gpiopin=17" | sudo tee -a /boot/firmware/config.txt```

And reboot by calling ```sudo reboot```.

### 3. Repository setup

Connect to git and checkout this repository (check git documentations). Install Python 3.13 and create a virtual environment by navigating to this repo and run ```python -m venv .venv```. Activate the environment by calling ```source .venv/bin/activate``` (ubuntu). If no poetry.lock file is present in the repo, run ````poetry lock``` and then ```poetry install``` to install every dependency needed for this project directly in the virtual environment.

