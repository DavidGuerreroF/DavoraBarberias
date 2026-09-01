"""
Vista de Kardex — movimientos cronológicos por producto con saldo acumulado.
"""

import tkinter as tk
from tkinter import ttk
from app.core.theme import *
from app.core.widgets import AppButton, AppTable, LabeledCombo, SearchBar
from app.db import crud


class KardexView(tk.Frame):
    def __init__(self, parent, navigate=None, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self._navigate = navigate
        self._products = []
        self._build()
        self.refresh()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG_DARK, pady=PAD)
        hdr.pack(fill="x", padx=PAD_LG)
        tk.Label(hdr, text="📊  Kardex de Inventario", bg=BG_DARK,
                 fg=TEXT_PRIMARY, font=FONT_TITLE).pack(side="left")
        AppButton(hdr, text="🔄 Refrescar", command=self.refresh,
                  style="ghost").pack(side="right", padx=4)

        # Filtros
        filter_frame = tk.Frame(self, bg=BG_CARD, padx=PAD, pady=PAD_SM)
        filter_frame.pack(fill="x", padx=PAD_LG, pady=(0, PAD_SM))

        tk.Label(filter_frame, text="Producto:", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).grid(row=0, column=0, sticky="w", padx=(0,4))
        self._combo_prod = ttk.Combobox(filter_frame, state="readonly", width=40, font=FONT_BODY)
        self._combo_prod.grid(row=0, column=1, padx=(0,PAD))

        tk.Label(filter_frame, text="Desde:", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).grid(row=0, column=2, sticky="w", padx=(0,4))
        self._f_from = tk.Entry(filter_frame, bg=BG_INPUT, fg=TEXT_PRIMARY,
                                insertbackground=TEXT_PRIMARY,
                                font=FONT_BODY, relief="flat", width=12)
        self._f_from.grid(row=0, column=3, padx=(0,PAD), ipady=4)

        tk.Label(filter_frame, text="Hasta:", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).grid(row=0, column=4, sticky="w", padx=(0,4))
        self._f_to = tk.Entry(filter_frame, bg=BG_INPUT, fg=TEXT_PRIMARY,
                              insertbackground=TEXT_PRIMARY,
                              font=FONT_BODY, relief="flat", width=12)
        self._f_to.grid(row=0, column=5, padx=(0,PAD), ipady=4)

        AppButton(filter_frame, text="🔍 Buscar", command=self._do_search,
                  style="primary").grid(row=0, column=6, padx=(0,PAD))
        AppButton(filter_frame, text="✖ Limpiar", command=self._clear_filters,
                  style="ghost").grid(row=0, column=7)

        # Tabla de movimientos
        cols = [
            ("tipo",      "Tipo",        90,  "center"),
            ("doc",       "Documento",  120,  "w"),
            ("fecha",     "Fecha",       90,  "center"),
            ("code",      "Código",     100,  "w"),
            ("producto",  "Producto",   260,  "w"),
            ("entrada",   "Entrada",    100,  "e"),
            ("salida",    "Salida",     100,  "e"),
            ("ajuste",    "Ajuste",     100,  "e"),
            ("costo",     "Costo U.",   100,  "e"),
            ("total",     "Total",      110,  "e"),
            ("saldo",     "Saldo",      110,  "e"),
            ("contra",    "Contraparte",160,  "w"),
        ]
        table_frame = tk.Frame(self, bg=BG_DARK)
        table_frame.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD))
        self._table = AppTable(table_frame, columns=cols)
        self._table.pack(fill="both", expand=True)

        # Estilos extra por tipo de movimiento
        self._table.tree.tag_configure("ENTRADA",  foreground=SUCCESS,  background=BG_TABLE)
        self._table.tree.tag_configure("SALIDA",   foreground=DANGER,   background=BG_TABLE)
        self._table.tree.tag_configure("AJUSTE+",  foreground=INFO,     background=BG_TABLE)
        self._table.tree.tag_configure("AJUSTE-",  foreground=WARNING,  background=BG_TABLE)
        self._table.tree.tag_configure("ENT_ALT",  foreground=SUCCESS,  background=BG_TABLE_ALT)
        self._table.tree.tag_configure("SAL_ALT",  foreground=DANGER,   background=BG_TABLE_ALT)
        self._table.tree.tag_configure("AJP_ALT",  foreground=INFO,     background=BG_TABLE_ALT)
        self._table.tree.tag_configure("AJN_ALT",  foreground=WARNING,  background=BG_TABLE_ALT)

        # Resumen inferior
        sum_frame = tk.Frame(self, bg=BG_CARD, padx=PAD, pady=PAD_SM)
        sum_frame.pack(fill="x", padx=PAD_LG, pady=(0, PAD))
        self._lbl_total_ent  = self._sum_label(sum_frame, "Total Entradas:", SUCCESS)
        self._lbl_total_sal  = self._sum_label(sum_frame, "Total Salidas:", DANGER)
        self._lbl_total_adj  = self._sum_label(sum_frame, "Total Ajustes:", INFO)
        self._lbl_saldo_fin  = self._sum_label(sum_frame, "Saldo Final:", ACCENT)
        self._lbl_movs       = self._sum_label(sum_frame, "Movimientos:", TEXT_SECONDARY)

    def _sum_label(self, parent, title, color):
        f = tk.Frame(parent, bg=BG_CARD)
        f.pack(side="left", padx=PAD_LG)
        tk.Label(f, text=title, bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL).pack(anchor="w")
        lbl = tk.Label(f, text="—", bg=BG_CARD, fg=color, font=FONT_HEAD)
        lbl.pack(anchor="w")
        return lbl

    def refresh(self):
        self._products = crud.get_all_products()
        names = ["(Todos los productos)"] + [
            f"{p['product_code']} — {p['description']}" for p in self._products
        ]
        self._combo_prod["values"] = names
        if not self._combo_prod.get():
            self._combo_prod.set("(Todos los productos)")
        self._do_search()

    def _clear_filters(self):
        self._combo_prod.set("(Todos los productos)")
        self._f_from.delete(0,"end")
        self._f_to.delete(0,"end")
        self._do_search()

    def _do_search(self):
        # Resolver product_id
        sel  = self._combo_prod.get()
        pid  = None
        for p in self._products:
            key = f"{p['product_code']} — {p['description']}"
            if key == sel:
                pid = p["id"]
                break

        date_from = self._f_from.get().strip() or None
        date_to   = self._f_to.get().strip()   or None

        rows = crud.get_kardex(product_id=pid, date_from=date_from, date_to=date_to)
        self._table.clear()

        saldo         = 0.0
        tot_entrada   = 0.0
        tot_salida    = 0.0
        tot_ajuste    = 0.0

        for i, r in enumerate(rows):
            alt    = (i % 2 != 0)
            tipo   = r["tipo"]
            ent    = float(r.get("entrada", 0))
            sal    = float(r.get("salida",  0))
            adj    = float(r.get("ajuste",  0))
            saldo += ent - sal + (adj if tipo == "AJUSTE" else 0)
            # Para AJUSTE se sumó arriba, recalcular bien:
            # El saldo acumulado se calcula con qty_signed
            if tipo == "ENTRADA":
                saldo_delta = ent
                tot_entrada += ent
                tag = "ENT_ALT" if alt else "ENTRADA"
            elif tipo == "SALIDA":
                saldo_delta = -sal
                tot_salida  += sal
                tag = "SAL_ALT" if alt else "SALIDA"
            else:  # AJUSTE
                saldo_delta = adj  # ya tiene signo
                tot_ajuste  += adj
                if adj >= 0:
                    tag = "AJP_ALT" if alt else "AJUSTE+"
                else:
                    tag = "AJN_ALT" if alt else "AJUSTE-"

            # Recalcular saldo correctamente (reset y reacumular)
            costo   = float(r.get("costo_unit",0) or 0)
            total   = float(r.get("total",0) or 0)
            contra  = r.get("contraparte","") or ""

            self._table.tree.insert("", "end", tags=(tag,), values=(
                tipo,
                r["documento"],
                (r.get("fecha","") or "")[:10],
                r["product_code"],
                r["producto"],
                f"{ent:,.4f}"   if ent  > 0 else "—",
                f"{sal:,.4f}"   if sal  > 0 else "—",
                f"{adj:+,.4f}"  if tipo == "AJUSTE" else "—",
                f"{costo:,.4f}" if costo else "—",
                f"$ {total:,.2f}",
                "—",          # saldo se recalcula abajo
                contra,
            ))

        # Recalcular saldos acumulados pasando de nuevo
        # Rearmar con saldo correcto
        self._table.clear()
        saldo = 0.0
        tot_entrada = tot_salida = tot_ajuste = 0.0
        for i, r in enumerate(rows):
            alt  = (i % 2 != 0)
            tipo = r["tipo"]
            ent  = float(r.get("entrada", 0))
            sal  = float(r.get("salida",  0))
            adj  = float(r.get("ajuste",  0))

            if tipo == "ENTRADA":
                saldo += ent
                tot_entrada += ent
                tag = "ENT_ALT" if alt else "ENTRADA"
            elif tipo == "SALIDA":
                saldo -= sal
                tot_salida += sal
                tag = "SAL_ALT" if alt else "SALIDA"
            else:
                saldo += adj
                tot_ajuste += adj
                if adj >= 0:
                    tag = "AJP_ALT" if alt else "AJUSTE+"
                else:
                    tag = "AJN_ALT" if alt else "AJUSTE-"

            costo  = float(r.get("costo_unit", 0) or 0)
            total  = float(r.get("total", 0)      or 0)
            contra = r.get("contraparte","") or ""

            self._table.tree.insert("", "end", tags=(tag,), values=(
                tipo,
                r["documento"],
                (r.get("fecha","") or "")[:10],
                r["product_code"],
                r["producto"],
                f"{ent:,.4f}"   if ent  > 0 else "—",
                f"{sal:,.4f}"   if sal  > 0 else "—",
                f"{adj:+,.4f}"  if tipo == "AJUSTE" else "—",
                f"{costo:,.4f}" if costo else "—",
                f"$ {total:,.2f}",
                f"{saldo:,.4f}",
                contra,
            ))

        # Actualizar resumen
        self._lbl_total_ent.config(text=f"{tot_entrada:,.4f}")
        self._lbl_total_sal.config(text=f"{tot_salida:,.4f}")
        self._lbl_total_adj.config(text=f"{tot_ajuste:+,.4f}")
        self._lbl_saldo_fin.config(text=f"{saldo:,.4f}")
        self._lbl_movs.config(text=str(len(rows)))
