import board
import adafruit_dht
import time

from datetime import datetime
from pydantic import Field
from pydantic_settings import BaseSettings

from w1thermsensor import W1ThermSensor

GPIO_PIN_HUMIDITY_TEMPERATURE_SENSOR = board.D4


class Settings(BaseSettings):

    measure_interval_seconds: int = Field(default=20)
    display_switch_interval: int = Field(default=10)

settings = Settings()

def measure_humidity_temperature(device_object: adafruit_dht.DHT11):

    try:

        temperature_c = device_object.temperature
        humidity = device_object.humidity

    except RuntimeError as error:

        print(f"Measuring humidity and temperature ran into runtime error: {error}")
        temperature_c = None
        humidity = None

    except Exception as error:

        print(f"Measuring humidity and temperature ran into unknown error: {error}")
        temperature_c = None
        humidity = None

    return humidity, temperature_c

def measure_temperature(sensor_object: W1ThermSensor):
    
    try:

        temperature_c = sensor_object.get_temperature()

    except Exception as error:

        print(f"Measuring outside temperature ran into unknown error: {error}")
        temperature_c = None

    return temperature_c

def main():

    humidityTemperatureDevice = adafruit_dht.DHT11(GPIO_PIN_HUMIDITY_TEMPERATURE_SENSOR, use_pulseio=False)
    temperatureOutsideSensor = W1ThermSensor()

    while True:

        humidity, temperature_middle = measure_humidity_temperature(
            device_object=humidityTemperatureDevice
        )

        temperature_outside = measure_temperature(
            sensor_object=temperatureOutsideSensor
        )

        print(
            f"""
            Measurements {datetime.now()}:
            - Humidity: {humidity}%, 
            - Temperature (Middle): {temperature_middle}°C
            - Temperature (Outside): {temperature_outside}°C
            """
        )

        time.sleep(settings.measure_interval_seconds)

    

if __name__ == "__main__":
    main()