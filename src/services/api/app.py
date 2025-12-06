from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.services.api.router.data import router as data_router
from src.services.api.router.windows import router as windows_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        from src.shared.actuators import setup_window_openers

        app.state.actuators = setup_window_openers()
    except ModuleNotFoundError:
        # happens while dev on another machine than the pi
        pass
    finally:
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(data_router, prefix="/data", tags=["measurements"])
app.include_router(windows_router, prefix="/window", tags=["actuators"])
