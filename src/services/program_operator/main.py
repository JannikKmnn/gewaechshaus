import asyncio

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    window_opener_temp_thres: int = Field(default=25)
    night_mode_on: bool = Field(default=False)


async def main():
    pass


if __name__ == "__main__":
    asyncio.run(main())
