"""
Ventana principal con sidebar de navegación y área de contenido.
"""

import tkinter as tk
from tkinter import ttk
from app.core.theme import *


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Inventarios")
        self.geometry("1280x760")
        self.minsize(1024, 640)
        self.configure(bg=BG_DARK)

        # Importar vistas aquí (evita circular imports)
        from app.views.dashboard   import DashboardView
        from app.views.products    import ProductsView
        from app.views.suppliers   import SuppliersView
        from app.views.groups      import GroupsView
        from app.views.entries     import EntriesView
        from app.views.exits       import ExitsView
        from app.views.adjustments import AdjustmentsView
        from app.views.kardex      import KardexView

        self._views_cls = {
            "dashboard":   DashboardView,
            "products":    ProductsView,
            "suppliers":   SuppliersView,
            "groups":      GroupsView,
            "entries":     EntriesView,
            "exits":       ExitsView,
            "adjustments": AdjustmentsView,
            "kardex":      KardexView,
        }
        self._view_cache = {}
        self._current_key = None
        self._btn_refs = {}

        self._build_layout()
        self._show("dashboard")

    # ─── Layout ─────────────────────────────────

    def _build_layout(self):
        # SIDEBAR
        self.sidebar = tk.Frame(self, bg=BG_SIDEBAR, width=SIDEBAR_WIDTH)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / título
        logo_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR, pady=PAD_LG)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="📦", bg=BG_SIDEBAR, fg=ACCENT,
                 font=("Segoe UI Emoji", 26)).pack()
        tk.Label(logo_frame, text="Inventarios", bg=BG_SIDEBAR, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 14, "bold")).pack()
        tk.Label(logo_frame, text="Sistema de Control", bg=BG_SIDEBAR, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack()

        # Separador
        tk.Frame(self.sidebar, bg=BG_CARD, height=1).pack(fill="x", padx=PAD, pady=(0, PAD_SM))

        # Navegación
        nav_items = [
            ("dashboard",   "🏠", "Dashboard"),
            ("products",    "📦", "Productos"),
            ("groups",      "🗂️",  "Grupos"),
            ("suppliers",   "🏭", "Proveedores"),
            ("entries",     "⬇️",  "Entradas"),
            ("exits",       "⬆️",  "Salidas"),
            ("adjustments", "⚖️",  "Ajustes"),
            ("kardex",      "📊", "Kardex"),
        ]
        nav_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        nav_frame.pack(fill="x", padx=PAD_SM)
        for key, icon, label in nav_items:
            btn = self._make_nav_btn(nav_frame, key, icon, label)
            self._btn_refs[key] = btn

        # Versión al pie
        tk.Label(self.sidebar, text="v1.0  |  SQLite", bg=BG_SIDEBAR,
                 fg=TEXT_MUTED, font=FONT_SMALL).pack(side="bottom", pady=PAD)

        # CONTENT AREA
        self.content = tk.Frame(self, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)

    def _make_nav_btn(self, parent, key, icon, label):
        frame = tk.Frame(parent, bg=BG_SIDEBAR, cursor="hand2")
        frame.pack(fill="x", pady=2)

        def on_enter(e):
            if self._current_key != key:
                frame.config(bg="#2a2a3e")
                lbl_icon.config(bg="#2a2a3e")
                lbl_text.config(bg="#2a2a3e")

        def on_leave(e):
            if self._current_key != key:
                frame.config(bg=BG_SIDEBAR)
                lbl_icon.config(bg=BG_SIDEBAR)
                lbl_text.config(bg=BG_SIDEBAR)

        def on_click(e):
            self._show(key)

        lbl_icon = tk.Label(frame, text=icon, bg=BG_SIDEBAR, fg=TEXT_SECONDARY,
                            font=("Segoe UI Emoji", 14), padx=PAD_SM, pady=PAD_SM)
        lbl_icon.pack(side="left")
        lbl_text = tk.Label(frame, text=label, bg=BG_SIDEBAR, fg=TEXT_SECONDARY,
                            font=FONT_BODY, pady=PAD_SM)
        lbl_text.pack(side="left")

        for widget in (frame, lbl_icon, lbl_text):
            widget.bind("<Enter>",  on_enter)
            widget.bind("<Leave>",  on_leave)
            widget.bind("<Button-1>", on_click)

        # Guarda referencias a los sub-widgets para cambiar color activo
        frame._icon = lbl_icon
        frame._text = lbl_text
        return frame

    def _show(self, key: str):
        if self._current_key == key:
            return

        # Desmarcar anterior
        if self._current_key and self._current_key in self._btn_refs:
            prev = self._btn_refs[self._current_key]
            prev.config(bg=BG_SIDEBAR)
            prev._icon.config(bg=BG_SIDEBAR, fg=TEXT_SECONDARY)
            prev._text.config(bg=BG_SIDEBAR, fg=TEXT_SECONDARY)

        # Marcar activo
        btn = self._btn_refs[key]
        btn.config(bg=ACCENT)
        btn._icon.config(bg=ACCENT, fg=BG_DARK)
        btn._text.config(bg=ACCENT, fg=BG_DARK, font=FONT_BTN)

        # Ocultar vista anterior
        if self._current_key and self._current_key in self._view_cache:
            self._view_cache[self._current_key].pack_forget()

        self._current_key = key

        # Crear o mostrar vista
        if key not in self._view_cache:
            cls = self._views_cls[key]
            view = cls(self.content, navigate=self._show)
            view.pack(fill="both", expand=True)
            self._view_cache[key] = view
        else:
            view = self._view_cache[key]
            view.pack(fill="both", expand=True)
            if hasattr(view, "refresh"):
                view.refresh()

    def navigate(self, key: str):
        self._show(key)
