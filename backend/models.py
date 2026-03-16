from pydantic import BaseModel, field_validator


class CreateItemRequest(BaseModel):
    name: str
    quantity: float = 1
    unit: str | None = None
    tags: list[str] = []

    @field_validator("quantity")
    @classmethod
    def quantity_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("quantity must be >= 0")
        return v


class UpdateItemRequest(BaseModel):
    name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    tags: list[str] | None = None

    @field_validator("quantity")
    @classmethod
    def quantity_non_negative(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("quantity must be >= 0")
        return v


class TagResponse(BaseModel):
    id: int
    name: str
    color: str | None


class ItemResponse(BaseModel):
    id: int
    name: str
    quantity: float
    unit: str | None
    barcode: str | None
    tags: list[TagResponse]
    created_at: str
    updated_at: str


class CreateTagRequest(BaseModel):
    name: str
    color: str | None = None
