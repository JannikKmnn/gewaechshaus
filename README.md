# 🧠🌱 Raspberry Pi Greenhouse Automations

This project implements a fully automated Raspberry Pi–powered greenhouse control system.
It collects environmental sensor data (temperature, humidity, pressure, and soil moisture), stores and visualizes telemetry, and automatically controls ventilation using linear actuators — all accessible via a custom web dashboard and API.

All sensor readings are periodically collected, logged, displayed inside a little self-made box for the raspi as well as stored inside an InfluxDB cloud instance. This allows both real time and historical data analysis on the measurements inside the frontend:

### Monitoring Dashboard
![Frontend dashboard (this one from winter time...)](images/frontend_dashboard.png?raw=true "Sensor Monitoring")

![InfluxDB dashboard](images/influxdb_dashboard.png?raw=true "Influx Monitoring")

The window events (opening/closing) are monitor- and controllable in the "Control Center" section in the frontend. I'm also collecting the timestamps of the window calls to reproduce the last openings times. The window calls are done either manually via the dashboard or the program operator service which is responsible for automatically open/close events based on pre defined thresholds for the inside temperature.

### Control Center
![Control Center dashboard](images/frontend_control_center.png?raw=true "Control Center")

In addition, a fastapi instance is implemented to fetch the sensor readings in a specific timeframe from the InfluxDB as well as opening and closing of the windows.

### API Interface
![fastapi interface](images/api.png?raw=true "API")

The idea is to build a fully automated system to minimize manual work by automation of ventilation and watering in the greenhouse as well as implementing a full-on web application from scratch to monitor and control every sensor remotely.

---

## 🛠 Tech Stack

- Python (asyncio, FastAPI)
- Raspberry Pi GPIO
- InfluxDB Cloud
- React + Vite
- Docker & Docker Compose
- Netdata monitoring
- Tailscale VPN

## 🔛 (Virtual) environment setup

The following setup is suited to develop directly on the pi, this is why allowing ssh access or the ubuntu desktop version is recommended.

After checking out this repository, navigate to the root folder (/gewaechshaus) and run

```python -m venv .venv```

This creates a .venv folder containing the python virtual environment which can by activated by running

```source .venv/bin/activate```

