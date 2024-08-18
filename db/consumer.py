import json
import logging
import aio_pika
from db.parcel import create_parcel_crud
from logic.periodic_task import get_exchange_rate
from models.parcel import Parcel
from settings import logger, rabbit_settings


async def calculate_price(weight: float, value: float):
    rate = await get_exchange_rate()
    price = (weight * 0.5 + value * 0.01) * rate
    return price


async def consumer():
    logging.basicConfig(level=logging.DEBUG)
    connection = await aio_pika.connect_robust(rabbit_settings.url)

    queue_name = rabbit_settings.queue_name

    async with connection:
        logger.info("Устанавливаю соединение в Раббит консьюмер")
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=100)

        queue = await channel.declare_queue(queue_name, auto_delete=True)
        logger.info("Очередь в Раббит консьюмер получена")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    async with message.process():
                        logger.info(
                            f"Получил из очереди сообщение {message.message_id}"
                        )
                        parcel_data = json.loads(message.body.decode())
                        parcel_data["price"] = await calculate_price(
                            parcel_data["weight"], parcel_data["value_in_dollars"]
                        )
                        new_parcel = Parcel(
                            id=parcel_data["id"],
                            name=parcel_data["name"],
                            weight=parcel_data["weight"],
                            type_id=parcel_data["type_id"],
                            value_in_dollars=parcel_data["value_in_dollars"],
                            price=parcel_data["price"],
                            owner=parcel_data["owner"],
                        )
                        await create_parcel_crud(new_parcel)
                except Exception as e:
                    logger.error(f"Ошибка при обработке сообщения {e}")
