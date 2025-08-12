import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from routers.pycalc_routers import router as math_router
from routers.auth_router import router as auth_router
from streaming.kafka_consumer import consume
from streaming.kafka_producer import start_kafka, stop_kafka
from db.db_connection import init_db
from prometheus_fastapi_instrumentator import Instrumentator

from streaming.kafka_storage import get_kafka_messages


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    await start_kafka()
    kafka_task = asyncio.create_task(consume())
    print("Kafka consumer started.")
    try:
        yield
    finally:
        kafka_task.cancel()
        try:
            await kafka_task
        except asyncio.CancelledError:
            print("Kafka consumer cancelled.")
        await stop_kafka()
        print("Kafka connection closed.")

app = FastAPI(lifespan=lifespan)
app.include_router(math_router)
app.include_router(auth_router)

@app.get("/kafka")
async def read_kafka_messages():
    return get_kafka_messages()

@app.get("/")
def home():
    return {"message": "home"}


instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
