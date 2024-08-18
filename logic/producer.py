import json
import aio_pika

from models.parcel import Parcel
from settings import rabbit_settings
from settings import logger


async def producer(parcel: Parcel):
    logger.info("Соединение с RabbitMQ.")
    connection = await aio_pika.connect_robust(rabbit_settings.url)
    async with connection:
        async with connection.channel() as channel:
            logger.info("Запись сообщения в очередь.")
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(parcel.to_dict()).encode()),
                routing_key=rabbit_settings.queue_name,
            )
            logger.info("Сообщение записано в очередь.")
