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


class MQTTResponse(str, Enum):

    NO_CLIENT = "No client defined."
    CLIENT_CRASHED = "Client crashed while publishing message."
    SUCCESS = "Message published."


class InfluxDBResponse(str, Enum):

    NO_CLIENT = "No client defined."
    ERROR = "Error while inserting data into InfluxDB."
    SUCCESS = "Data inserted in InfluxDB."
