"""
CRUD completo para todas las entidades del sistema de inventarios.
Usa sqlite3 nativo con Row factory.
"""

import sqlite3
from datetime import datetime
from .database import get_connection


# ─────────────────────────────────────────────
# GRUPOS DE INVENTARIO
# ─────────────────────────────────────────────

def get_all_groups():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM inventory_groups ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_group(group_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM inventory_groups WHERE id=?", (group_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_group(group_code: str, name: str, description: str = ""):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO inventory_groups (group_code, name, description) VALUES (?,?,?)",
        (group_code.strip().upper(), name.strip(), description.strip())
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def update_group(group_id: int, group_code: str, name: str, description: str = ""):
    conn = get_connection()
    conn.execute(
        "UPDATE inventory_groups SET group_code=?, name=?, description=? WHERE id=?",
        (group_code.strip().upper(), name.strip(), description.strip(), group_id)
    )
    conn.commit()
    conn.close()

def delete_group(group_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM inventory_groups WHERE id=?", (group_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# PROVEEDORES
# ─────────────────────────────────────────────

def get_all_suppliers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_supplier(supplier_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM suppliers WHERE id=?", (supplier_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_supplier(data: dict):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO suppliers
           (supplier_code, identification_number, document_type, name, phone, email, address)
           VALUES (?,?,?,?,?,?,?)""",
        (
            data.get("supplier_code","").strip().upper(),
            data.get("identification_number",""),
            data.get("document_type",""),
            data.get("name","").strip(),
            data.get("phone",""),
            data.get("email",""),
            data.get("address",""),
        )
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def update_supplier(supplier_id: int, data: dict):
    conn = get_connection()
    conn.execute(
        """UPDATE suppliers SET
           supplier_code=?, identification_number=?, document_type=?,
           name=?, phone=?, email=?, address=?,
           updated_at=datetime('now','localtime')
           WHERE id=?""",
        (
            data.get("supplier_code","").strip().upper(),
            data.get("identification_number",""),
            data.get("document_type",""),
            data.get("name","").strip(),
            data.get("phone",""),
            data.get("email",""),
            data.get("address",""),
            supplier_id
        )
    )
    conn.commit()
    conn.close()

def delete_supplier(supplier_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# PRODUCTOS
# ─────────────────────────────────────────────

def get_all_products(search: str = "", group_id: int = None, active_only: bool = True):
    conn = get_connection()
    sql = """
        SELECT p.*, ig.name AS group_name
        FROM products p
        LEFT JOIN inventory_groups ig ON p.inventory_group_id = ig.id
        WHERE 1=1
    """
    params = []
    if active_only:
        sql += " AND p.active = 1"
    if search:
        sql += " AND (p.product_code LIKE ? OR p.description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if group_id:
        sql += " AND p.inventory_group_id = ?"
        params.append(group_id)
    sql += " ORDER BY p.description"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_product(product_id: int):
    conn = get_connection()
    row = conn.execute(
        """SELECT p.*, ig.name AS group_name
           FROM products p
           LEFT JOIN inventory_groups ig ON p.inventory_group_id = ig.id
           WHERE p.id=?""",
        (product_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def get_product_by_code(code: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE product_code=?", (code.strip().upper(),)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_product(data: dict):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO products
           (product_code, description, unit, cost, price,
            price_list1, price_list2, price_list3,
            tax_percent, retention_percent,
            min_stock, max_stock, inventory_group_id)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            data.get("product_code","").strip().upper(),
            data.get("description","").strip(),
            data.get("unit","UND"),
            float(data.get("cost", 0)),
            float(data.get("price", 0)),
            _fnone(data.get("price_list1")),
            _fnone(data.get("price_list2")),
            _fnone(data.get("price_list3")),
            float(data.get("tax_percent", 0)),
            float(data.get("retention_percent", 0)),
            float(data.get("min_stock", 0)),
            float(data.get("max_stock", 0)),
            data.get("inventory_group_id") or None,
        )
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def update_product(product_id: int, data: dict):
    conn = get_connection()
    conn.execute(
        """UPDATE products SET
           product_code=?, description=?, unit=?,
           cost=?, price=?,
           price_list1=?, price_list2=?, price_list3=?,
           tax_percent=?, retention_percent=?,
           min_stock=?, max_stock=?,
           inventory_group_id=?,
           updated_at=datetime('now','localtime')
           WHERE id=?""",
        (
            data.get("product_code","").strip().upper(),
            data.get("description","").strip(),
            data.get("unit","UND"),
            float(data.get("cost", 0)),
            float(data.get("price", 0)),
            _fnone(data.get("price_list1")),
            _fnone(data.get("price_list2")),
            _fnone(data.get("price_list3")),
            float(data.get("tax_percent", 0)),
            float(data.get("retention_percent", 0)),
            float(data.get("min_stock", 0)),
            float(data.get("max_stock", 0)),
            data.get("inventory_group_id") or None,
            product_id
        )
    )
    conn.commit()
    conn.close()

def delete_product(product_id: int):
    conn = get_connection()
    # soft delete
    conn.execute("UPDATE products SET active=0 WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

def _update_product_quantity(conn: sqlite3.Connection, product_id: int):
    """Recalcula current_quantity desde movimientos."""
    row = conn.execute(
        """SELECT COALESCE(SUM(q),0) FROM (
            SELECT SUM(quantity) AS q FROM inventory_entry_items WHERE product_id=?
            UNION ALL
            SELECT -SUM(quantity) AS q FROM inventory_exit_items WHERE product_id=?
            UNION ALL
            SELECT SUM(quantity) AS q FROM inventory_adjustment_items WHERE product_id=?
        )""",
        (product_id, product_id, product_id)
    ).fetchone()
    qty = row[0] if row else 0
    conn.execute("UPDATE products SET current_quantity=? WHERE id=?", (qty, product_id))


# ─────────────────────────────────────────────
# ENTRADAS DE INVENTARIO
# ─────────────────────────────────────────────

def get_all_entries(search: str = ""):
    conn = get_connection()
    sql = """
        SELECT e.*, s.name AS supplier_name
        FROM inventory_entries e
        LEFT JOIN suppliers s ON e.supplier_id = s.id
        WHERE 1=1
    """
    params = []
    if search:
        sql += " AND (e.entry_number LIKE ? OR e.invoice_number LIKE ? OR s.name LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    sql += " ORDER BY e.entry_date DESC, e.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_entry(entry_id: int):
    conn = get_connection()
    row = conn.execute(
        """SELECT e.*, s.name AS supplier_name
           FROM inventory_entries e
           LEFT JOIN suppliers s ON e.supplier_id = s.id
           WHERE e.id=?""",
        (entry_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def get_entry_items(entry_id: int):
    conn = get_connection()
    rows = conn.execute(
        """SELECT ei.*, p.product_code, p.description AS product_description, p.unit
           FROM inventory_entry_items ei
           JOIN products p ON ei.product_id = p.id
           WHERE ei.entry_id=?""",
        (entry_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_entry(header: dict, items: list):
    """Crea una entrada y sus ítems. Actualiza stock."""
    conn = get_connection()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute(
            """INSERT INTO inventory_entries
               (entry_number, entry_date, supplier_id, invoice_number, notes)
               VALUES (?,?,?,?,?)""",
            (
                header["entry_number"].strip(),
                header.get("entry_date", datetime.now().strftime("%Y-%m-%d")),
                header.get("supplier_id") or None,
                header.get("invoice_number",""),
                header.get("notes",""),
            )
        )
        entry_id = cur.lastrowid
        total = 0.0
        for it in items:
            qty   = float(it["quantity"])
            cost  = float(it["unit_cost"])
            tc    = round(qty * cost, 4)
            total += tc
            conn.execute(
                """INSERT INTO inventory_entry_items
                   (entry_id, product_id, quantity, unit_cost, tax_percent, retention_percent, total_cost)
                   VALUES (?,?,?,?,?,?,?)""",
                (entry_id, it["product_id"], qty, cost,
                 float(it.get("tax_percent",0)), float(it.get("retention_percent",0)), tc)
            )
            _update_product_quantity(conn, it["product_id"])
        conn.execute("UPDATE inventory_entries SET total_cost=? WHERE id=?", (total, entry_id))
        conn.commit()
        return entry_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_entry(entry_id: int):
    """Elimina entrada y revierte stock."""
    conn = get_connection()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        items = conn.execute(
            "SELECT product_id FROM inventory_entry_items WHERE entry_id=?", (entry_id,)
        ).fetchall()
        conn.execute("DELETE FROM inventory_entries WHERE id=?", (entry_id,))
        for it in items:
            _update_product_quantity(conn, it["product_id"])
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_next_entry_number():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) FROM inventory_entries").fetchone()
    conn.close()
    n = (row[0] if row else 0) + 1
    return f"ENT-{n:06d}"


# ─────────────────────────────────────────────
# SALIDAS DE INVENTARIO
# ─────────────────────────────────────────────

def get_all_exits(search: str = ""):
    conn = get_connection()
    sql = """
        SELECT * FROM inventory_exits
        WHERE 1=1
    """
    params = []
    if search:
        sql += " AND (exit_number LIKE ? OR invoice_number LIKE ? OR client_name LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    sql += " ORDER BY exit_date DESC, id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_exit(exit_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM inventory_exits WHERE id=?", (exit_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_exit_items(exit_id: int):
    conn = get_connection()
    rows = conn.execute(
        """SELECT xi.*, p.product_code, p.description AS product_description, p.unit
           FROM inventory_exit_items xi
           JOIN products p ON xi.product_id = p.id
           WHERE xi.exit_id=?""",
        (exit_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_exit(header: dict, items: list):
    conn = get_connection()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        # Verificar stock disponible
        for it in items:
            row = conn.execute(
                "SELECT current_quantity, description FROM products WHERE id=?",
                (it["product_id"],)
            ).fetchone()
            if row and float(row["current_quantity"]) < float(it["quantity"]):
                raise ValueError(
                    f"Stock insuficiente para '{row['description']}': "
                    f"disponible={row['current_quantity']}, solicitado={it['quantity']}"
                )
        cur = conn.execute(
            """INSERT INTO inventory_exits
               (exit_number, exit_date, client_name, invoice_number, notes)
               VALUES (?,?,?,?,?)""",
            (
                header["exit_number"].strip(),
                header.get("exit_date", datetime.now().strftime("%Y-%m-%d")),
                header.get("client_name",""),
                header.get("invoice_number",""),
                header.get("notes",""),
            )
        )
        exit_id = cur.lastrowid
        total = 0.0
        for it in items:
            qty   = float(it["quantity"])
            cost  = float(it.get("unit_cost", 0))
            price = float(it.get("unit_price", 0))
            tc    = round(qty * cost, 4)
            total += tc
            conn.execute(
                """INSERT INTO inventory_exit_items
                   (exit_id, product_id, quantity, unit_cost, unit_price, total_cost)
                   VALUES (?,?,?,?,?,?)""",
                (exit_id, it["product_id"], qty, cost, price, tc)
            )
            _update_product_quantity(conn, it["product_id"])
        conn.execute("UPDATE inventory_exits SET total_cost=? WHERE id=?", (total, exit_id))
        conn.commit()
        return exit_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_exit(exit_id: int):
    conn = get_connection()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        items = conn.execute(
            "SELECT product_id FROM inventory_exit_items WHERE exit_id=?", (exit_id,)
        ).fetchall()
        conn.execute("DELETE FROM inventory_exits WHERE id=?", (exit_id,))
        for it in items:
            _update_product_quantity(conn, it["product_id"])
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_next_exit_number():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) FROM inventory_exits").fetchone()
    conn.close()
    n = (row[0] if row else 0) + 1
    return f"SAL-{n:06d}"


# ─────────────────────────────────────────────
# AJUSTES DE INVENTARIO
# ─────────────────────────────────────────────

def get_all_adjustments(search: str = ""):
    conn = get_connection()
    sql = "SELECT * FROM inventory_adjustments WHERE 1=1"
    params = []
    if search:
        sql += " AND (adjustment_number LIKE ? OR reason LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    sql += " ORDER BY adjustment_date DESC, id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_adjustment(adj_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM inventory_adjustments WHERE id=?", (adj_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_adjustment_items(adj_id: int):
    conn = get_connection()
    rows = conn.execute(
        """SELECT ai.*, p.product_code, p.description AS product_description, p.unit
           FROM inventory_adjustment_items ai
           JOIN products p ON ai.product_id = p.id
           WHERE ai.adjustment_id=?""",
        (adj_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_adjustment(header: dict, items: list):
    conn = get_connection()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute(
            """INSERT INTO inventory_adjustments
               (adjustment_number, adjustment_date, reason, notes)
               VALUES (?,?,?,?)""",
            (
                header["adjustment_number"].strip(),
                header.get("adjustment_date", datetime.now().strftime("%Y-%m-%d")),
                header.get("reason",""),
                header.get("notes",""),
            )
        )
        adj_id = cur.lastrowid
        for it in items:
            qty  = float(it["quantity"])
            cost = float(it.get("unit_cost", 0))
            tc   = round(qty * cost, 4)
            conn.execute(
                """INSERT INTO inventory_adjustment_items
                   (adjustment_id, product_id, quantity, unit_cost, total_cost, notes)
                   VALUES (?,?,?,?,?,?)""",
                (adj_id, it["product_id"], qty, cost, tc, it.get("notes",""))
            )
            _update_product_quantity(conn, it["product_id"])
        conn.commit()
        return adj_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_adjustment(adj_id: int):
    conn = get_connection()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        items = conn.execute(
            "SELECT product_id FROM inventory_adjustment_items WHERE adjustment_id=?", (adj_id,)
        ).fetchall()
        conn.execute("DELETE FROM inventory_adjustments WHERE id=?", (adj_id,))
        for it in items:
            _update_product_quantity(conn, it["product_id"])
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_next_adjustment_number():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) FROM inventory_adjustments").fetchone()
    conn.close()
    n = (row[0] if row else 0) + 1
    return f"AJU-{n:06d}"


# ─────────────────────────────────────────────
# KARDEX / MOVIMIENTOS
# ─────────────────────────────────────────────

def get_kardex(product_id: int = None, date_from: str = None, date_to: str = None):
    conn = get_connection()
    sql = """
        SELECT * FROM (
            SELECT
                'ENTRADA'               AS tipo,
                e.entry_number          AS documento,
                e.entry_date            AS fecha,
                p.product_code,
                p.description           AS producto,
                ei.quantity             AS entrada,
                0.0                     AS salida,
                0.0                     AS ajuste,
                ei.unit_cost            AS costo_unit,
                ei.total_cost           AS total,
                s.name                  AS contraparte,
                ei.product_id,
                ei.created_at
            FROM inventory_entry_items ei
            JOIN inventory_entries e ON ei.entry_id = e.id
            JOIN products p ON ei.product_id = p.id
            LEFT JOIN suppliers s ON e.supplier_id = s.id

            UNION ALL

            SELECT
                'SALIDA'                AS tipo,
                x.exit_number          AS documento,
                x.exit_date            AS fecha,
                p.product_code,
                p.description          AS producto,
                0.0                    AS entrada,
                xi.quantity            AS salida,
                0.0                    AS ajuste,
                xi.unit_cost           AS costo_unit,
                xi.total_cost          AS total,
                x.client_name          AS contraparte,
                xi.product_id,
                xi.created_at
            FROM inventory_exit_items xi
            JOIN inventory_exits x ON xi.exit_id = x.id
            JOIN products p ON xi.product_id = p.id

            UNION ALL

            SELECT
                'AJUSTE'               AS tipo,
                a.adjustment_number    AS documento,
                a.adjustment_date      AS fecha,
                p.product_code,
                p.description          AS producto,
                CASE WHEN ai.quantity>0 THEN ai.quantity ELSE 0 END  AS entrada,
                CASE WHEN ai.quantity<0 THEN ABS(ai.quantity) ELSE 0 END AS salida,
                ai.quantity            AS ajuste,
                ai.unit_cost           AS costo_unit,
                ai.total_cost          AS total,
                a.reason               AS contraparte,
                ai.product_id,
                ai.created_at
            FROM inventory_adjustment_items ai
            JOIN inventory_adjustments a ON ai.adjustment_id = a.id
            JOIN products p ON ai.product_id = p.id
        ) m
        WHERE 1=1
    """
    params = []
    if product_id:
        sql += " AND product_id=?"
        params.append(product_id)
    if date_from:
        sql += " AND fecha >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND fecha <= ?"
        params.append(date_to)
    sql += " ORDER BY fecha ASC, created_at ASC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────
# DASHBOARD / KPIs
# ─────────────────────────────────────────────

def get_dashboard_kpis():
    conn = get_connection()
    kpis = {}

    kpis["total_products"]   = conn.execute("SELECT COUNT(*) FROM products WHERE active=1").fetchone()[0]
    kpis["total_suppliers"]  = conn.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0]
    kpis["total_groups"]     = conn.execute("SELECT COUNT(*) FROM inventory_groups").fetchone()[0]

    val = conn.execute(
        "SELECT COALESCE(SUM(current_quantity * cost),0) FROM products WHERE active=1"
    ).fetchone()[0]
    kpis["stock_value"] = round(float(val), 2)

    kpis["entries_today"] = conn.execute(
        "SELECT COUNT(*) FROM inventory_entries WHERE entry_date=date('now','localtime')"
    ).fetchone()[0]
    kpis["exits_today"] = conn.execute(
        "SELECT COUNT(*) FROM inventory_exits WHERE exit_date=date('now','localtime')"
    ).fetchone()[0]

    # Productos bajo mínimo
    low = conn.execute(
        "SELECT COUNT(*) FROM products WHERE active=1 AND min_stock>0 AND current_quantity < min_stock"
    ).fetchone()[0]
    kpis["low_stock_count"] = low

    # Top 5 productos con mayor valor en stock
    top = conn.execute(
        """SELECT description, current_quantity, cost,
                  current_quantity*cost AS valor
           FROM products WHERE active=1
           ORDER BY valor DESC LIMIT 5"""
    ).fetchall()
    kpis["top_products"] = [dict(r) for r in top]

    # Últimas 5 entradas
    last_entries = conn.execute(
        """SELECT e.entry_number, e.entry_date, s.name AS supplier, e.total_cost
           FROM inventory_entries e
           LEFT JOIN suppliers s ON e.supplier_id = s.id
           ORDER BY e.entry_date DESC, e.id DESC LIMIT 5"""
    ).fetchall()
    kpis["last_entries"] = [dict(r) for r in last_entries]

    # Últimas 5 salidas
    last_exits = conn.execute(
        """SELECT exit_number, exit_date, client_name, total_cost
           FROM inventory_exits
           ORDER BY exit_date DESC, id DESC LIMIT 5"""
    ).fetchall()
    kpis["last_exits"] = [dict(r) for r in last_exits]

    conn.close()
    return kpis


def _fnone(val):
    """Convierte vacío/None a None, sino float."""
    if val is None or str(val).strip() == "":
        return None
    try:
        return float(val)
    except Exception:
        return None
