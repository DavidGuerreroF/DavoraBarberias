"""
Módulo de base de datos SQLite para el sistema de inventarios.
Compatible con DB Browser for SQLite.
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "inventario.db"


def get_connection() -> sqlite3.Connection:
    """Retorna una conexión a SQLite con foreign keys habilitadas."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db():
    """Crea todas las tablas si no existen."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    -- Grupos de inventario
    CREATE TABLE IF NOT EXISTS inventory_groups (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        group_code  TEXT NOT NULL UNIQUE,
        name        TEXT NOT NULL,
        description TEXT,
        created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );

    -- Proveedores
    CREATE TABLE IF NOT EXISTS suppliers (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_code         TEXT NOT NULL UNIQUE,
        identification_number TEXT,
        document_type         TEXT,
        name                  TEXT NOT NULL,
        phone                 TEXT,
        email                 TEXT,
        address               TEXT,
        created_at            TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        updated_at            TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );

    -- Productos
    CREATE TABLE IF NOT EXISTS products (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        product_code        TEXT NOT NULL UNIQUE,
        description         TEXT NOT NULL,
        unit                TEXT DEFAULT 'UND',
        cost                REAL NOT NULL DEFAULT 0,
        price               REAL NOT NULL DEFAULT 0,
        price_list1         REAL DEFAULT NULL,
        price_list2         REAL DEFAULT NULL,
        price_list3         REAL DEFAULT NULL,
        tax_percent         REAL DEFAULT 0,
        retention_percent   REAL DEFAULT 0,
        min_stock           REAL DEFAULT 0,
        max_stock           REAL DEFAULT 0,
        inventory_group_id  INTEGER REFERENCES inventory_groups(id) ON DELETE SET NULL,
        current_quantity    REAL NOT NULL DEFAULT 0,
        active              INTEGER NOT NULL DEFAULT 1,
        created_at          TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        updated_at          TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE INDEX IF NOT EXISTS idx_products_group ON products(inventory_group_id);
    CREATE INDEX IF NOT EXISTS idx_products_code  ON products(product_code);

    -- Entradas de inventario
    CREATE TABLE IF NOT EXISTS inventory_entries (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_number   TEXT NOT NULL UNIQUE,
        entry_date     TEXT NOT NULL DEFAULT (date('now','localtime')),
        supplier_id    INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
        invoice_number TEXT,
        notes          TEXT,
        status         TEXT NOT NULL DEFAULT 'confirmed',
        total_cost     REAL DEFAULT 0,
        created_at     TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS inventory_entry_items (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id          INTEGER NOT NULL REFERENCES inventory_entries(id) ON DELETE CASCADE,
        product_id        INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
        quantity          REAL NOT NULL CHECK (quantity > 0),
        unit_cost         REAL NOT NULL DEFAULT 0,
        tax_percent       REAL DEFAULT 0,
        retention_percent REAL DEFAULT 0,
        total_cost        REAL DEFAULT 0,
        created_at        TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE INDEX IF NOT EXISTS idx_entry_items_product ON inventory_entry_items(product_id);
    CREATE INDEX IF NOT EXISTS idx_entry_items_entry   ON inventory_entry_items(entry_id);

    -- Salidas de inventario
    CREATE TABLE IF NOT EXISTS inventory_exits (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        exit_number    TEXT NOT NULL UNIQUE,
        exit_date      TEXT NOT NULL DEFAULT (date('now','localtime')),
        client_name    TEXT,
        invoice_number TEXT,
        notes          TEXT,
        status         TEXT NOT NULL DEFAULT 'confirmed',
        total_cost     REAL DEFAULT 0,
        created_at     TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS inventory_exit_items (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        exit_id    INTEGER NOT NULL REFERENCES inventory_exits(id) ON DELETE CASCADE,
        product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
        quantity   REAL NOT NULL CHECK (quantity > 0),
        unit_cost  REAL NOT NULL DEFAULT 0,
        unit_price REAL NOT NULL DEFAULT 0,
        total_cost REAL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE INDEX IF NOT EXISTS idx_exit_items_product ON inventory_exit_items(product_id);
    CREATE INDEX IF NOT EXISTS idx_exit_items_exit    ON inventory_exit_items(exit_id);

    -- Ajustes de inventario
    CREATE TABLE IF NOT EXISTS inventory_adjustments (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        adjustment_number TEXT NOT NULL UNIQUE,
        adjustment_date   TEXT NOT NULL DEFAULT (date('now','localtime')),
        reason            TEXT,
        notes             TEXT,
        created_at        TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS inventory_adjustment_items (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        adjustment_id INTEGER NOT NULL REFERENCES inventory_adjustments(id) ON DELETE CASCADE,
        product_id    INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
        quantity      REAL NOT NULL,
        unit_cost     REAL DEFAULT 0,
        total_cost    REAL DEFAULT 0,
        notes         TEXT,
        created_at    TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE INDEX IF NOT EXISTS idx_adj_items_product    ON inventory_adjustment_items(product_id);
    CREATE INDEX IF NOT EXISTS idx_adj_items_adjustment ON inventory_adjustment_items(adjustment_id);
    """)

    conn.commit()
    conn.close()
    print(f"[DB] Base de datos inicializada: {DB_PATH}")
