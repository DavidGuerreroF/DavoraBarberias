import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/davora_inventario")

# Crear engine async
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base para modelos
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency para obtener sesión de BD en rutas."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Inicializa la base de datos creando todas las tablas."""
    async with engine.begin() as conn:
        # Ejecutar Schema.sql
        with open("Schema.sql", "r") as f:
            schema_sql = f.read()
        # Dividir por ; y ejecutar cada statement
        statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
        for stmt in statements:
            try:
                await conn.execute(stmt)
                print(f"✓ Ejecutado: {stmt[:50]}...")
            except Exception as e:
                print(f"⚠ Error en statement: {e}")
        
        print("✓ Base de datos inicializada correctamente")


async def close_db():
    """Cierra la conexión con la base de datos."""
    await engine.dispose()
