from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class InventoryAdjustmentItemCreate(BaseModel):
    product_id: int
    quantity: Decimal  # puede ser positivo o negativo
    unit_cost: Optional[Decimal] = None
    notes: Optional[str] = None


class InventoryAdjustmentCreate(BaseModel):
    adjustment_number: str = Field(..., min_length=1, max_length=100)
    reason: Optional[str] = None
    notes: Optional[str] = None
    items: List[InventoryAdjustmentItemCreate] = Field(..., min_items=1)


class InventoryAdjustmentItemRead(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_cost: Optional[Decimal]
    total_cost: Decimal
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryAdjustmentRead(BaseModel):
    id: int
    adjustment_number: str
    adjustment_date: datetime
    reason: Optional[str]
    notes: Optional[str]
    created_at: datetime
    items: List[InventoryAdjustmentItemRead] = []

    class Config:
        from_attributes = True
