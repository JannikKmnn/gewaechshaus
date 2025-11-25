# 🧠🌱 Raspberry Pi Greenhouse Automations

This smart home automation project represents the codebase to collect physical data inside my little garden greenhouse from multiple sensors connected to a Raspberry Pi 4 — including temperature, humidity, air pressure and soil moisture.

All sensor readings are periodically collected, logged, displayed inside a little self-made box for the raspi as well as stored inside an InfluxDB cloud instance. This allows both real time and historical data analysis on the measurements:

![InfluxDB dashboard (this one from winter time...)](images/influxdb_dashboard.png?raw=true "Sensor Monitoring")

Currently, this MVP includes mainly storing & displaying sensor values to indicate if certain actions on the greenhouse are required (watering, ventilation). The idea is to build a fully automated system to minimize manual work in the greenhouse as well as implementing a full-on web application from scratch to monitor and control every sensor remotely. Adding linear actuators to automatically open & close the windows is a work in progress.

---

## 📸 Pictures & Greenhouse Informations

The greenhous is made out of wood and isolated with standard greenhouse foil to trap heat inside. It's 70cm x 90cm x ca. 160cm, while the bottom is directly connected to the surrounding soil and a second level is addable. This level serves also as an option either to add more plant pots...

<p align="center">
    <img src="images/inside_greenhouse.jpg" alt="Inside the greenhouse" width="300"/>
</p>

...or to develop directly at a desktop inside the greenhouse! (ssh access is activated now so not required but still cool)

<p align="center">
    <img src="images/desktop_greenhouse.jpg" alt="Desktop in greenhouse" width="300"/>
</p>

The box at the top left position is the "house" of the rasperry and the 16x2 lcd display. Inside, a breadboard and a bunch of jumper cables ensure a stable connection between the sensors and the pi, which measures on different GPIO pins asynchronously.

<p align="center">
    <img src="images/inside_box.jpg" alt="Inside box" width="300"/>
</p>

Another cool feature is the lightning in the night since different leds indicate wet or dry soil moistures, and together with the display a futuristic effect is made:

<p align="center">
    <img src="images/night_greenhouse.jpg" alt="Greenhouse at night" width="300"/>
</p>

---

## 🎛️ Sensor Setup & GPIO wiring

- 🧠 **Raspberry Pi 4 Model B**
- 🖥️ **1× 16c2 lcd display** with IIC/I2c interface for easy wiring:
    - 5V VCC -> 5V VCC
    - GND -> GND
    - SDA -> SDA
    - SCL -> SCL 
- 🫧 **1× GY-BME280** barometric sensor for temperature, air humidity and air pressure
    - 5V VCC -> 5V VCC
    - GND -> GND
    - SDA -> SDA
    - SCL -> SCL 
    - (Since SDA/SCL are bus pins, multiple wiring together with the display shouldn't be a problem)
- 🌡️ **2× DS18B20** temperature sensors, water resistant
    - 3V VCC -> 3V VCC
    - GND -> GND
    - DATA -> Any GPIO pin, checkout this [tutorial](https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/)
    - (10k Ohm resistor in parallel to the sensors required)
- 🫗 **2× Soil Moisture Sensors**
    - 5V VCC -> 5V VCC
    - GND -> GND
    - DATA SM1 -> GPIO 23 (Physical 16)
    - DATA SM2 -> GPIO 24 (Physical 18)

---

# 🕹️ OS setup & software resources

The pi runs on ubuntu 25.10 lts (desktop version) and Python 3.13. Other ubuntu version should also work, just select one that suites best from the [Raspberry Pi Imager](https://www.raspberrypi.com/software/).The OS setup for the sensors (i2cdetect, config.txt lines, modules etc.) are readable in the specific documentations.

The repository contains poetry for dependency management and docker/docker-compose to run the application inside a container on the pi. The models and settings are wrapped by pydantic models and the envrionment variables are set either inside the docker files or (for sensitive informations like the influxdb connection details) inside an .env file. For local development, I use vscode and a virtual environment managed with poetry.

Basic python and

## 🔛 (Virtual) environment setup

The following setup is suited to develop directly on the pi, this is why allowing ssh access or the ubuntu desktop version is recommended.

After checking out this repository, navigate to the root folder (´´´/gewaechshaus´´´) and run

```python -m venv .venv```

This creates a .venv folder containing the python virtual environment which can by activated by running

```source .venv/bin/activate```

on ubuntu. Next, every dependency defined in this repo can be directly installed via poetry. For that, install poetry according to the [documentation](https://www.digitalocean.com/community/tutorials/how-to-install-poetry-to-manage-python-dependencies-on-ubuntu-22-04) and simply run

```poetry install```

This will install all dependencies necessary for this project into your venv.

To secretly store your influxDB properties, create an .env file in you root folder containing following environment variables (insert your values from InfluxDB cloud):

```
INFLUXDB_HOST=<YOUR_HOST>
INFLUXDB_ORG=<YOUR_ORGANISATION_NAME>
INFLUXDB_BUCKET=<YOUR_BUCKET_NAME>
INFLUXDB_TOKEN=<YOUR_TOKEN>
```

The docker-compose will load these environment variables while building the image.


