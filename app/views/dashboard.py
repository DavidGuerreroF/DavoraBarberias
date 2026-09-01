"""
Vista de Dashboard — KPIs, gráficas simples con Canvas nativo y tablas resumen.
"""

import tkinter as tk
from app.core.theme import *
from app.core.widgets import AppButton, KpiCard
from app.db import crud


class DashboardView(tk.Frame):
    def __init__(self, parent, navigate=None, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self._navigate = navigate
        self._build()
        self.refresh()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG_DARK, pady=PAD)
        hdr.pack(fill="x", padx=PAD_LG)
        tk.Label(hdr, text="🏠  Dashboard", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=FONT_TITLE).pack(side="left")
        AppButton(hdr, text="🔄 Refrescar", command=self.refresh,
                  style="ghost").pack(side="right")

        # Área con scroll
        canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        self._inner = tk.Frame(canvas, bg=BG_DARK)
        self._win_id = canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(self._win_id, width=e.width))
        # Scroll con rueda del ratón
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._canvas = canvas

    def refresh(self):
        # Limpiar inner
        for w in self._inner.winfo_children():
            w.destroy()

        kpis = crud.get_dashboard_kpis()

        # ── Fila 1: tarjetas KPI ──
        kpi_row = tk.Frame(self._inner, bg=BG_DARK)
        kpi_row.pack(fill="x", padx=PAD_LG, pady=(PAD, PAD_SM))

        cards_data = [
            ("Productos activos",   kpis["total_products"],  ACCENT,   "📦"),
            ("Proveedores",         kpis["total_suppliers"], INFO,     "🏭"),
            ("Grupos",              kpis["total_groups"],    WARNING,  "🗂️"),
            ("Valor en stock",      f"$ {kpis['stock_value']:,.0f}", SUCCESS, "💰"),
            ("Entradas hoy",        kpis["entries_today"],   SUCCESS,  "⬇️"),
            ("Salidas hoy",         kpis["exits_today"],     DANGER,   "⬆️"),
            ("Bajo stock mínimo",   kpis["low_stock_count"], DANGER if kpis["low_stock_count"] else SUCCESS, "⚠️"),
        ]

        for title, value, color, icon in cards_data:
            card = KpiCard(kpi_row, title=title, value=value, color=color, icon=icon)
            card.pack(side="left", padx=(0, PAD_SM), pady=4, ipadx=6, ipady=4)

        # ── Alerta bajo stock ──
        if kpis["low_stock_count"] > 0:
            alert = tk.Frame(self._inner, bg="#3d2020", padx=PAD, pady=PAD_SM)
            alert.pack(fill="x", padx=PAD_LG, pady=(0, PAD_SM))
            tk.Label(alert,
                     text=f"⚠️  {kpis['low_stock_count']} producto(s) por debajo del stock mínimo.",
                     bg="#3d2020", fg=DANGER, font=FONT_HEAD).pack(side="left")
            if self._navigate:
                AppButton(alert, text="Ver Productos", style="danger",
                          command=lambda: self._navigate("products")).pack(side="right")

        # ── Fila 2: dos columnas ──
        col_row = tk.Frame(self._inner, bg=BG_DARK)
        col_row.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD_SM))
        col_row.columnconfigure(0, weight=1)
        col_row.columnconfigure(1, weight=1)

        # Columna izquierda: últimas entradas
        self._build_mini_table(
            col_row,
            title="📥 Últimas Entradas",
            headers=["N° Entrada", "Fecha", "Proveedor", "Total"],
            rows=[
                (e["entry_number"],
                 (e.get("entry_date","") or "")[:10],
                 e.get("supplier","") or "—",
                 f"$ {float(e.get('total_cost',0)):,.2f}")
                for e in kpis["last_entries"]
            ],
            col=0,
        )

        # Columna derecha: últimas salidas
        self._build_mini_table(
            col_row,
            title="📤 Últimas Salidas",
            headers=["N° Salida", "Fecha", "Cliente", "Total"],
            rows=[
                (e["exit_number"],
                 (e.get("exit_date","") or "")[:10],
                 e.get("client_name","") or "—",
                 f"$ {float(e.get('total_cost',0)):,.2f}")
                for e in kpis["last_exits"]
            ],
            col=1,
        )

        # ── Fila 3: top productos + gráfica de barras ──
        row3 = tk.Frame(self._inner, bg=BG_DARK)
        row3.pack(fill="both", padx=PAD_LG, pady=(0, PAD_LG))
        row3.columnconfigure(0, weight=1)
        row3.columnconfigure(1, weight=1)

        self._build_top_products(row3, kpis["top_products"])
        self._build_bar_chart(row3, kpis["top_products"])

    def _build_mini_table(self, parent, title, headers, rows, col):
        frame = tk.Frame(parent, bg=BG_CARD, padx=PAD, pady=PAD)
        frame.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else PAD_SM, 0))

        tk.Label(frame, text=title, bg=BG_CARD, fg=ACCENT, font=FONT_HEAD).pack(anchor="w",
                                                                                  pady=(0, PAD_SM))

        # Header row
        hdr = tk.Frame(frame, bg=BG_CARD)
        hdr.pack(fill="x")
        widths = [130, 80, 160, 90]
        for i, h in enumerate(headers):
            tk.Label(hdr, text=h, bg=BG_CARD, fg=TEXT_MUTED,
                     font=FONT_SMALL, width=widths[i]//8, anchor="w").pack(side="left")

        tk.Frame(frame, bg=BG_INPUT, height=1).pack(fill="x", pady=4)

        if not rows:
            tk.Label(frame, text="Sin movimientos recientes.", bg=BG_CARD,
                     fg=TEXT_MUTED, font=FONT_SMALL).pack(pady=PAD)
            return

        for i, row in enumerate(rows):
            bg = BG_TABLE_ALT if i % 2 == 0 else BG_TABLE
            r  = tk.Frame(frame, bg=bg)
            r.pack(fill="x")
            for j, cell in enumerate(row):
                tk.Label(r, text=str(cell), bg=bg, fg=TEXT_PRIMARY,
                         font=FONT_BODY, width=widths[j]//8, anchor="w",
                         padx=4, pady=3).pack(side="left")

    def _build_top_products(self, parent, top_products):
        frame = tk.Frame(parent, bg=BG_CARD, padx=PAD, pady=PAD)
        frame.grid(row=0, column=0, sticky="nsew", pady=(PAD_SM, 0))

        tk.Label(frame, text="🏆 Top 5 Productos por Valor en Stock",
                 bg=BG_CARD, fg=ACCENT, font=FONT_HEAD).pack(anchor="w", pady=(0, PAD_SM))

        headers  = ["Producto", "Stock", "Costo", "Valor Total"]
        widths   = [200, 80, 80, 100]
        hdr = tk.Frame(frame, bg=BG_CARD); hdr.pack(fill="x")
        for i, h in enumerate(headers):
            tk.Label(hdr, text=h, bg=BG_CARD, fg=TEXT_MUTED,
                     font=FONT_SMALL, width=widths[i]//7, anchor="w").pack(side="left")
        tk.Frame(frame, bg=BG_INPUT, height=1).pack(fill="x", pady=4)

        if not top_products:
            tk.Label(frame, text="No hay productos.", bg=BG_CARD,
                     fg=TEXT_MUTED, font=FONT_SMALL).pack(pady=PAD)
            return

        for i, p in enumerate(top_products):
            bg = BG_TABLE_ALT if i % 2 == 0 else BG_TABLE
            r  = tk.Frame(frame, bg=bg); r.pack(fill="x")
            vals = [
                p["description"][:28],
                f"{float(p['current_quantity']):,.2f}",
                f"$ {float(p['cost']):,.2f}",
                f"$ {float(p['valor']):,.0f}",
            ]
            for j, v in enumerate(vals):
                tk.Label(r, text=v, bg=bg, fg=TEXT_PRIMARY,
                         font=FONT_BODY, width=widths[j]//7, anchor="w",
                         padx=4, pady=4).pack(side="left")

    def _build_bar_chart(self, parent, top_products):
        frame = tk.Frame(parent, bg=BG_CARD, padx=PAD, pady=PAD)
        frame.grid(row=0, column=1, sticky="nsew", padx=(PAD_SM, 0), pady=(PAD_SM, 0))
        tk.Label(frame, text="📊 Valor en Stock — Top 5",
                 bg=BG_CARD, fg=ACCENT, font=FONT_HEAD).pack(anchor="w", pady=(0, PAD_SM))

        if not top_products:
            tk.Label(frame, text="Sin datos.", bg=BG_CARD,
                     fg=TEXT_MUTED, font=FONT_SMALL).pack(pady=PAD)
            return

        max_val = max(float(p["valor"]) for p in top_products) or 1
        canvas  = tk.Canvas(frame, bg=BG_CARD, height=200,
                            highlightthickness=0, width=380)
        canvas.pack(fill="x")

        bar_h   = 28
        gap     = 10
        x_label = 160
        x_start = x_label + 10
        max_bar = 180
        colors  = [ACCENT, INFO, SUCCESS, WARNING, DANGER]

        for i, p in enumerate(top_products):
            y = i * (bar_h + gap) + 10
            pct = float(p["valor"]) / max_val
            bar_w = max(4, int(pct * max_bar))

            # Nombre
            name = p["description"][:22]
            canvas.create_text(x_label - 5, y + bar_h // 2,
                                text=name, fill=TEXT_SECONDARY,
                                font=FONT_SMALL, anchor="e")
            # Barra
            col = colors[i % len(colors)]
            canvas.create_rectangle(x_start, y,
                                     x_start + bar_w, y + bar_h,
                                     fill=col, outline="")
            # Valor
            canvas.create_text(x_start + bar_w + 6, y + bar_h // 2,
                                text=f"$ {float(p['valor']):,.0f}",
                                fill=col, font=FONT_SMALL, anchor="w")
