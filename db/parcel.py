from typing import Optional
from sqlalchemy import select
from db.db import get_async_session
from models.parcel import Parcel, ParcelType
from schemas.parcel import ParcelTypeEnum
from settings import logger
from sqlalchemy.ext.asyncio import AsyncSession


async def create_parcel_crud(parcel: Parcel):
    logger.info(f"Запись посылки {parcel.id} в базу данных")
    async for session in get_async_session():
        session.add(parcel)
        await session.commit()
        logger.info(f"Посылка {parcel.id} записана в базу данных")


async def get_parcel_crud(id: int, session: AsyncSession):
    logger.info(f"Запрос к базе на получение посылки {id}.")
    query = select(Parcel).where(Parcel.id == id)
    result = await session.execute(query)
    parcel = result.scalar_one_or_none()
    return parcel


async def get_parcels_by_client_crud(
    price_calculated: Optional[bool],
    type_id: Optional[ParcelTypeEnum],
    skip: int,
    limit: int,
    session_id: str,
    session: AsyncSession,
):
    logger.info(f"Запрос к базе на получение посылок пользователя {session_id}.")
    query = select(Parcel).filter(Parcel.owner == session_id)

    if type_id is not None:
        query = query.filter(Parcel.type_id == type_id.value)

    if price_calculated is not None:
        if price_calculated:
            query = query.filter(Parcel.price.isnot(None))
        else:
            query = query.filter(Parcel.price.is_(None))

    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    parcels = result.scalars().all()
    return parcels


async def get_parcel_type_crud():
    logger.info("Запрос к базе для получения типов посылок")
    async for session in get_async_session():
        query = select(ParcelType.id, ParcelType.name)
        result = await session.execute(query)
        list_parcel_type = result.mappings().all()
        parcel_type_dict = {str(item["id"]): item["name"] for item in list_parcel_type}
        return parcel_type_dict
