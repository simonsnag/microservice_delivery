from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.params import Query

from db.db import get_async_session
from routers.depends import get_session_id
from schemas.parcel import CreateParcelSchema, DisplayParcelSchema, ParcelTypeEnum
from logic.parcel import (
    calculate_rate_logic,
    create_parcel_logic,
    get_parcel_logic,
    get_parcel_type_logic,
    get_parcels_by_client_logic,
)
from sqlalchemy.ext.asyncio import AsyncSession

parcel_router = APIRouter()


@parcel_router.post("/parcel")
async def create_parcel(
    parcel: CreateParcelSchema,
    session_id: str = Depends(get_session_id),
) -> dict:
    parcel_id = await create_parcel_logic(parcel, session_id)
    return {
        "status": "success",
        "message": "Ваша заявка принята. Номер посылки:",
        "data": {"parcel_id": parcel_id},
    }


@parcel_router.get("/parcel_type")
async def get_parcel_type() -> dict:
    parcel_type_dict = await get_parcel_type_logic()
    return {
        "status": "success",
        "message": "Все типы посылок",
        "data": parcel_type_dict,
    }


@parcel_router.get("/parcel")
async def get_parcels_by_client(
    price_calculated: Optional[bool] = None,
    type_id: Optional[ParcelTypeEnum] = None,
    skip: int = Query(0),
    limit: int = Query(10),
    session_id: str = Depends(get_session_id),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    parcels = await get_parcels_by_client_logic(
        price_calculated, type_id, skip, limit, session_id, session
    )
    return {
        "status": "success",
        "message": "Посылки данного пользователя.",
        "data": parcels,
    }


@parcel_router.get("/parcel/{id}")
async def get_parcel(
    id: int,
    session_id: str = Depends(get_session_id),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    parcel = await get_parcel_logic(id, session_id, session)
    parcel = DisplayParcelSchema.model_validate(parcel)
    return {
        "status": "success",
        "message": "Информация о посылке",
        "data": parcel,
    }


@parcel_router.get("/admin/calculate_rate")
async def calculate_rate(admin_session: str) -> dict:
    rate = await calculate_rate_logic(admin_session)
    return {
        "status": "success",
        "message": "Данные о курсе доллар/рубля обновлены. Актуальный курс:",
        "rate": rate,
    }
