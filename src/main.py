import board
import adafruit_dht
import time

from pydantic import Field
from pydantic_settings import BaseSettings

GPIO_PIN_HUMIDITY_TEMPERATURE_SENSOR = board.D4
GPIO_PIN_TEMPERATURE_SENSOR_INSIDE = board.D17
GPIO_PIN_TEMPERATURE_SENSOR_OUTSIDE = board.D22


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


def main():

    humidityTemperatureDevice = adafruit_dht.DHT11(GPIO_PIN_HUMIDITY_TEMPERATURE_SENSOR, use_pulseio=False)

    while True:

        humidity, temperature_middle = measure_humidity_temperature(
            device_object=humidityTemperatureDevice
        )

        print(
            f"Humidity: {humidity}%, Temperature (Middle): {temperature_middle}°C"
        )

        time.sleep(settings.measure_interval_seconds)

    

if __name__ == "__main__":
    main()