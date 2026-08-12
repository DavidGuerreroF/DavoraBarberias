from pydantic import BaseModel, condecimal
from typing import Optional

Decimal = condecimal(max_digits=18, decimal_places=4)

class ProductBase(BaseModel):
    product_code: str
    description: str
    cost: Optional[Decimal] = 0
    price: Optional[Decimal] = 0
    inventory_group_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int
    current_quantity: Optional[Decimal] = 0

    class Config:
        orm_mode = True