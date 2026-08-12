from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models
from .schemas import ProductCreate

async def get_products(db: AsyncSession, limit: int = 100, offset: int = 0):
    q = select(models.Product).limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()

async def get_product_by_code(db: AsyncSession, product_code: str):
    q = select(models.Product).where(models.Product.product_code == product_code)
    result = await db.execute(q)
    return result.scalars().first()

async def create_product(db: AsyncSession, product_in: ProductCreate):
    product = models.Product(
        product_code=product_in.product_code,
        description=product_in.description,
        cost=product_in.cost or 0,
        price=product_in.price or 0,
        inventory_group_id=product_in.inventory_group_id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product