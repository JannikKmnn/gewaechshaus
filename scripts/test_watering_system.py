import asyncio
import sys

from pathlib import Path
from dotenv import load_dotenv

from src.shared.actuators import setup_watering_system

env_path = Path(__file__).resolve().parent.parent / ".env.local"
print(env_path)
print(env_path.exists())

load_dotenv(env_path)

# from src.shared.actuators import setup_watering_system

WATERING_PUMP_PIN = 21
WATERING_TIME_SECONDS = 900.0


async def main():

    watering_pump = await setup_watering_system()

    assert watering_pump is not None

    print("Starting Watering System Test...")
    await watering_pump.run_watering()
    print("Watering done.")

    await watering_pump.cleanup()


if __name__ == "__main__":

    print("Starting Watering System Test...")

    asyncio.run(main())

    print("Test done.")
