from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InventoryGroupCreate(BaseModel):
    group_code: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class InventoryGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class InventoryGroupRead(BaseModel):
    id: int
    group_code: str
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
