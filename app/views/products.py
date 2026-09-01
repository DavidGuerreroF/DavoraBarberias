"""
Vista de Productos — CRUD completo con formulario lateral.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from app.core.theme import *
from app.core.widgets import (
    AppButton, LabeledEntry, LabeledCombo, LabeledText,
    AppTable, SearchBar, ask_confirm, show_error, show_info
)
from app.db import crud


class ProductsView(tk.Frame):
    def __init__(self, parent, navigate=None, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self._navigate = navigate
        self._selected_id = None
        self._groups = []
        self._build()
        self.refresh()

    # ──────────────────────────────────────────
    # Layout
    # ──────────────────────────────────────────
    def _build(self):
        # Encabezado
        hdr = tk.Frame(self, bg=BG_DARK, pady=PAD)
        hdr.pack(fill="x", padx=PAD_LG)
        tk.Label(hdr, text="📦  Productos", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=FONT_TITLE).pack(side="left")
        AppButton(hdr, text="＋ Nuevo", command=self._new, style="primary").pack(side="right", padx=4)
        AppButton(hdr, text="🔄 Refrescar", command=self.refresh, style="ghost").pack(side="right", padx=4)

        # Cuerpo: tabla izquierda + panel derecho
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.rowconfigure(1, weight=1)

        # Barra búsqueda + filtro grupo
        top = tk.Frame(body, bg=BG_DARK)
        top.grid(row=0, column=0, sticky="ew", pady=(0, PAD_SM))
        self._search = SearchBar(top, on_search=lambda q: self.refresh(q))
        self._search.pack(side="left")

        tk.Label(top, text="Grupo:", bg=BG_DARK, fg=TEXT_SECONDARY, font=FONT_BODY).pack(side="left", padx=(PAD,4))
        self._combo_filter = ttk.Combobox(top, state="readonly", width=22, font=FONT_BODY)
        self._combo_filter.pack(side="left")
        self._combo_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # Tabla
        cols = [
            ("code",     "Código",        110, "w"),
            ("desc",     "Descripción",   260, "w"),
            ("unit",     "Unidad",         65, "center"),
            ("cost",     "Costo",         100, "e"),
            ("price",    "Precio",        100, "e"),
            ("tax",      "IVA %",          70, "e"),
            ("qty",      "Stock",         100, "e"),
            ("min",      "Mín",            70, "e"),
            ("group",    "Grupo",         130, "w"),
        ]
        self._table = AppTable(body, columns=cols)
        self._table.grid(row=1, column=0, sticky="nsew")
        self._table.bind_double(self._on_select)
        self._table.bind_select(self._on_row_click)

        # Panel formulario (derecha)
        self._panel = tk.Frame(body, bg=BG_CARD, width=310, padx=PAD, pady=PAD)
        self._panel.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(PAD, 0))
        self._panel.grid_propagate(False)
        self._build_form()

    def _build_form(self):
        p = self._panel
        tk.Label(p, text="Detalle del Producto", bg=BG_CARD, fg=ACCENT,
                 font=FONT_HEAD).pack(anchor="w", pady=(0, PAD_SM))

        self._f_code  = LabeledEntry(p, "Código *"); self._f_code.pack(fill="x", pady=2)
        self._f_desc  = LabeledEntry(p, "Descripción *"); self._f_desc.pack(fill="x", pady=2)
        self._f_unit  = LabeledEntry(p, "Unidad"); self._f_unit.set("UND"); self._f_unit.pack(fill="x", pady=2)

        # precios en 2 col
        row1 = tk.Frame(p, bg=BG_CARD); row1.pack(fill="x", pady=2)
        self._f_cost  = LabeledEntry(row1, "Costo", width=120); self._f_cost.pack(side="left", expand=True, fill="x", padx=(0,4))
        self._f_price = LabeledEntry(row1, "Precio", width=120); self._f_price.pack(side="left", expand=True, fill="x")

        row2 = tk.Frame(p, bg=BG_CARD); row2.pack(fill="x", pady=2)
        self._f_p1 = LabeledEntry(row2, "Lista 1", width=90); self._f_p1.pack(side="left", expand=True, fill="x", padx=(0,2))
        self._f_p2 = LabeledEntry(row2, "Lista 2", width=90); self._f_p2.pack(side="left", expand=True, fill="x", padx=(0,2))
        self._f_p3 = LabeledEntry(row2, "Lista 3", width=90); self._f_p3.pack(side="left", expand=True, fill="x")

        row3 = tk.Frame(p, bg=BG_CARD); row3.pack(fill="x", pady=2)
        self._f_tax  = LabeledEntry(row3, "IVA %", width=110); self._f_tax.set("0"); self._f_tax.pack(side="left", expand=True, fill="x", padx=(0,4))
        self._f_ret  = LabeledEntry(row3, "Retención %", width=110); self._f_ret.set("0"); self._f_ret.pack(side="left", expand=True, fill="x")

        row4 = tk.Frame(p, bg=BG_CARD); row4.pack(fill="x", pady=2)
        self._f_min  = LabeledEntry(row4, "Stock Mín", width=110); self._f_min.set("0"); self._f_min.pack(side="left", expand=True, fill="x", padx=(0,4))
        self._f_max  = LabeledEntry(row4, "Stock Máx", width=110); self._f_max.set("0"); self._f_max.pack(side="left", expand=True, fill="x")

        self._f_group = LabeledCombo(p, "Grupo de Inventario"); self._f_group.pack(fill="x", pady=2)

        tk.Frame(p, bg=BG_INPUT, height=1).pack(fill="x", pady=PAD_SM)

        btn_row = tk.Frame(p, bg=BG_CARD); btn_row.pack(fill="x", pady=(4,0))
        AppButton(btn_row, text="💾 Guardar", command=self._save, style="success").pack(side="left", padx=(0,4))
        AppButton(btn_row, text="🗑 Eliminar", command=self._delete, style="danger").pack(side="left", padx=(0,4))
        AppButton(btn_row, text="✖ Limpiar", command=self._clear, style="ghost").pack(side="left")

    # ──────────────────────────────────────────
    # Datos
    # ──────────────────────────────────────────
    def refresh(self, search=""):
        self._groups = crud.get_all_groups()
        group_names = ["(Todos los grupos)"] + [g["name"] for g in self._groups]
        self._combo_filter["values"] = group_names
        if not self._combo_filter.get():
            self._combo_filter.set("(Todos los grupos)")
        self._f_group.set_values([""] + [g["name"] for g in self._groups])

        sel_group = self._combo_filter.get()
        group_id  = None
        for g in self._groups:
            if g["name"] == sel_group:
                group_id = g["id"]
                break

        products = crud.get_all_products(search=search, group_id=group_id)

        def tag(row):
            try:
                qty = float(row.get("current_quantity", 0))
                mn  = float(row.get("min_stock", 0))
                if mn > 0 and qty < mn:
                    return "low"
            except Exception:
                pass
            return None

        rows = []
        for p in products:
            rows.append({
                "code":  p["product_code"],
                "desc":  p["description"],
                "unit":  p["unit"] or "UND",
                "cost":  f"{float(p['cost']):,.2f}",
                "price": f"{float(p['price']):,.2f}",
                "tax":   f"{float(p['tax_percent']):.1f}%",
                "qty":   f"{float(p['current_quantity']):,.4f}",
                "min":   f"{float(p['min_stock']):,.2f}",
                "group": p.get("group_name") or "",
            })
        self._table.load(rows, tag_fn=lambda r: "low" if r == "low" else None)
        # re-tag usando productos directamente
        self._table.clear()
        self._raw_products = products
        for i, p in enumerate(products):
            qty = float(p.get("current_quantity", 0))
            mn  = float(p.get("min_stock", 0))
            tag_val = "low" if (mn > 0 and qty < mn) else ("even" if i % 2 == 0 else "odd")
            vals = (
                p["product_code"],
                p["description"],
                p["unit"] or "UND",
                f"{float(p['cost']):,.2f}",
                f"{float(p['price']):,.2f}",
                f"{float(p['tax_percent']):.1f}%",
                f"{float(p['current_quantity']):,.4f}",
                f"{float(p['min_stock']):,.2f}",
                p.get("group_name") or "",
            )
            self._table.tree.insert("", "end", iid=str(p["id"]), values=vals, tags=(tag_val,))

    def _on_row_click(self):
        sel = self._table.tree.selection()
        if sel:
            pid = int(sel[0])
            self._load_to_form(pid)

    def _on_select(self):
        self._on_row_click()

    def _load_to_form(self, product_id: int):
        self._selected_id = product_id
        p = crud.get_product(product_id)
        if not p:
            return
        self._f_code.set(p["product_code"])
        self._f_desc.set(p["description"])
        self._f_unit.set(p.get("unit") or "UND")
        self._f_cost.set(p["cost"])
        self._f_price.set(p["price"])
        self._f_p1.set(p.get("price_list1") or "")
        self._f_p2.set(p.get("price_list2") or "")
        self._f_p3.set(p.get("price_list3") or "")
        self._f_tax.set(p["tax_percent"])
        self._f_ret.set(p["retention_percent"])
        self._f_min.set(p["min_stock"])
        self._f_max.set(p["max_stock"])
        # grupo
        gname = p.get("group_name") or ""
        self._f_group.set(gname)

    def _new(self):
        self._selected_id = None
        self._clear()
        self._f_code.entry.focus_set()

    def _clear(self):
        self._selected_id = None
        for f in (self._f_code, self._f_desc, self._f_p1, self._f_p2, self._f_p3):
            f.clear()
        self._f_unit.set("UND")
        for f in (self._f_cost, self._f_price, self._f_tax, self._f_ret, self._f_min, self._f_max):
            f.set("0")
        self._f_group.clear()

    def _save(self):
        code = self._f_code.get().strip()
        desc = self._f_desc.get().strip()
        if not code:
            show_error("Error", "El código del producto es obligatorio.")
            return
        if not desc:
            show_error("Error", "La descripción es obligatoria.")
            return

        # Resolver grupo
        gname    = self._f_group.get()
        group_id = None
        for g in self._groups:
            if g["name"] == gname:
                group_id = g["id"]
                break

        data = {
            "product_code":       code,
            "description":        desc,
            "unit":               self._f_unit.get() or "UND",
            "cost":               self._f_cost.get() or 0,
            "price":              self._f_price.get() or 0,
            "price_list1":        self._f_p1.get() or None,
            "price_list2":        self._f_p2.get() or None,
            "price_list3":        self._f_p3.get() or None,
            "tax_percent":        self._f_tax.get() or 0,
            "retention_percent":  self._f_ret.get() or 0,
            "min_stock":          self._f_min.get() or 0,
            "max_stock":          self._f_max.get() or 0,
            "inventory_group_id": group_id,
        }
        try:
            if self._selected_id:
                crud.update_product(self._selected_id, data)
                show_info("Éxito", "Producto actualizado correctamente.")
            else:
                crud.create_product(data)
                show_info("Éxito", "Producto creado correctamente.")
            self._clear()
            self.refresh()
        except Exception as e:
            show_error("Error al guardar", str(e))

    def _delete(self):
        if not self._selected_id:
            show_error("Error", "Seleccione un producto primero.")
            return
        if ask_confirm("Eliminar", "¿Desactivar este producto del inventario?"):
            crud.delete_product(self._selected_id)
            self._clear()
            self.refresh()
