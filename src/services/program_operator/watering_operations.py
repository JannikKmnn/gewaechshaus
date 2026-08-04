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

    read_write_timeout = (
        max(duration.total_seconds() + 80, 30) if duration is not None else 1000
    )

    timeout = httpx.Timeout(
        30.0,
        read=read_write_timeout,
        write=read_write_timeout,
    )

    async with httpx.AsyncClient(timeout=timeout) as client:
        logger.info(f"Starting Watering API call with duration {duration}...")
        try:
            response = await client.post(
                url=base_url,
                json={
                    "watering_time_seconds": (
                        int(duration.total_seconds()) if duration else None
                    )
                },
            )
            response.raise_for_status()
            return response
        except httpx.HTTPError as err:
            logger.error(f"Watering call failed due to {err}")
            return None
