from datetime import datetime, timezone
from typing import List
from sqlalchemy import BIGINT, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class ParcelType(Base):
    __tablename__ = "parcel_type"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    parcels: Mapped[List["Parcel"]] = relationship(
        "Parcel", back_populates="parcel_type"
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Parcel(Base):
    __tablename__ = "parcel"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("parcel_type.id"), nullable=False)
    value_in_dollars: Mapped[float] = mapped_column(nullable=False)
    price: Mapped[float | None] = mapped_column(nullable=True)
    owner: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    time_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    parcel_type: Mapped[ParcelType] = relationship(
        "ParcelType", back_populates="parcels"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "weight": self.weight,
            "type_id": self.type_id,
            "value_in_dollars": self.value_in_dollars,
            "price": self.price,
            "owner": self.owner,
        }
