from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from routers.pycalc_routers import router as math_router
from routers.auth_router import router as auth_router
from db.db_connection import init_db
from prometheus_fastapi_instrumentator import Instrumentator


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(math_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "home"}


instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
