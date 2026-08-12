-- Schema para sistema de inventarios (PostgreSQL)

-- 1) Grupos de inventario
CREATE TABLE inventory_groups (
  id BIGSERIAL PRIMARY KEY,
  group_code VARCHAR(100) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2) Productos
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  product_code VARCHAR(100) NOT NULL UNIQUE,
  description TEXT NOT NULL,
  cost NUMERIC(14,4) NOT NULL DEFAULT 0,                 -- costo promedio o inicial
  price NUMERIC(14,4) NOT NULL DEFAULT 0,                -- precio por defecto
  price_list1 NUMERIC(14,4) DEFAULT NULL,
  price_list2 NUMERIC(14,4) DEFAULT NULL,
  price_list3 NUMERIC(14,4) DEFAULT NULL,
  tax_percent NUMERIC(5,2) DEFAULT 0,                    -- % impuesto
  retention_percent NUMERIC(5,2) DEFAULT 0,              -- % retención
  inventory_group_id BIGINT REFERENCES inventory_groups(id) ON DELETE SET NULL,
  current_quantity NUMERIC(18,4) NOT NULL DEFAULT 0,     -- valor cacheado; fuente real: movimientos
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_products_group ON products(inventory_group_id);

-- 3) Proveedores
CREATE TABLE suppliers (
  id BIGSERIAL PRIMARY KEY,
  supplier_code VARCHAR(100) NOT NULL UNIQUE,
  identification_number VARCHAR(100),
  document_type VARCHAR(50),
  name VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  email VARCHAR(255),
  address TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4) Entradas de inventario (documento principal)
CREATE TABLE inventory_entries (
  id BIGSERIAL PRIMARY KEY,
  entry_number VARCHAR(100) NOT NULL UNIQUE,    -- número de entrada (factura/guía)
  entry_date TIMESTAMPTZ NOT NULL DEFAULT now(),
  supplier_id BIGINT REFERENCES suppliers(id) ON DELETE SET NULL,
  invoice_number VARCHAR(100),
  notes TEXT,
  total_cost NUMERIC(18,4) DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4.1) Items de entrada (líneas)
CREATE TABLE inventory_entry_items (
  id BIGSERIAL PRIMARY KEY,
  entry_id BIGINT NOT NULL REFERENCES inventory_entries(id) ON DELETE CASCADE,
  product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  quantity NUMERIC(18,4) NOT NULL CHECK (quantity >= 0),
  unit_cost NUMERIC(18,4) NOT NULL DEFAULT 0,
  tax_percent NUMERIC(5,2) DEFAULT NULL,
  retention_percent NUMERIC(5,2) DEFAULT NULL,
  total_cost NUMERIC(18,4) GENERATED ALWAYS AS (quantity * unit_cost) STORED,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_entry_items_product ON inventory_entry_items(product_id);
CREATE INDEX idx_entry_items_entry ON inventory_entry_items(entry_id);

-- 5) Salidas de inventario (documento principal)
CREATE TABLE inventory_exits (
  id BIGSERIAL PRIMARY KEY,
  exit_number VARCHAR(100) NOT NULL UNIQUE,
  exit_date TIMESTAMPTZ NOT NULL DEFAULT now(),
  supplier_id BIGINT REFERENCES suppliers(id) ON DELETE SET NULL, -- si aplica; o NULL para salidas internas
  invoice_number VARCHAR(100),
  notes TEXT,
  total_cost NUMERIC(18,4) DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5.1) Items de salida (líneas)
CREATE TABLE inventory_exit_items (
  id BIGSERIAL PRIMARY KEY,
  exit_id BIGINT NOT NULL REFERENCES inventory_exits(id) ON DELETE CASCADE,
  product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  quantity NUMERIC(18,4) NOT NULL CHECK (quantity >= 0),
  unit_cost NUMERIC(18,4) NOT NULL DEFAULT 0,  -- costo aplicado a la salida
  total_cost NUMERIC(18,4) GENERATED ALWAYS AS (quantity * unit_cost) STORED,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_exit_items_product ON inventory_exit_items(product_id);
CREATE INDEX idx_exit_items_exit ON inventory_exit_items(exit_id);

-- 6) Ajustes de inventario (documento principal)
CREATE TABLE inventory_adjustments (
  id BIGSERIAL PRIMARY KEY,
  adjustment_number VARCHAR(100) NOT NULL UNIQUE,
  adjustment_date TIMESTAMPTZ NOT NULL DEFAULT now(),
  reason TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6.1) Items de ajuste (la cantidad puede ser positiva o negativa)
CREATE TABLE inventory_adjustment_items (
  id BIGSERIAL PRIMARY KEY,
  adjustment_id BIGINT NOT NULL REFERENCES inventory_adjustments(id) ON DELETE CASCADE,
  product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  quantity NUMERIC(18,4) NOT NULL,  -- puede ser positivo (sobrante) o negativo (faltante)
  unit_cost NUMERIC(18,4) DEFAULT NULL,
  total_cost NUMERIC(18,4) GENERATED ALWAYS AS (quantity * COALESCE(unit_cost, 0)) STORED,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_adjust_items_product ON inventory_adjustment_items(product_id);
CREATE INDEX idx_adjust_items_adjustment ON inventory_adjustment_items(adjustment_id);

-- 7) Vista unificada de movimientos (entradas positivas, salidas negativas, ajustes según signo)
CREATE OR REPLACE VIEW inventory_movements AS
SELECT
  ('entry-' || ei.id)::TEXT AS movement_id,
  'entry'::TEXT AS movement_type,
  e.id AS document_id,
  e.entry_number AS document_number,
  e.entry_date AS movement_date,
  ei.product_id,
  ei.quantity AS qty_signed,
  ei.unit_cost,
  ei.total_cost,
  e.supplier_id,
  e.invoice_number,
  ei.created_at
