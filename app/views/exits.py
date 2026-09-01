"""
Vista de Salidas de Inventario — con control de stock disponible.
"""

import tkinter as tk
from datetime import date
from app.core.theme import *
from app.core.widgets import (
    AppButton, LabeledEntry, LabeledCombo,
    AppTable, SearchBar, ask_confirm, show_error, show_info
)
from app.db import crud
from app.views.entries import ProductPickerDialog


class ExitsView(tk.Frame):
    def __init__(self, parent, navigate=None, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self._navigate    = navigate
        self._selected_id = None
        self._items_buffer = []
        self._current_product = None
        self._build()
        self.refresh()

    def _build(self):
        hdr = tk.Frame(self, bg=BG_DARK, pady=PAD)
        hdr.pack(fill="x", padx=PAD_LG)
        tk.Label(hdr, text="⬆️  Salidas de Inventario", bg=BG_DARK,
                 fg=TEXT_PRIMARY, font=FONT_TITLE).pack(side="left")
        AppButton(hdr, text="＋ Nueva Salida", command=self._new,
                  style="primary").pack(side="right", padx=4)
        AppButton(hdr, text="🔄 Refrescar", command=self.refresh,
                  style="ghost").pack(side="right", padx=4)

        paned = tk.PanedWindow(self, orient="vertical", bg=BG_DARK,
                               sashwidth=6, sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD))

        # Lista superior
        top_frame = tk.Frame(paned, bg=BG_DARK)
        paned.add(top_frame, minsize=160)

        sr = tk.Frame(top_frame, bg=BG_DARK)
        sr.pack(fill="x", pady=(0, PAD_SM))
        SearchBar(sr, on_search=lambda q: self.refresh(q)).pack(side="left")

        list_cols = [
            ("num",     "N° Salida",    120, "w"),
            ("date",    "Fecha",         90, "center"),
            ("client",  "Cliente",      200, "w"),
            ("invoice", "Factura",      110, "w"),
            ("total",   "Total Costo",  120, "e"),
            ("notes",   "Notas",        220, "w"),
        ]
        self._list_table = AppTable(top_frame, columns=list_cols)
        self._list_table.pack(fill="both", expand=True)
        self._list_table.bind_double(self._on_list_select)
        self._list_table.bind_select(self._on_list_click)

        # Formulario inferior
        bot_frame = tk.Frame(paned, bg=BG_CARD)
        paned.add(bot_frame, minsize=280)
        self._build_form(bot_frame)

    def _build_form(self, parent):
        top = tk.Frame(parent, bg=BG_CARD, pady=PAD_SM, padx=PAD)
        top.pack(fill="x")
        tk.Label(top, text="Documento de Salida", bg=BG_CARD,
                 fg=ACCENT, font=FONT_HEAD).pack(side="left")
        AppButton(top, text="💾 Confirmar Salida", command=self._save,
                  style="success").pack(side="right", padx=(4,0))
        AppButton(top, text="🗑 Eliminar",  command=self._delete,
                  style="danger").pack(side="right", padx=4)
        AppButton(top, text="✖ Cancelar",  command=self._cancel,
                  style="ghost").pack(side="right", padx=4)

        tk.Frame(parent, bg=BG_INPUT, height=1).pack(fill="x")

        hdr_frame = tk.Frame(parent, bg=BG_CARD, padx=PAD, pady=PAD_SM)
        hdr_frame.pack(fill="x")
        self._f_num     = LabeledEntry(hdr_frame, "N° Salida *", width=130)
        self._f_num.grid(row=0, column=0, sticky="ew", padx=(0,PAD_SM))
        self._f_date    = LabeledEntry(hdr_frame, "Fecha (YYYY-MM-DD)", width=130)
        self._f_date.set(date.today().isoformat())
        self._f_date.grid(row=0, column=1, sticky="ew", padx=(0,PAD_SM))
        self._f_client  = LabeledEntry(hdr_frame, "Cliente", width=160)
        self._f_client.grid(row=0, column=2, sticky="ew", padx=(0,PAD_SM))
        self._f_invoice = LabeledEntry(hdr_frame, "N° Factura", width=130)
        self._f_invoice.grid(row=0, column=3, sticky="ew", padx=(0,PAD_SM))
        self._f_notes   = LabeledEntry(hdr_frame, "Notas", width=200)
        self._f_notes.grid(row=0, column=4, sticky="ew")
        for c in range(5):
            hdr_frame.columnconfigure(c, weight=1)

        # Fila de adición
        add_row = tk.Frame(parent, bg=BG_SIDEBAR, padx=PAD, pady=PAD_SM)
        add_row.pack(fill="x")
        tk.Label(add_row, text="Producto:", bg=BG_SIDEBAR,
                 fg=TEXT_SECONDARY, font=FONT_SMALL).pack(side="left", padx=(0,4))
        self._add_code = tk.Entry(add_row, bg=BG_INPUT, fg=TEXT_PRIMARY,
                                  insertbackground=TEXT_PRIMARY,
                                  font=FONT_BODY, relief="flat", width=16)
        self._add_code.pack(side="left", ipady=4, padx=(0,4))
        self._add_code.bind("<Return>", lambda e: self._lookup_product())
        self._lbl_prod = tk.Label(add_row, text="—", bg=BG_SIDEBAR,
                                  fg=TEXT_SECONDARY, font=FONT_SMALL, width=30, anchor="w")
        self._lbl_prod.pack(side="left", padx=(0,PAD_SM))
        self._lbl_stock = tk.Label(add_row, text="", bg=BG_SIDEBAR,
                                   fg=INFO, font=FONT_SMALL, width=14, anchor="w")
        self._lbl_stock.pack(side="left", padx=(0,PAD_SM))

        tk.Label(add_row, text="Cant:", bg=BG_SIDEBAR, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).pack(side="left")
        self._add_qty = tk.Entry(add_row, bg=BG_INPUT, fg=TEXT_PRIMARY,
                                 insertbackground=TEXT_PRIMARY,
                                 font=FONT_BODY, relief="flat", width=8)
        self._add_qty.pack(side="left", ipady=4, padx=(4,4))

        tk.Label(add_row, text="Precio u.:", bg=BG_SIDEBAR, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).pack(side="left")
        self._add_price = tk.Entry(add_row, bg=BG_INPUT, fg=TEXT_PRIMARY,
                                   insertbackground=TEXT_PRIMARY,
                                   font=FONT_BODY, relief="flat", width=10)
        self._add_price.pack(side="left", ipady=4, padx=(4,4))

        AppButton(add_row, text="➕ Agregar", command=self._add_item,
                  style="primary").pack(side="left", padx=(4,0))
        AppButton(add_row, text="🔎 Buscar", command=self._open_picker,
                  style="ghost").pack(side="left", padx=4)

        # Tabla de ítems
        items_frame = tk.Frame(parent, bg=BG_CARD)
        items_frame.pack(fill="both", expand=True, padx=PAD, pady=(PAD_SM, 0))
        item_cols = [
            ("code",   "Código",      100, "w"),
            ("desc",   "Descripción", 300, "w"),
            ("unit",   "Und",          50, "center"),
            ("stock",  "Stock Disp.", 100, "e"),
            ("qty",    "Cantidad",    100, "e"),
            ("price",  "Precio",      110, "e"),
            ("total",  "Total",       120, "e"),
        ]
        self._items_table = AppTable(items_frame, columns=item_cols)
        self._items_table.pack(fill="both", expand=True)
        self._items_table.bind_double(self._remove_item)

        tot_row = tk.Frame(parent, bg=BG_CARD, padx=PAD, pady=PAD_SM)
        tot_row.pack(fill="x")
        tk.Label(tot_row, text="Total Salida:", bg=BG_CARD,
                 fg=TEXT_SECONDARY, font=FONT_HEAD).pack(side="right", padx=(0,4))
        self._lbl_total = tk.Label(tot_row, text="$ 0.00", bg=BG_CARD,
                                   fg=DANGER, font=("Segoe UI", 14, "bold"))
        self._lbl_total.pack(side="right")
        tk.Label(tot_row, text="(doble clic en ítem para eliminarlo)",
                 bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL).pack(side="left")

    # ── Datos ──
    def refresh(self, search=""):
        exits = crud.get_all_exits(search)
        self._list_table.clear()
        for i, e in enumerate(exits):
            tag = "even" if i % 2 == 0 else "odd"
            self._list_table.tree.insert("", "end", iid=str(e["id"]), tags=(tag,), values=(
                e["exit_number"],
                (e.get("exit_date","") or "")[:10],
                e.get("client_name","") or "",
                e.get("invoice_number","") or "",
                f"$ {float(e.get('total_cost',0)):,.2f}",
                e.get("notes","") or "",
            ))

    def _on_list_click(self):
        sel = self._list_table.tree.selection()
        if sel:
            self._load_exit(int(sel[0]))

    def _on_list_select(self):
        self._on_list_click()

    def _load_exit(self, exit_id: int):
        self._selected_id = exit_id
        e = crud.get_exit(exit_id)
        if not e: return
        self._f_num.set(e["exit_number"])
        self._f_date.set((e.get("exit_date","") or "")[:10])
        self._f_client.set(e.get("client_name","") or "")
        self._f_invoice.set(e.get("invoice_number","") or "")
        self._f_notes.set(e.get("notes","") or "")
        items = crud.get_exit_items(exit_id)
        self._items_buffer = [
            {
                "product_id":   it["product_id"],
                "product_code": it["product_code"],
                "description":  it["product_description"],
                "unit":         it.get("unit","UND"),
                "current_quantity": 0,
                "quantity":     float(it["quantity"]),
                "unit_cost":    float(it["unit_cost"]),
                "unit_price":   float(it["unit_price"]),
                "total_cost":   float(it["total_cost"]),
            }
            for it in items
        ]
        self._refresh_items_table()

    # ── Ítems ──
    def _lookup_product(self):
        code = self._add_code.get().strip().upper()
        if not code: return
        p = crud.get_product_by_code(code)
        if p:
            self._current_product = p
            self._lbl_prod.config(text=p["description"][:30], fg=SUCCESS)
            stock = float(p["current_quantity"])
            self._lbl_stock.config(
                text=f"Stock: {stock:,.2f}",
                fg=SUCCESS if stock > 0 else DANGER
            )
            self._add_price.delete(0,"end")
            self._add_price.insert(0, str(p["price"]))
            self._add_qty.focus_set()
        else:
            self._lbl_prod.config(text="No encontrado", fg=DANGER)
            self._lbl_stock.config(text="")
            self._current_product = None

    def _open_picker(self):
        ProductPickerDialog(self, on_select=self._on_product_picked)

    def _on_product_picked(self, product):
        self._current_product = product
        self._add_code.delete(0,"end")
        self._add_code.insert(0, product["product_code"])
        self._lbl_prod.config(text=product["description"][:30], fg=SUCCESS)
        stock = float(product["current_quantity"])
        self._lbl_stock.config(
            text=f"Stock: {stock:,.2f}",
            fg=SUCCESS if stock > 0 else DANGER
        )
        self._add_price.delete(0,"end")
        self._add_price.insert(0, str(product["price"]))
        self._add_qty.focus_set()

    def _add_item(self):
        if not self._current_product:
            self._lookup_product()
        if not self._current_product:
            show_error("Error", "Seleccione un producto válido.")
            return
        try:
            qty   = float(self._add_qty.get())
            price = float(self._add_price.get())
        except ValueError:
            show_error("Error", "Cantidad y precio deben ser números.")
            return
        if qty <= 0:
            show_error("Error", "La cantidad debe ser mayor a cero.")
            return

        item = {
            "product_id":        self._current_product["id"],
            "product_code":      self._current_product["product_code"],
            "description":       self._current_product["description"],
            "unit":              self._current_product.get("unit","UND"),
            "current_quantity":  float(self._current_product.get("current_quantity",0)),
            "quantity":          qty,
            "unit_cost":         float(self._current_product.get("cost",0)),
            "unit_price":        price,
            "total_cost":        round(qty * price, 4),
        }
        self._items_buffer.append(item)
        self._refresh_items_table()
        self._add_code.delete(0,"end")
        self._add_qty.delete(0,"end")
        self._add_price.delete(0,"end")
        self._lbl_prod.config(text="—", fg=TEXT_SECONDARY)
        self._lbl_stock.config(text="")
        self._current_product = None

    def _remove_item(self):
        sel = self._items_table.tree.selection()
        if not sel: return
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
                f"{it.get('current_quantity',0):,.4f}",
                f"{it['quantity']:,.4f}",
                f"{it['unit_price']:,.2f}",
                f"$ {it['total_cost']:,.2f}",
            ))
            total += it["total_cost"]
        self._lbl_total.config(text=f"$ {total:,.2f}")

    # ── CRUD ──
    def _new(self):
        self._selected_id = None
        self._items_buffer = []
        self._f_num.set(crud.get_next_exit_number())
        self._f_date.set(date.today().isoformat())
        self._f_client.clear()
        self._f_invoice.clear()
        self._f_notes.clear()
        self._refresh_items_table()
        self._add_code.focus_set()

    def _cancel(self):
        self._selected_id = None
        self._items_buffer = []
        for f in (self._f_num, self._f_client, self._f_invoice, self._f_notes):
            f.clear()
        self._refresh_items_table()

    def _save(self):
        num = self._f_num.get().strip()
        if not num:
            show_error("Error", "El número de salida es obligatorio.")
            return
        if not self._items_buffer:
            show_error("Error", "Agregue al menos un producto.")
            return
        if self._selected_id:
            show_error("Aviso", "Las salidas confirmadas no se pueden editar.\nElimínela y cree una nueva.")
            return
        header = {
            "exit_number":    num,
            "exit_date":      self._f_date.get() or date.today().isoformat(),
            "client_name":    self._f_client.get(),
            "invoice_number": self._f_invoice.get(),
            "notes":          self._f_notes.get(),
        }
        try:
            crud.create_exit(header, self._items_buffer)
            show_info("Éxito", f"Salida {num} confirmada y stock descontado.")
            self._cancel()
            self.refresh()
        except Exception as e:
            show_error("Error al guardar", str(e))

    def _delete(self):
        if not self._selected_id:
            show_error("Error", "Seleccione una salida de la lista.")
            return
        if ask_confirm("Eliminar Salida",
                       "¿Eliminar esta salida? El stock será restituido."):
            try:
                crud.delete_exit(self._selected_id)
                self._cancel()
                self.refresh()
            except Exception as e:
                show_error("Error al eliminar", str(e))
