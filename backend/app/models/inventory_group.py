from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, func
from backend.app.db.database import Base


class InventoryGroup(Base):
    __tablename__ = "inventory_groups"

    id = Column(BigInteger, primary_key=True, index=True)
    group_code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
