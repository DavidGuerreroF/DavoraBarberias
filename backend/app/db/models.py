from sqlalchemy import (
    Column, BigInteger, String, Text, Numeric, TIMESTAMP, ForeignKey
)
from sqlalchemy.orm import relationship
from .db.session import Base
from sqlalchemy.sql import func

class InventoryGroup(Base):
    __tablename__ = "inventory_groups"
    id = Column(BigInteger, primary_key=True)
    group_code = Column(String(100), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Product(Base):
    __tablename__ = "products"
    id = Column(BigInteger, primary_key=True)
    product_code = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    cost = Column(Numeric(14,4), nullable=False, default=0)
    price = Column(Numeric(14,4), nullable=False, default=0)
    price_list1 = Column(Numeric(14,4))
    price_list2 = Column(Numeric(14,4))
    price_list3 = Column(Numeric(14,4))
    tax_percent = Column(Numeric(5,2), default=0)
    retention_percent = Column(Numeric(5,2), default=0)
    inventory_group_id = Column(BigInteger, ForeignKey("inventory_groups.id", ondelete="SET NULL"))
    current_quantity = Column(Numeric(18,4), nullable=False, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    group = relationship("InventoryGroup", backref="products")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(BigInteger, primary_key=True)
    supplier_code = Column(String(100), nullable=False, unique=True)
    identification_number = Column(String(100))
    document_type = Column(String(50))
    name = Column(String(255), nullable=False)
    phone = Column(String(50))
    email = Column(String(255))
    address = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

# (Puedes añadir mapeo de inventory_entries, inventory_entry_items, exits, adjustments si los necesitas
#  ahora o hacerlo por separado. Para empezar con la conexión y CRUD de productos, esto es suficiente.)