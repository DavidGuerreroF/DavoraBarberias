from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, func, Numeric, ForeignKey
from backend.app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True)
    product_code = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    cost = Column(Numeric(14, 4), default=0)
    price = Column(Numeric(14, 4), default=0)
    price_list1 = Column(Numeric(14, 4), nullable=True)
    price_list2 = Column(Numeric(14, 4), nullable=True)
    price_list3 = Column(Numeric(14, 4), nullable=True)
    tax_percent = Column(Numeric(5, 2), default=0)
    retention_percent = Column(Numeric(5, 2), default=0)
    inventory_group_id = Column(BigInteger, ForeignKey("inventory_groups.id", ondelete="SET NULL"), nullable=True)
    current_quantity = Column(Numeric(18, 4), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
