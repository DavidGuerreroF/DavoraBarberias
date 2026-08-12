from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class InventoryEntryItemCreate(BaseModel):
    product_id: int
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Decimal = Field(default=Decimal("0"))
    tax_percent: Optional[Decimal] = None
    retention_percent: Optional[Decimal] = None


class InventoryEntryCreate(BaseModel):
    entry_number: str = Field(..., min_length=1, max_length=100)
    supplier_id: Optional[int] = None
    invoice_number: Optional[str] = None
    notes: Optional[str] = None
    items: List[InventoryEntryItemCreate] = Field(..., min_items=1)


class InventoryEntryItemRead(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_cost: Decimal
    tax_percent: Optional[Decimal]
    retention_percent: Optional[Decimal]
    total_cost: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryEntryRead(BaseModel):
    id: int
    entry_number: str
    entry_date: datetime
    supplier_id: Optional[int]
    invoice_number: Optional[str]
    notes: Optional[str]
    total_cost: Decimal
    created_at: datetime
    items: List[InventoryEntryItemRead] = []

    class Config:
        from_attributes = True
