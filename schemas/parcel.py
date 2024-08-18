from enum import Enum
from typing import Optional
from pydantic import Field, field_validator
from schemas.base import BaseSchema


class CreateParcelSchema(BaseSchema):
    name: str = Field(max_length=128)
    weight: float = Field(gt=0)
    type_id: int = Field(
        ge=1,
        le=3,
    )
    value_in_dollars: float = Field(
        gt=0,
    )

    class Config:
        from_attributes = True


class DisplayParcelSchema(BaseSchema):
    id: int
    name: str
    weight: float = Field(gt=0)
    type_id: int
    type: str
    value_in_dollars: float = Field(gt=0)
    price: Optional[float | str] = Field(gt=0)

    @field_validator("price")
    def set_default_price(cls, v):
        if v is None:
            return "Не рассчитано"
        return v

    class Config:
        from_attributes = True


class ParcelTypeEnum(int, Enum):
    cloth = 1
    electron = 2
    differ = 3
