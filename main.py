import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
import uvicorn
from db.consumer import consumer
from db.redis import redis_cache
from logic.periodic_task import fetch_exchange_rate
from settings import logger
from routers.parcel import parcel_router


async def periodic_update_exchange_rate():
    while True:
        logger.info("Запуск периодического обновления курса валюты.")
        await fetch_exchange_rate()
        logger.info("Периодическое обновление завершено, жду 1 час.")
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    try:
        logger.info("Поднимаю Редис.")
        await redis_cache.initialize()

        logger.info("Поднимаю Раббит консьюмера")
        consumer_task = asyncio.create_task(consumer())

        logger.info("Запускаю периодическую задачу получения курса")
        asyncio.create_task(periodic_update_exchange_rate())
        yield
    finally:
        logger.info("Останавливаю Редис")
        await redis_cache.close()

        logger.info("Останавливаю Раббит консьюмера")
        consumer_task.cancel()

        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Раббит консьюмер был отменен.")


app = FastAPI(lifespan=lifespan)
app.include_router(parcel_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
