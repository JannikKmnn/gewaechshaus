import httpx

from datetime import timedelta
from logging import Logger


async def run_scheduled_watering(
    url: str,
    logger: Logger,
    duration: timedelta | None = None,
):
    """
    Calls watering API endpoint to start watering for a given duration.
    If no duration is provided, it will use the default duration set in the API.
    """

    base_url = f"{url}/watering/run_watering"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url=base_url,
                json={"duration": duration.total_seconds() if duration else None},
            )
        except httpx.HTTPError as err:
            logger.error(f"Watering call failed due to {err}")
            response = None

    return response
