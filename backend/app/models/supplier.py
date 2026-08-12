from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, func
from backend.app.db.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(BigInteger, primary_key=True, index=True)
    supplier_code = Column(String(100), unique=True, nullable=False, index=True)
    identification_number = Column(String(100), nullable=True)
    document_type = Column(String(50), nullable=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
