from fastapi import FastAPI

from router.data import router as data_router

app = FastAPI()

app.include_router(data_router, prefix="/data", tags=["measurements"])
