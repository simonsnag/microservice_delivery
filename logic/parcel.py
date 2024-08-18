import random
from typing import Optional

from fastapi import HTTPException
from db.parcel import (
    get_parcel_crud,
    get_parcel_type_crud,
    get_parcels_by_client_crud,
)
from logic.periodic_task import get_exchange_rate
from logic.producer import producer
from models.parcel import Parcel
from schemas.parcel import CreateParcelSchema, DisplayParcelSchema, ParcelTypeEnum
from main import redis_cache
from settings import logger, admin
from sqlalchemy.ext.asyncio import AsyncSession


async def create_parcel_logic(parcel: CreateParcelSchema, session_id: str) -> int:
    """Создает обьект Посылка, сохраняет его в кэш на минуту(на случай если за минуту не будет рассчитана стоимость доставки),
    и добавляет в очередь сообщений"""
    id = random.randint(10**14, int("9" * 15))
    new_parcel = Parcel(
        id=id,
        name=parcel.name,
        weight=parcel.weight,
        type_id=parcel.type_id,
        value_in_dollars=parcel.value_in_dollars,
        owner=session_id,
    )
    await redis_cache.set(str(id), new_parcel.to_dict(), 60)
    try:
        await producer(new_parcel)
        return id
    except Exception as e:
        logger.error(f"Ошибка во время передачи сообщения в очередь: {e}")
        raise HTTPException(
            status_code=503,
            detail=(
                {
                    "status": "error",
                    "message": "Произошла ошибка во время сохранения заявки, пожалуйста, повторите запрос.",
                    "data": None,
                }
            ),
        )


async def get_parcels_by_client_logic(
    price_calculated: Optional[bool],
    type_id: Optional[ParcelTypeEnum],
    skip: int,
    limit: int,
    session_id: str,
    session: AsyncSession,
) -> list:
    """Получение посылок из базы данных(если они уже были обработаны), результат не кэшируется,
    так как данные могут часто меняться, но в будущем можно добавить логику частичного кэширования"""

    list_parcels = await get_parcels_by_client_crud(
        price_calculated, type_id, skip, limit, session_id, session
    )
    if not list_parcels:
        logger.info(f"Посылок пользователя {session_id} нет.")
        raise HTTPException(
            status_code=200,
            detail=(
                {
                    "status": "error",
                    "message": "Посылок для данного пользователя нет или заявки еще не обработаны",
                    "data": None,
                }
            ),
        )
    parcels = []
    for parcel in list_parcels:
        parcel = parcel.to_dict()
        parcel["type"] = await type_id_to_name(parcel["type_id"])
        parcels.append(DisplayParcelSchema.model_validate(parcel))
    return parcels


async def get_parcel_logic(id: int, session_id: str, session: AsyncSession) -> dict:
    """Получение обьекта сначала из кэша(если не прошла минута), далее получение из базы данных
    с уже рассчитанной стоимостью"""

    parcel = await redis_cache.get(str(id))
    if not parcel:
        parcel = await get_parcel_crud(id, session)

        if not parcel:
            logger.info(f"Посылка {id} не существует или еще не обработана")
            raise HTTPException(
                status_code=404,
                detail=(
                    {
                        "status": "error",
                        "message": "Такой посылки не существует или заявка еще не обработана",
                        "data": None,
                    }
                ),
            )
        parcel = parcel.to_dict()

    if parcel["owner"] != session_id:
        logger.info(f"Запрещенный доступ к посылке {id}")
        raise HTTPException(
            status_code=403,
            detail=(
                {
                    "status": "error",
                    "message": "Нет доступа к данным этой посылки.",
                    "data": None,
                }
            ),
        )
    parcel["type"] = await type_id_to_name(parcel["type_id"])
    return parcel


async def get_parcel_type_logic() -> dict:
    """Получение списка типов посылки, кэширование на один час"""

    parcel_type_dict = await redis_cache.get("parcel_type")
    if parcel_type_dict:
        return parcel_type_dict

    parcel_type_dict = await get_parcel_type_crud()
    if not parcel_type_dict:
        logger.warning("Не удалось получить типы посылок.")
        raise HTTPException(
            status_code=404,
            detail=(
                {
                    "status": "error",
                    "message": "Типы посылок не найдены",
                    "data": None,
                }
            ),
        )
    await redis_cache.set("parcel_type", parcel_type_dict, 3600)

    logger.info("Типы посылок закешированы.")
    return parcel_type_dict


async def calculate_rate_logic(admin_session: str) -> float:
    """Обновление курса валют с использованием админ сессии"""
    if admin_session != admin.session:
        raise HTTPException(
            status_code=403,
            detail=({"status": "error", "message": "Заблокированный доступ."}),
        )
    rate = await get_exchange_rate(calculate=True)
    return rate


async def type_id_to_name(id: int):
    parcel_type_dict = await get_parcel_type_logic()
    return parcel_type_dict[str(id)]
