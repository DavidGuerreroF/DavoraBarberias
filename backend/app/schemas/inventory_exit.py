from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class InventoryExitItemCreate(BaseModel):
    product_id: int
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Decimal = Field(default=Decimal("0"))


class InventoryExitCreate(BaseModel):
    exit_number: str = Field(..., min_length=1, max_length=100)
    supplier_id: Optional[int] = None
    invoice_number: Optional[str] = None
    notes: Optional[str] = None
    items: List[InventoryExitItemCreate] = Field(..., min_items=1)


class InventoryExitItemRead(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryExitRead(BaseModel):
    id: int
    exit_number: str
    exit_date: datetime
    supplier_id: Optional[int]
    invoice_number: Optional[str]
    notes: Optional[str]
    total_cost: Decimal
    created_at: datetime
    items: List[InventoryExitItemRead] = []

    class Config:
        from_attributes = True
