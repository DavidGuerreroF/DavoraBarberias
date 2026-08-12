from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class SupplierCreate(BaseModel):
    supplier_code: str = Field(..., min_length=1, max_length=100)
    identification_number: Optional[str] = None
    document_type: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    identification_number: Optional[str] = None
    document_type: Optional[str] = None


class SupplierRead(BaseModel):
    id: int
    supplier_code: str
    identification_number: Optional[str]
    document_type: Optional[str]
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