on ubuntu. Next, every dependency defined in this repo can be directly installed and managed via poetry. For that, install poetry according to the [documentation](https://www.digitalocean.com/community/tutorials/how-to-install-poetry-to-manage-python-dependencies-on-ubuntu-22-04) and simply run

```poetry install```

This will install all dependencies necessary for this project into your venv.

To secretly store your influxDB properties as well as the environment variables for the actuator pins, create an .env file in your root folder containing following environment variables (insert your values from InfluxDB cloud):

```
LCD_COLUMNS=16

INFLUXDB_HOST=<YOUR_HOST>
INFLUXDB_ORG=<YOUR_ORGANISATION_NAME>
INFLUXDB_BUCKET=<YOUR_BUCKET_NAME>
INFLUXDB_TOKEN=<YOUR_TOKEN>

SQLITE_DB_NAME=<LOCAL_SQLITE_DB_PATH>
SQLITE_ACTUATOR_EVENTS_TABLE=window_status

WINDOW_ACTUATOR_LEFT_EXTEND_PIN=<GPIO_PIN_LEFT_EXTEND>
WINDOW_ACTUATOR_LEFT_RETRACT_PIN=<GPIO_PIN_LEFT_RETRACT>
WINDOW_ACTUATOR_RIGHT_EXTEND_PIN=<GPIO_PIN_RIGHT_EXTEND>
WINDOW_ACTUATOR_RIGHT_RETRACT_PIN=<GPIO_PIN_RIGHT_RETRACT>
WINDOW_MOVING_TIME=<HOW_LONG_ACTUATOR_TAKES>

CPU_TEMP_PATH=/sys/class/thermal/thermal_zone0/temp

FRONTEND_URL=<YOUR_LOCAL_FRONTEND_URL>
VITE_API_BASE_URL=<BASE_API_FOR_FRONTEND>
```

The docker-compose will load these environment variables while building the image. To start it, navigate to the repo root and run ```docker compose up -d --build```. Docker will create 6 images and start their corresponding containers:

- ```gewaechshaus-program-operator```: The cron worker that fetches the temperature from inside the greenhouse in a given interval (15 minutes) and operates on windows if certain thresholds are crossed. Source code in ```src/services/program_operator```.
- ```gewaechshaus-api```: The uvicorn fastapi instance with endpoints to fetch data and call windows. Source code in ```src/services/api```.
- ```gewaechshaus-sensor-reader```: The sensor reader to read GPIO singals from sensors, writes measurement into InfluxDB and displays values on lcd display. Source code in ```src/services/sensor_reader```.
- ```gewaechshaus-frontend```: React frontend for web dashboard. Source code in ```frontend/gewaechshaus```.
- ```netdata```: To monitor pi resources, such as memory & cpu load, disk I/O, network and container resources.
- ```sqlite-web```: UI for lightweight SQLite database on the pi.

## 📸 Pictures & Greenhouse Information

The greenhouse is made of wood and isolated with standard greenhouse foil to trap heat inside. It's 70cm x 90cm x ca. 160cm, while the bottom is directly connected to the surrounding soil and a second level is addable. This level serves also as an option either to add more plant pots...

<p align="center">
    <img src="images/inside_greenhouse.jpg" alt="Inside the greenhouse" width="300"/>
</p>

...or to develop directly at a desktop inside the greenhouse! (ssh access is activated now so not required but still cool)

<p align="center">
    <img src="images/desktop_greenhouse.jpg" alt="Desktop in greenhouse" width="300"/>
</p>

The box at the top left position is the "house" of the Raspberry and the 16x2 lcd display, which displays all the measurements successively in every measure cycle. Inside, a breadboard and a bunch of jumper cables ensure a stable connection between the sensors and the pi, which measures on different GPIO pins asynchronously.

<p align="center">
    <img src="images/inside_box.jpg" alt="Inside box" width="300"/>
</p>

Another cool feature is the lightning in the night since different leds indicate wet or dry soil moistures, and together with the display a futuristic effect is made:

<p align="center">
    <img src="images/night_greenhouse.jpg" alt="Greenhouse at night" width="300"/>
</p>

The windows are opened and closed by 12V linear actuators which are connected with a H-Bridge to 2-channel-relays that are controlled by the pi and via the API or via scripts.

<p align="center">
    <img src="images/window_open.jpg" alt="Opened window by actuator" width="300"/>
</p>

<p align="center">
    <img src="images/actuator_wiring.jpg" alt="Actuators connected to raspi house" width="300"/>
</p>
---

## 🎛️ Sensor Setup & GPIO wiring

> ⚠️ Note: The sensor wiring is customized for this greenhouse setup.  
> The software can run without hardware, but sensor_reader requires GPIO-connected devices.

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
- ⚙️ **2× Linear Actuators for Wiring** (+ 2 Double-Pole 5V Relays)
    - Actuator - -> COM2
    - Actuator + -> COM1
    - 12V DC - -> NC1 and NC2
    - 12V DC + -> NO1 and NO2
    - 5V VCC -> Relays VCC
    - Pi GND -> Relays GND
    - Actuator Right Extend Pin (GPIO 16) -> Relays (R) IN1
    - Actuator Right Retract Pin (GPIO 20) -> Relays (R) IN2
    - Actuator Left Extend Pin (GPIO 5) -> Relays (L) IN1
    - Actuator Left Retract Pin (GPIO 6) -> Relays (L) IN2


---

# 🕹️ OS setup & software resources

The pi runs on ubuntu 25.10 lts (desktop version) and Python 3.13. Other ubuntu version should also work, just select one that suites best from the [Raspberry Pi Imager](https://www.raspberrypi.com/software/). The OS setup for the sensors (i2cdetect, config.txt lines, modules etc.) are readable in the specific documentations.

The repository contains poetry for dependency management and docker/docker-compose to run the application inside a container on the pi. The models and settings are wrapped by pydantic models and the environment variables are set either inside the docker files or (for sensitive informations like the influxdb connection details) inside an .env file. For local development, I use vscode and a virtual environment managed with poetry.

The data pipeline starts at the sensors, whereas the sensor_reader container is responsible for reading the data from the hardware, writing them into the InfluxDB and displaying the values frequently on the display inside the greenhouse. In addition, a lightweight SQLite DB is running on the pi to log the opening/closing events of the windows. The API is then structured to query the databases and provides endpoints to call on the windows or fetch data series, while big requests (>1 day, minute interval) are aggregated to ensure smooth and fast returns. The API is called from the frontend or by the program operator, which runs an asynchronous worker every 15 minutes to fetch the latest temperature inside datapoints and act on the window endpoints if required (thresholds defined as environment variables).

<p align="center">
    <img src="images/service_interactions.png" alt="Service architecture and data flow" width="300"/>
</p>

## ✨ Features

- 🌡 Real-time environmental monitoring
- 📈 Historical telemetry & dashboards
- 🪟 Automated window ventilation
- 🌱 Soil moisture monitoring
- 🌐 Remote control via web dashboard
- 🔒 Secure remote access via Tailscale VPN
- 🐳 Containerized multi-service architecture
