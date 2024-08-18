import asyncio
import json
import aiohttp
from db.redis import redis_cache
from settings import logger


async def fetch_exchange_rate():
    """Получение курса валюты с внешнего API."""
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    async with aiohttp.ClientSession() as session:
        logger.info("Запрос на внешний ресурс для получения курса валют.")
        attempt = 0
        while attempt < 5:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.text()
                        rate = json.loads(data)["Valute"]["USD"]["Value"]
                        await redis_cache.set("rate", {"rate": rate}, 3600)
                        logger.info("Курс валют получен.")
                        return float(rate)
            except Exception as e:
                logger.warning(f"Ошибка получения курса: {e}, пробую еще раз.")
                attempt += 1
                await asyncio.sleep(2)

    logger.error("Не удалось получить курс после нескольких попыток.")
    return None


async def get_exchange_rate(calculate: bool = False) -> float:
    """Получение курса валюты из кэша или с внешнего API."""
    if not calculate:
        rate = await redis_cache.get("rate")
        if rate:
            return rate["rate"]

    return await fetch_exchange_rate()
