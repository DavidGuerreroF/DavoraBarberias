from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models import Product
from backend.app.schemas.product import ProductCreate, ProductUpdate


async def create_product(db: AsyncSession, product: ProductCreate) -> Product:
    db_product = Product(
        product_code=product.product_code,
        description=product.description,
        cost=product.cost,
        price=product.price,
        price_list1=product.price_list1,
        price_list2=product.price_list2,
        price_list3=product.price_list3,
        tax_percent=product.tax_percent,
        retention_percent=product.retention_percent,
        inventory_group_id=product.inventory_group_id,
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def get_product(db: AsyncSession, product_id: int) -> Product:
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalars().first()


async def get_product_by_code(db: AsyncSession, product_code: str) -> Product:
    result = await db.execute(select(Product).where(Product.product_code == product_code))
    return result.scalars().first()


async def list_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Product).offset(skip).limit(limit))
    return result.scalars().all()


async def list_products_by_group(db: AsyncSession, group_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Product)
        .where(Product.inventory_group_id == group_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_product(db: AsyncSession, product_id: int, product: ProductUpdate) -> Product:
    db_product = await get_product(db, product_id)
    if not db_product:
        return None
    
    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def delete_product(db: AsyncSession, product_id: int) -> bool:
    db_product = await get_product(db, product_id)
    if not db_product:
        return False
    
    await db.delete(db_product)
    await db.commit()
    return True
