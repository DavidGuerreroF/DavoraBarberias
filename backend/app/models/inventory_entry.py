from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, func, Numeric, ForeignKey, CheckConstraint
from backend.app.db.database import Base


class InventoryEntry(Base):
    __tablename__ = "inventory_entries"

    id = Column(BigInteger, primary_key=True, index=True)
    entry_number = Column(String(100), unique=True, nullable=False, index=True)
    entry_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    supplier_id = Column(BigInteger, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)
    invoice_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    total_cost = Column(Numeric(18, 4), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class InventoryEntryItem(Base):
    __tablename__ = "inventory_entry_items"

    id = Column(BigInteger, primary_key=True, index=True)
    entry_id = Column(BigInteger, ForeignKey("inventory_entries.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Numeric(18, 4), nullable=False)
    unit_cost = Column(Numeric(18, 4), default=0)
    tax_percent = Column(Numeric(5, 2), nullable=True)
    retention_percent = Column(Numeric(5, 2), nullable=True)
    total_cost = Column(Numeric(18, 4), default=0)  # quantity * unit_cost
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("quantity >= 0"),
    )
