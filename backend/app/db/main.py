import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from typing import List

from .db.session import engine, Base, get_db
from . import crud, schemas, models
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="Inventory API")

# Health
@app.get("/health")
async def health():
    return {"status": "ok"}

# Crear tablas (solo para desarrollo; en producción usa Alembic)
@app.on_event("startup")
async def startup():
    # crear tablas si no existen (sync-like using engine.begin)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/products", response_model=List[schemas.ProductRead])
async def list_products(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    products = await crud.get_products(db, limit=limit, offset=offset)
    return products

@app.post("/products", response_model=schemas.ProductRead, status_code=201)
async def create_product(product_in: schemas.ProductCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_product_by_code(db, product_in.product_code)
    if existing:
        raise HTTPException(status_code=400, detail="product_code ya existe")
    try:
        product = await crud.create_product(db, product_in)
        return product
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Error de integridad en la base de datos")

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)