FROM inventory_entry_items ei
JOIN inventory_entries e ON ei.entry_id = e.id

UNION ALL

SELECT
  ('exit-' || xi.id)::TEXT AS movement_id,
  'exit'::TEXT AS movement_type,
  x.id AS document_id,
  x.exit_number AS document_number,
  x.exit_date AS movement_date,
  xi.product_id,
  (xi.quantity * -1) AS qty_signed,  -- negativo para salidas
  xi.unit_cost,
  xi.total_cost,
  x.supplier_id,
  x.invoice_number,
  xi.created_at
FROM inventory_exit_items xi
JOIN inventory_exits x ON xi.exit_id = x.id

UNION ALL

SELECT
  ('adjust-' || ai.id)::TEXT AS movement_id,
  'adjustment'::TEXT AS movement_type,
  a.id AS document_id,
  a.adjustment_number AS document_number,
  a.adjustment_date AS movement_date,
  ai.product_id,
  ai.quantity AS qty_signed,          -- ya tiene signo
  ai.unit_cost,
  ai.total_cost,
  NULL::BIGINT AS supplier_id,
  NULL::VARCHAR AS invoice_number,
  ai.created_at
FROM inventory_adjustment_items ai
JOIN inventory_adjustments a ON ai.adjustment_id = a.id
;

-- 8) Kardex (saldo acumulado por producto). Ordena por fecha y por created_at para estabilidad.
-- Nota: Este view calcula el saldo acumulado en el orden cronológico de movimientos.
CREATE OR REPLACE VIEW inventory_kardex AS
SELECT
  m.*,
  SUM(m.qty_signed) OVER (
    PARTITION BY m.product_id
    ORDER BY m.movement_date, m.created_at, m.movement_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_balance
FROM inventory_movements m
ORDER BY product_id, movement_date, created_at;

-- 9) Vista: Catálogo de referencias (resumen por producto)
-- Campos: product_code, description, cantidad_disponible, ultimo_costo, price_list1/2/3, grupo
CREATE OR REPLACE VIEW catalog_references AS
SELECT
  p.product_code,
  p.description,
  COALESCE(SUM(m.qty_signed), 0) AS cantidad_disponible,
  (  -- último costo: busca la última entrada donde haya unit_cost registrado
    SELECT ie.unit_cost
    FROM inventory_entry_items ie
    JOIN inventory_entries e ON ie.entry_id = e.id
    WHERE ie.product_id = p.id
      AND ie.unit_cost IS NOT NULL
    ORDER BY e.entry_date DESC, ie.id DESC
    LIMIT 1
  ) AS ultimo_costo,
  p.price_list1,
  p.price_list2,
  p.price_list3,
  ig.group_code AS grupo_codigo,
  ig.name AS grupo_nombre
FROM products p
LEFT JOIN inventory_movements m ON p.id = m.product_id
LEFT JOIN inventory_groups ig ON p.inventory_group_id = ig.id
GROUP BY p.id, ig.group_code, ig.name, p.price_list1, p.price_list2, p.price_list3;

-- 10) Vistas catálogo simples
CREATE OR REPLACE VIEW catalog_providers AS
SELECT id AS provider_id, supplier_code, identification_number, document_type, name, phone, email, address
FROM suppliers
ORDER BY name;

CREATE OR REPLACE VIEW catalog_entries AS
SELECT
  e.id,
  e.entry_number,
  e.entry_date,
  e.supplier_id,
  s.name AS supplier_name,
  e.invoice_number,
  e.total_cost
FROM inventory_entries e
LEFT JOIN suppliers s ON e.supplier_id = s.id
ORDER BY e.entry_date DESC;

CREATE OR REPLACE VIEW catalog_exits AS
SELECT
  x.id,
  x.exit_number,
  x.exit_date,
  x.supplier_id,
  s.name AS supplier_name,
  x.invoice_number,
  x.total_cost
FROM inventory_exits x
LEFT JOIN suppliers s ON x.supplier_id = s.id
ORDER BY x.exit_date DESC;

CREATE OR REPLACE VIEW catalog_adjustments AS
SELECT
  a.id,
  a.adjustment_number,
  a.adjustment_date,
  a.reason,
  a.notes
FROM inventory_adjustments a
ORDER BY a.adjustment_date DESC;

-- 11) Utilidades / constraints adicionales
-- Evitar números duplicados vacíos
ALTER TABLE inventory_entries
  ADD CONSTRAINT entry_number_not_empty CHECK (length(trim(entry_number)) > 0);

ALTER TABLE inventory_exits
  ADD CONSTRAINT exit_number_not_empty CHECK (length(trim(exit_number)) > 0);

ALTER TABLE inventory_adjustments
  ADD CONSTRAINT adjustment_number_not_empty CHECK (length(trim(adjustment_number)) > 0);

-- 12) Triggers recomendados (comentado): 
-- Es recomendable crear triggers para:
--  - Actualizar products.current_quantity al insertar/actualizar/eliminar items de entrada/salida/ajuste.
--  - Actualizar products.updated_at a NOW() cuando se cambia product.
-- Por ahora no se incluyen para que decidas la lógica (FIFO/LIFO/promedio) si quieres manejar costos y stock automáticamente.

-- Fin del esquema