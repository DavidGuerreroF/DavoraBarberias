from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models import Supplier
from backend.app.schemas.supplier import SupplierCreate, SupplierUpdate


async def create_supplier(db: AsyncSession, supplier: SupplierCreate) -> Supplier:
    db_supplier = Supplier(
        supplier_code=supplier.supplier_code,
        identification_number=supplier.identification_number,
        document_type=supplier.document_type,
        name=supplier.name,
        phone=supplier.phone,
        email=supplier.email,
        address=supplier.address,
    )
    db.add(db_supplier)
    await db.commit()
    await db.refresh(db_supplier)
    return db_supplier


async def get_supplier(db: AsyncSession, supplier_id: int) -> Supplier:
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    return result.scalars().first()


async def get_supplier_by_code(db: AsyncSession, supplier_code: str) -> Supplier:
    result = await db.execute(select(Supplier).where(Supplier.supplier_code == supplier_code))
    return result.scalars().first()


async def list_suppliers(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Supplier).offset(skip).limit(limit))
    return result.scalars().all()


async def update_supplier(db: AsyncSession, supplier_id: int, supplier: SupplierUpdate) -> Supplier:
    db_supplier = await get_supplier(db, supplier_id)
    if not db_supplier:
        return None
    
    update_data = supplier.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_supplier, key, value)
    
    db.add(db_supplier)
    await db.commit()
    await db.refresh(db_supplier)
    return db_supplier


async def delete_supplier(db: AsyncSession, supplier_id: int) -> bool:
    db_supplier = await get_supplier(db, supplier_id)
    if not db_supplier:
        return False
    
    await db.delete(db_supplier)
    await db.commit()
    return True
