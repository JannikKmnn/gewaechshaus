from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.services.api.router.data import router as data_router
from src.services.api.router.windows import router as windows_router

from src.shared.sqlite import setup_db

from pydantic import Field
from pydantic_settings import BaseSettings

IMPORT_SUCCESS = False
try:
    from src.shared.actuators import setup_window_openers

    IMPORT_SUCCESS = True
except ModuleNotFoundError:
    # happens while dev on another machine than the pi
    pass


class Settings(BaseSettings):

    # sqlite setup
    sqlite_db_name = Field(default="/data/greenhouse.db")
    sqlite_actuator_events_table = Field(default="window_status")


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if IMPORT_SUCCESS:
        app.state.actuators = await setup_window_openers()

    # Init sqlite DB for window status
    # Expected to create only once because of persistent DB storage
    _ = await setup_db(
        db_name=settings.sqlite_db_name,
        actuator_events_table=settings.sqlite_actuator_events_table,
    )

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(data_router, prefix="/data", tags=["measurements"])
app.include_router(windows_router, prefix="/window", tags=["actuators"])
