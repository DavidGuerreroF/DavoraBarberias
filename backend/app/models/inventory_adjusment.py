from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, func, Numeric, ForeignKey
from backend.app.db.database import Base


class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"

    id = Column(BigInteger, primary_key=True, index=True)
    adjustment_number = Column(String(100), unique=True, nullable=False, index=True)
    adjustment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class InventoryAdjustmentItem(Base):
    __tablename__ = "inventory_adjustment_items"

    id = Column(BigInteger, primary_key=True, index=True)
    adjustment_id = Column(BigInteger, ForeignKey("inventory_adjustments.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Numeric(18, 4), nullable=False)  # positivo o negativo
    unit_cost = Column(Numeric(18, 4), nullable=True)
    total_cost = Column(Numeric(18, 4), default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
