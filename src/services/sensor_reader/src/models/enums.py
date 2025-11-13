from enum import Enum


class SensorType(str, Enum):

    TEMPERATURE = "Temperature"
    HUMIDITY = "Humidity"
    SOIL_MOISTURE = "SoilMoisture"


class MeasureUnit(str, Enum):

    CELSIUS = "°C"
    PERCENT = "%"


class Position(str, Enum):

    LEFT = "Left"
    RIGHT = "Right"
    BACK = "Back"
    FRONT = "Front"
    UP = "Up"
    MIDDLE = "Middle"
    DOWN = "Down"
