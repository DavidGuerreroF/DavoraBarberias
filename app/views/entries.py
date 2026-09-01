"""
Vista de Entradas de Inventario — cabecera + ítems con búsqueda de producto.
"""

import tkinter as tk
from tkinter import ttk
from datetime import date
from app.core.theme import *
from app.core.widgets import (
    AppButton, LabeledEntry, LabeledCombo, LabeledText,
    AppTable, SearchBar, ask_confirm, show_error, show_info
)
from app.db import crud


class EntriesView(tk.Frame):
    def __init__(self, parent, navigate=None, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self._navigate  = navigate
        self._selected_id = None
        self._suppliers = []
        self._items_buffer = []   # lista de dicts mientras se edita
        self._build()
        self.refresh()

    # ────────────────────────────────────────────
    # Layout principal: lista arriba, formulario abajo
    # ────────────────────────────────────────────
    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG_DARK, pady=PAD)
        hdr.pack(fill="x", padx=PAD_LG)
        tk.Label(hdr, text="⬇️  Entradas de Inventario", bg=BG_DARK,
                 fg=TEXT_PRIMARY, font=FONT_TITLE).pack(side="left")
        AppButton(hdr, text="＋ Nueva Entrada", command=self._new,
                  style="primary").pack(side="right", padx=4)
        AppButton(hdr, text="🔄 Refrescar", command=self.refresh,
                  style="ghost").pack(side="right", padx=4)

        # PanedWindow vertical: lista arriba / formulario abajo
        paned = tk.PanedWindow(self, orient="vertical", bg=BG_DARK,
                               sashwidth=6, sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD))

        # ── Panel Superior: lista de entradas ──
        top_frame = tk.Frame(paned, bg=BG_DARK)
        paned.add(top_frame, minsize=160)

        search_row = tk.Frame(top_frame, bg=BG_DARK)
        search_row.pack(fill="x", pady=(0, PAD_SM))
        SearchBar(search_row, on_search=lambda q: self.refresh(q)).pack(side="left")

        list_cols = [
            ("num",      "N° Entrada",  120, "w"),
            ("date",     "Fecha",        90, "center"),
            ("supplier", "Proveedor",   200, "w"),
            ("invoice",  "Factura",     110, "w"),
            ("total",    "Total Costo", 120, "e"),
            ("notes",    "Notas",       220, "w"),
        ]
        self._list_table = AppTable(top_frame, columns=list_cols)
        self._list_table.pack(fill="both", expand=True)
        self._list_table.bind_double(self._on_list_select)
        self._list_table.bind_select(self._on_list_click)

        # ── Panel Inferior: formulario de edición ──
        bot_frame = tk.Frame(paned, bg=BG_CARD)
        paned.add(bot_frame, minsize=280)

        self._build_form(bot_frame)

    def _build_form(self, parent):
        # Título + botones de acción
        top = tk.Frame(parent, bg=BG_CARD, pady=PAD_SM, padx=PAD)
        top.pack(fill="x")
        tk.Label(top, text="Documento de Entrada", bg=BG_CARD,
                 fg=ACCENT, font=FONT_HEAD).pack(side="left")
        AppButton(top, text="💾 Confirmar Entrada", command=self._save,
                  style="success").pack(side="right", padx=(4,0))
        AppButton(top, text="🗑 Eliminar",  command=self._delete,
                  style="danger").pack(side="right", padx=4)
        AppButton(top, text="✖ Cancelar",  command=self._cancel,
                  style="ghost").pack(side="right", padx=4)

        tk.Frame(parent, bg=BG_INPUT, height=1).pack(fill="x")

        # Campos cabecera
        hdr_frame = tk.Frame(parent, bg=BG_CARD, padx=PAD, pady=PAD_SM)
        hdr_frame.pack(fill="x")

        self._f_num     = LabeledEntry(hdr_frame, "N° Entrada *", width=130)
        self._f_num.grid(row=0, column=0, sticky="ew", padx=(0,PAD_SM))
        self._f_date    = LabeledEntry(hdr_frame, "Fecha (YYYY-MM-DD)", width=130)
        self._f_date.set(date.today().isoformat())
        self._f_date.grid(row=0, column=1, sticky="ew", padx=(0,PAD_SM))
        self._f_invoice = LabeledEntry(hdr_frame, "N° Factura", width=130)
        self._f_invoice.grid(row=0, column=2, sticky="ew", padx=(0,PAD_SM))
        self._f_supplier = LabeledCombo(hdr_frame, "Proveedor", width=26)
        self._f_supplier.grid(row=0, column=3, sticky="ew", padx=(0,PAD_SM))
        self._f_notes = LabeledEntry(hdr_frame, "Notas", width=200)
        self._f_notes.grid(row=0, column=4, sticky="ew")
        for c in range(5):
            hdr_frame.columnconfigure(c, weight=1)

        # ── Línea de adición de productos ──
        add_row = tk.Frame(parent, bg=BG_SIDEBAR, padx=PAD, pady=PAD_SM)
        add_row.pack(fill="x")
        tk.Label(add_row, text="Añadir producto:", bg=BG_SIDEBAR,
                 fg=TEXT_SECONDARY, font=FONT_SMALL).pack(side="left", padx=(0,4))

        self._add_code = tk.Entry(add_row, bg=BG_INPUT, fg=TEXT_PRIMARY,
                                  insertbackground=TEXT_PRIMARY,
                                  font=FONT_BODY, relief="flat", width=16)
        self._add_code.pack(side="left", ipady=4, padx=(0,4))
        self._add_code.bind("<Return>", lambda e: self._lookup_product())
        self._lbl_prod = tk.Label(add_row, text="—", bg=BG_SIDEBAR,
                                  fg=TEXT_SECONDARY, font=FONT_SMALL, width=30, anchor="w")
        self._lbl_prod.pack(side="left", padx=(0,PAD_SM))

        tk.Label(add_row, text="Cant:", bg=BG_SIDEBAR, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).pack(side="left")
        self._add_qty = tk.Entry(add_row, bg=BG_INPUT, fg=TEXT_PRIMARY,
                                 insertbackground=TEXT_PRIMARY,
                                 font=FONT_BODY, relief="flat", width=8)
        self._add_qty.pack(side="left", ipady=4, padx=(4,4))

        tk.Label(add_row, text="Costo u.:", bg=BG_SIDEBAR, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).pack(side="left")
        self._add_cost = tk.Entry(add_row, bg=BG_INPUT, fg=TEXT_PRIMARY,
                                  insertbackground=TEXT_PRIMARY,
                                  font=FONT_BODY, relief="flat", width=10)
        self._add_cost.pack(side="left", ipady=4, padx=(4,4))

        tk.Label(add_row, text="IVA%:", bg=BG_SIDEBAR, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).pack(side="left")
        self._add_tax = tk.Entry(add_row, bg=BG_INPUT, fg=TEXT_PRIMARY,
                                 insertbackground=TEXT_PRIMARY,
                                 font=FONT_BODY, relief="flat", width=6)
        self._add_tax.insert(0, "0")
        self._add_tax.pack(side="left", ipady=4, padx=(4,4))

        AppButton(add_row, text="➕ Agregar", command=self._add_item,
                  style="primary").pack(side="left", padx=(4,0))
        AppButton(add_row, text="🔎 Buscar", command=self._open_product_picker,
                  style="ghost").pack(side="left", padx=4)

        # Tabla de ítems del documento
        items_frame = tk.Frame(parent, bg=BG_CARD)
        items_frame.pack(fill="both", expand=True, padx=PAD, pady=(PAD_SM, 0))

        item_cols = [
            ("code",  "Código",      100, "w"),
            ("desc",  "Descripción", 300, "w"),
            ("unit",  "Und",          50, "center"),
            ("qty",   "Cantidad",    100, "e"),
            ("cost",  "Costo Unit",  110, "e"),
            ("tax",   "IVA%",         60, "e"),
            ("total", "Total",       120, "e"),
        ]
        self._items_table = AppTable(items_frame, columns=item_cols)
        self._items_table.pack(fill="both", expand=True)
        self._items_table.bind_double(self._remove_item)

        # Total general
        tot_row = tk.Frame(parent, bg=BG_CARD, padx=PAD, pady=PAD_SM)
        tot_row.pack(fill="x")
        tk.Label(tot_row, text="Total Entrada:", bg=BG_CARD,
                 fg=TEXT_SECONDARY, font=FONT_HEAD).pack(side="right", padx=(0,4))
        self._lbl_total = tk.Label(tot_row, text="$ 0.00", bg=BG_CARD,
                                   fg=SUCCESS, font=("Segoe UI", 14, "bold"))
        self._lbl_total.pack(side="right")
        tk.Label(tot_row, text="(doble clic en ítem para eliminarlo)",
                 bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL).pack(side="left")

        self._current_product = None  # dict del producto seleccionado

    # ────────────────────────────────────────────
    # Acciones de la lista principal
    # ────────────────────────────────────────────
    def refresh(self, search=""):
        self._suppliers = crud.get_all_suppliers()
        self._f_supplier.set_values([""] + [s["name"] for s in self._suppliers])

        entries = crud.get_all_entries(search)
        self._list_table.clear()
        for i, e in enumerate(entries):
            tag = "even" if i % 2 == 0 else "odd"
            self._list_table.tree.insert("", "end", iid=str(e["id"]), tags=(tag,), values=(
                e["entry_number"],
                e.get("entry_date","")[:10],
                e.get("supplier_name","") or "",
                e.get("invoice_number","") or "",
                f"$ {float(e.get('total_cost',0)):,.2f}",
                e.get("notes","") or "",
            ))

    def _on_list_click(self):
        sel = self._list_table.tree.selection()
        if sel:
            self._load_entry(int(sel[0]))

    def _on_list_select(self):
        self._on_list_click()

    def _load_entry(self, entry_id: int):
        self._selected_id = entry_id
        e = crud.get_entry(entry_id)
        if not e: return
        self._f_num.set(e["entry_number"])
        self._f_date.set((e.get("entry_date","") or "")[:10])
        self._f_invoice.set(e.get("invoice_number","") or "")
        self._f_notes.set(e.get("notes","") or "")
        sname = e.get("supplier_name","") or ""
        self._f_supplier.set(sname)

        items = crud.get_entry_items(entry_id)
        self._items_buffer = [
            {
                "product_id":   it["product_id"],
                "product_code": it["product_code"],
                "description":  it["product_description"],
                "unit":         it.get("unit","UND"),
                "quantity":     float(it["quantity"]),
                "unit_cost":    float(it["unit_cost"]),
                "tax_percent":  float(it.get("tax_percent",0)),
                "total_cost":   float(it["total_cost"]),
            }
            for it in items
        ]
        self._refresh_items_table()

    # ────────────────────────────────────────────
    # Gestión de ítems del documento
    # ────────────────────────────────────────────
    def _lookup_product(self):
        code = self._add_code.get().strip().upper()
        if not code:
            return
        p = crud.get_product_by_code(code)
        if p:
            self._current_product = p
            self._lbl_prod.config(text=p["description"][:38], fg=SUCCESS)
            self._add_cost.delete(0,"end")
            self._add_cost.insert(0, str(p["cost"]))
            self._add_qty.focus_set()
        else:
            self._lbl_prod.config(text="Producto no encontrado", fg=DANGER)
            self._current_product = None

    def _open_product_picker(self):
        ProductPickerDialog(self, on_select=self._on_product_picked)

    def _on_product_picked(self, product: dict):
        self._current_product = product
        self._add_code.delete(0,"end")
        self._add_code.insert(0, product["product_code"])
        self._lbl_prod.config(text=product["description"][:38], fg=SUCCESS)
        self._add_cost.delete(0,"end")
        self._add_cost.insert(0, str(product["cost"]))
        self._add_qty.focus_set()

    def _add_item(self):
        if not self._current_product:
            self._lookup_product()
        if not self._current_product:
            show_error("Error", "Seleccione un producto válido primero.")
            return
        try:
            qty  = float(self._add_qty.get())
            cost = float(self._add_cost.get())
            tax  = float(self._add_tax.get() or 0)
        except ValueError:
            show_error("Error", "Cantidad y costo deben ser números.")
            return
        if qty <= 0:
            show_error("Error", "La cantidad debe ser mayor a cero.")
            return
        if cost < 0:
            show_error("Error", "El costo no puede ser negativo.")
            return

        item = {
            "product_id":   self._current_product["id"],
            "product_code": self._current_product["product_code"],
            "description":  self._current_product["description"],
            "unit":         self._current_product.get("unit","UND"),
            "quantity":     qty,
            "unit_cost":    cost,
            "tax_percent":  tax,
            "total_cost":   round(qty * cost, 4),
        }
        self._items_buffer.append(item)
        self._refresh_items_table()
        # Limpiar fila de adición
        self._add_code.delete(0,"end")
        self._add_qty.delete(0,"end")
        self._add_cost.delete(0,"end")
        self._add_tax.delete(0,"end"); self._add_tax.insert(0,"0")
        self._lbl_prod.config(text="—", fg=TEXT_SECONDARY)
        self._current_product = None

    def _remove_item(self):
        sel = self._items_table.tree.selection()
        if not sel:
            return
        idx = self._items_table.tree.index(sel[0])
        if 0 <= idx < len(self._items_buffer):
            self._items_buffer.pop(idx)
            self._refresh_items_table()

    def _refresh_items_table(self):
        self._items_table.clear()
        total = 0.0
        for i, it in enumerate(self._items_buffer):
            tag = "even" if i % 2 == 0 else "odd"
            self._items_table.tree.insert("", "end", tags=(tag,), values=(
                it["product_code"],
                it["description"],
                it.get("unit","UND"),
                f"{it['quantity']:,.4f}",
                f"{it['unit_cost']:,.4f}",
                f"{it['tax_percent']:.1f}%",
                f"$ {it['total_cost']:,.2f}",
            ))
            total += it["total_cost"]
        self._lbl_total.config(text=f"$ {total:,.2f}")

    # ────────────────────────────────────────────
    # CRUD
    # ────────────────────────────────────────────
    def _new(self):
        self._selected_id = None
        self._items_buffer = []
        self._f_num.set(crud.get_next_entry_number())
        self._f_date.set(date.today().isoformat())
        self._f_invoice.clear()
        self._f_notes.clear()
        self._f_supplier.clear()
        self._refresh_items_table()
        self._add_code.focus_set()

    def _cancel(self):
        self._selected_id = None
        self._items_buffer = []
        self._f_num.clear()
        self._f_invoice.clear()
        self._f_notes.clear()
        self._f_supplier.clear()
        self._refresh_items_table()

    def _save(self):
        num = self._f_num.get().strip()
        if not num:
            show_error("Error", "El número de entrada es obligatorio.")
            return
        if not self._items_buffer:
            show_error("Error", "Agregue al menos un producto.")
            return
        if self._selected_id:
            show_error("Aviso", "Las entradas confirmadas no se pueden editar.\nElimínela y cree una nueva.")
            return

        sname = self._f_supplier.get()
        sid   = None
        for s in self._suppliers:
            if s["name"] == sname:
                sid = s["id"]
                break

        header = {
            "entry_number":   num,
            "entry_date":     self._f_date.get() or date.today().isoformat(),
            "supplier_id":    sid,
            "invoice_number": self._f_invoice.get(),
            "notes":          self._f_notes.get(),
        }
        try:
            crud.create_entry(header, self._items_buffer)
            show_info("Éxito", f"Entrada {num} confirmada y stock actualizado.")
            self._cancel()
            self.refresh()
        except Exception as e:
            show_error("Error al guardar", str(e))

    def _delete(self):
        if not self._selected_id:
            show_error("Error", "Seleccione una entrada de la lista.")
            return
        if ask_confirm("Eliminar Entrada",
                       "¿Eliminar esta entrada? El stock se revertirá automáticamente."):
            try:
                crud.delete_entry(self._selected_id)
                self._cancel()
                self.refresh()
            except Exception as e:
                show_error("Error al eliminar", str(e))


