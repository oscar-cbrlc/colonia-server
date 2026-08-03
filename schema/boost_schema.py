from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BoostBase(BaseModel):
    boost_name: str = Field(min_length=1)
    boost_description: str = Field(min_length=1)
    boost_effect: Decimal
    boost_image: str = Field(min_length=1)


class BoostCreate(BoostBase):
    pass


class BoostUpdate(BaseModel):
    boost_name: str | None = Field(default=None, min_length=1)
    boost_description: str | None = Field(default=None, min_length=1)
    boost_effect: Decimal | None = None
    boost_image: str | None = Field(default=None, min_length=1)


class BoostResponse(BoostBase):
    boost_id: int

    model_config = ConfigDict(from_attributes=True)
