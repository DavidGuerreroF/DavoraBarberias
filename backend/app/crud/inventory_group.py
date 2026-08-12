from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models import InventoryGroup
from backend.app.schemas.inventory_group import InventoryGroupCreate, InventoryGroupUpdate


async def create_group(db: AsyncSession, group: InventoryGroupCreate) -> InventoryGroup:
    db_group = InventoryGroup(
        group_code=group.group_code,
        name=group.name,
        description=group.description,
    )
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group


async def get_group(db: AsyncSession, group_id: int) -> InventoryGroup:
    result = await db.execute(select(InventoryGroup).where(InventoryGroup.id == group_id))
    return result.scalars().first()


async def get_group_by_code(db: AsyncSession, group_code: str) -> InventoryGroup:
    result = await db.execute(select(InventoryGroup).where(InventoryGroup.group_code == group_code))
    return result.scalars().first()


async def list_groups(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(InventoryGroup).offset(skip).limit(limit))
    return result.scalars().all()


async def update_group(db: AsyncSession, group_id: int, group: InventoryGroupUpdate) -> InventoryGroup:
    db_group = await get_group(db, group_id)
    if not db_group:
        return None
    
    update_data = group.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_group, key, value)
    
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group


async def delete_group(db: AsyncSession, group_id: int) -> bool:
    db_group = await get_group(db, group_id)
    if not db_group:
        return False
    
    await db.delete(db_group)
    await db.commit()
    return True