# ─────────────────────────────────────────────────
# Diálogo selector de producto (compartido con Salidas)
# ─────────────────────────────────────────────────

class ProductPickerDialog(tk.Toplevel):
    def __init__(self, parent, on_select=None):
        super().__init__(parent)
        self.title("Seleccionar Producto")
        self.geometry("700x420")
        self.configure(bg=BG_DARK)
        self.grab_set()
        self._on_select = on_select

        tk.Label(self, text="Buscar y seleccionar producto",
                 bg=BG_DARK, fg=ACCENT, font=FONT_HEAD).pack(pady=PAD)

        self._search = SearchBar(self, on_search=self._do_search)
        self._search.pack(padx=PAD, fill="x")

        cols = [
            ("code",  "Código",      110, "w"),
            ("desc",  "Descripción", 300, "w"),
            ("unit",  "Und",          50, "center"),
            ("stock", "Stock",       100, "e"),
            ("cost",  "Costo",       100, "e"),
            ("price", "Precio",      100, "e"),
        ]
        self._table = AppTable(self, columns=cols)
        self._table.pack(fill="both", expand=True, padx=PAD, pady=PAD_SM)
        self._table.bind_double(self._select)

        AppButton(self, text="✅ Seleccionar", command=self._select,
                  style="success").pack(pady=(0, PAD))

        self._products = []
        self._do_search("")

    def _do_search(self, q=""):
        self._products = crud.get_all_products(search=q)
        self._table.clear()
        for i, p in enumerate(self._products):
            tag = "even" if i % 2 == 0 else "odd"
            self._table.tree.insert("", "end", iid=str(p["id"]), tags=(tag,), values=(
                p["product_code"],
                p["description"],
                p.get("unit","UND"),
                f"{float(p['current_quantity']):,.4f}",
                f"{float(p['cost']):,.2f}",
                f"{float(p['price']):,.2f}",
            ))

    def _select(self):
        sel = self._table.tree.selection()
        if not sel:
            return
        pid = int(sel[0])
        p   = crud.get_product(pid)
        if p and self._on_select:
            self._on_select(p)
        self.destroy()
