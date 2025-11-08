import asyncio

from RPLCD.i2c import CharLCD
from main import Settings

settings = Settings()


def display_measurements(lcd_object: CharLCD | None, line_1: str, line_2: str):

    if not lcd_object:
        return None

    lcd_object.clear()

    # make sure only the first {lcd_columns} characters are displayed
    lcd_object.write_string(line_1[: settings.lcd_columns])
    if line_2:
        lcd_object.cursor_pos = (1, 0)
        lcd_object.write_string(str(line_2))


async def display_task(lcd_object: CharLCD, result_dict: dict):

    for sensor, value in result_dict.items():
        if lcd_object is not None:
            display_measurements(lcd_object=lcd_object, line_1=sensor, line_2=value)
        await asyncio.sleep(
            settings.measure_interval_seconds / len(result_dict.values())
        )
