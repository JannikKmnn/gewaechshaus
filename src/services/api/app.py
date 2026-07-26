from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.services.api.router.data import router as data_router
from src.services.api.router.windows import router as windows_router
from src.services.api.router.watering import router as watering_router

from src.shared.sqlite import setup_windows_db, setup_watering_db

from pydantic import Field
from pydantic_settings import BaseSettings

IMPORT_SUCCESS = False
try:
    from src.shared.actuators import setup_window_openers, setup_watering_system

    IMPORT_SUCCESS = True
except ModuleNotFoundError:
    # happens while dev on another machine than the pi
    pass


class Settings(BaseSettings):

    # sqlite setup
    sqlite_db_name: str = Field(default="/data/greenhouse.db")
    sqlite_actuator_events_table: str = Field(default="window_status")
    sqlite_window_entity_table: str = Field(default="window")
    sqlite_watering_events_table: str = Field(default="watering")

    frontend_url: str = Field(default="http://localhost:5173")
    frontend_url_prd: str = Field(default="http://localhost:5174")


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if IMPORT_SUCCESS:
        app.state.actuators = await setup_window_openers()
        app.state.watering_system = await setup_watering_system()

    # Init sqlite DB for window status and watering events
    # Expected to create only once because of persistent DB storage
    _ = await setup_windows_db(
        db_name=settings.sqlite_db_name,
        actuator_events_table=settings.sqlite_actuator_events_table,
    )

    _ = await setup_watering_db(
        db_name=settings.sqlite_db_name,
        watering_events_table=settings.sqlite_watering_events_table,
    )

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, settings.frontend_url_prd],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_router, prefix="/data", tags=["measurements"])
app.include_router(windows_router, prefix="/window", tags=["actuators"])
app.include_router(watering_router, prefix="/watering", tags=["pump"])
