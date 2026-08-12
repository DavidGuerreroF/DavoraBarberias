from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    product_code: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    cost: Decimal = Field(default=Decimal("0"))
    price: Decimal = Field(default=Decimal("0"))
    price_list1: Optional[Decimal] = None
    price_list2: Optional[Decimal] = None
    price_list3: Optional[Decimal] = None
    tax_percent: Decimal = Field(default=Decimal("0"))
    retention_percent: Decimal = Field(default=Decimal("0"))
    inventory_group_id: Optional[int] = None


class ProductUpdate(BaseModel):
    description: Optional[str] = None
    cost: Optional[Decimal] = None
    price: Optional[Decimal] = None
    price_list1: Optional[Decimal] = None
    price_list2: Optional[Decimal] = None
    price_list3: Optional[Decimal] = None
    tax_percent: Optional[Decimal] = None
    retention_percent: Optional[Decimal] = None
    inventory_group_id: Optional[int] = None


class ProductRead(BaseModel):
    id: int
    product_code: str
    description: str
    cost: Decimal
    price: Decimal
    price_list1: Optional[Decimal]
    price_list2: Optional[Decimal]
    price_list3: Optional[Decimal]
    tax_percent: Decimal
    retention_percent: Decimal
    inventory_group_id: Optional[int]
    current_quantity: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
