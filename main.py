import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from routers.pycalc_routers import router as math_router
from routers.auth_router import router as auth_router
from db.db_connection import init_db
from prometheus_fastapi_instrumentator import Instrumentator
from streaming.pubsub_consumer import consume
from streaming.kafka_storage import get_kafka_messages


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, consume)

    print("Pub/Sub consumer started.")
    try:
        yield
    finally:
        print("Application shutdown.")

app = FastAPI(lifespan=lifespan)
app.include_router(math_router)
app.include_router(auth_router)


@app.get("/kafka")
async def read_kafka_messages():
    return get_kafka_messages()


@app.get("/")
def home():
    return {"message":"Welcome to my PyCalc app!"}


instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
