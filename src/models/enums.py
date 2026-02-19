from enum import Enum


class SensorType(str, Enum):

    TEMPERATURE = "Temperature"
    HUMIDITY = "Humidity"
    SOIL_MOISTURE = "SoilMoisture"
    AIR_PRESSURE = "AirPressure"
    BAROMETRIC = "Barometric"


class MeasureUnit(str, Enum):

    CELSIUS = "°C"
    PERCENT = "%"
    HECTOPASCAL = "hPa"


class Position(str, Enum):

    LEFT = "Left"
    RIGHT = "Right"
    BACK = "Back"
    FRONT = "Front"
    UP = "Up"
    MIDDLE = "Middle"
    DOWN = "Down"
    OUTSIDE = "Outside"
    INSIDE = "Inside"
    PICPU = "Pi CPU"


class InfluxDBResponse(str, Enum):

    NO_CLIENT = "No client defined."
    ERROR = "Error while inserting data into InfluxDB."
    SUCCESS = "Data inserted in InfluxDB."


class DynamicDataAggregation(str, Enum):

    DAYS_1 = "5m"
    DAYS_4 = "10m"
    DAYS_7 = "30m"
    DAYS_14 = "1h"
    DAYS_60 = "2h"
