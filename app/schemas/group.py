from pydantic import BaseModel, Field, ConfigDict


class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    trainer_id: int
    price_per_training: float = Field(ge=0)
    subscription_price: float = Field(ge=0)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    trainer_id: int | None = None
    price_per_training: float | None = Field(default=None, ge=0)
    subscription_price: float | None = Field(default=None, ge=0)


class GroupResponse(GroupBase):
    id: int

    model_config = ConfigDict(from_attributes=True)