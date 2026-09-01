"""
Widgets reutilizables para toda la aplicación.
Construidos sobre tkinter nativo para máxima compatibilidad.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from .theme import *


# ─────────────────────────────────────────────
# Botones
# ─────────────────────────────────────────────

class AppButton(tk.Button):
    def __init__(self, parent, text="", command=None, style="primary", **kw):
        colors = {
            "primary": (ACCENT,      BG_DARK,   ACCENT_HOVER),
            "success": (SUCCESS,     BG_DARK,   "#b9f0b4"),
            "danger":  (DANGER,      BG_DARK,   "#f5a0b5"),
            "warning": (WARNING,     BG_DARK,   "#fbebb0"),
            "ghost":   (BG_CARD,     TEXT_PRIMARY, BG_INPUT),
        }
        bg, fg, hov = colors.get(style, colors["primary"])
        super().__init__(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=hov, activeforeground=fg,
            font=FONT_BTN, relief="flat", cursor="hand2",
            padx=PAD, pady=PAD_SM, bd=0, **kw
        )
        self._bg  = bg
        self._hov = hov
        self.bind("<Enter>", lambda e: self.config(bg=self._hov))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))


class IconButton(tk.Button):
    """Botón pequeño con icono/emoji."""
    def __init__(self, parent, text="", command=None, bg=BG_CARD, **kw):
        super().__init__(
            parent, text=text, command=command,
            bg=bg, fg=TEXT_PRIMARY, activebackground=BG_INPUT, activeforeground=TEXT_PRIMARY,
            font=("Segoe UI Emoji", 12), relief="flat", cursor="hand2",
            padx=6, pady=4, bd=0, **kw
        )


# ─────────────────────────────────────────────
# Entradas
# ─────────────────────────────────────────────

class LabeledEntry(tk.Frame):
    """Label + Entry en columna."""
    def __init__(self, parent, label="", width=220, **kw):
        super().__init__(parent, bg=BG_CARD, **kw)
        tk.Label(self, text=label, bg=BG_CARD, fg=TEXT_SECONDARY, font=FONT_SMALL).pack(anchor="w")
        self.var = tk.StringVar()
        self.entry = tk.Entry(
            self, textvariable=self.var,
            bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
            relief="flat", font=FONT_BODY, width=width // 8
        )
        self.entry.pack(fill="x", ipady=5, pady=(2, 0))

    def get(self):   return self.var.get()
    def set(self, v): self.var.set(str(v) if v is not None else "")
    def clear(self): self.var.set("")


class LabeledCombo(tk.Frame):
    """Label + Combobox en columna."""
    def __init__(self, parent, label="", values=None, width=26, **kw):
        super().__init__(parent, bg=BG_CARD, **kw)
        tk.Label(self, text=label, bg=BG_CARD, fg=TEXT_SECONDARY, font=FONT_SMALL).pack(anchor="w")
        self.var = tk.StringVar()
        style_name = f"App.TCombobox"
        self.combo = ttk.Combobox(
            self, textvariable=self.var,
            values=values or [], font=FONT_BODY, width=width, state="readonly"
        )
        self.combo.pack(fill="x", pady=(2, 0))

    def get(self):        return self.var.get()
    def set(self, v):     self.var.set(str(v) if v is not None else "")
    def set_values(self, vals): self.combo["values"] = vals
    def clear(self):      self.var.set("")


class LabeledText(tk.Frame):
    """Label + Text multilínea."""
    def __init__(self, parent, label="", height=3, **kw):
        super().__init__(parent, bg=BG_CARD, **kw)
        tk.Label(self, text=label, bg=BG_CARD, fg=TEXT_SECONDARY, font=FONT_SMALL).pack(anchor="w")
        self.text = tk.Text(
            self, height=height,
            bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
            relief="flat", font=FONT_BODY, wrap="word"
        )
        self.text.pack(fill="x", pady=(2, 0))

    def get(self):   return self.text.get("1.0", "end").strip()
    def set(self, v): self.text.delete("1.0","end"); self.text.insert("1.0", str(v) if v else "")
    def clear(self): self.text.delete("1.0","end")


# ─────────────────────────────────────────────
# Tabla (Treeview estilizado)
# ─────────────────────────────────────────────

class AppTable(tk.Frame):
    def __init__(self, parent, columns: list, show_index=False, **kw):
        """
        columns: list of (id, heading, width, anchor)
        """
        super().__init__(parent, bg=BG_DARK, **kw)
        self._setup_style()
        self.tree = ttk.Treeview(
            self, columns=[c[0] for c in columns],
            show="headings", style="App.Treeview",
            selectmode="browse"
        )
        vsb = ttk.Scrollbar(self, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for col_id, heading, width, anchor in columns:
            self.tree.heading(col_id, text=heading, anchor=anchor)
            self.tree.column(col_id,  width=width,  anchor=anchor, minwidth=40)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Colores alternados
        self.tree.tag_configure("even", background=BG_TABLE)
        self.tree.tag_configure("odd",  background=BG_TABLE_ALT)
        self.tree.tag_configure("low",  background="#3d2020", foreground=DANGER)

    def _setup_style(self):
        s = ttk.Style()
        s.configure("App.Treeview",
            background=BG_TABLE, foreground=TEXT_PRIMARY,
            fieldbackground=BG_TABLE, rowheight=ROW_HEIGHT,
            font=FONT_BODY, borderwidth=0)
        s.configure("App.Treeview.Heading",
            background=BG_CARD, foreground=ACCENT,
            font=FONT_BODY, relief="flat")
        s.map("App.Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", BG_DARK)])

    def load(self, rows: list, tag_fn=None):
        """Carga filas. rows: list of tuples/dicts."""
        self.clear()
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            if tag_fn:
                extra = tag_fn(row)
                if extra:
                    tag = extra
            if isinstance(row, dict):
                vals = list(row.values())
            else:
                vals = list(row)
            self.tree.insert("", "end", values=vals, tags=(tag,))

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def selected_values(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"]

    def bind_double(self, callback):
        self.tree.bind("<Double-1>", lambda e: callback())

    def bind_select(self, callback):
        self.tree.bind("<<TreeviewSelect>>", lambda e: callback())


# ─────────────────────────────────────────────
# Cards de KPI
# ─────────────────────────────────────────────

class KpiCard(tk.Frame):
    def __init__(self, parent, title="", value="", color=ACCENT, icon="📦", **kw):
        super().__init__(parent, bg=BG_CARD, padx=PAD, pady=PAD, **kw)
        # Icono
        tk.Label(self, text=icon, bg=BG_CARD, fg=color,
                 font=("Segoe UI Emoji", 22)).grid(row=0, column=0, rowspan=2, padx=(0, PAD))
        # Título
        tk.Label(self, text=title, bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=FONT_SMALL).grid(row=0, column=1, sticky="w")
        # Valor
        self._lbl = tk.Label(self, text=str(value), bg=BG_CARD, fg=color,
                              font=("Segoe UI", 20, "bold"))
        self._lbl.grid(row=1, column=1, sticky="w")

    def update_value(self, v):
        self._lbl.config(text=str(v))


# ─────────────────────────────────────────────
# Helpers de diálogo
# ─────────────────────────────────────────────

def ask_confirm(title, msg):
    return messagebox.askyesno(title, msg)

def show_error(title, msg):
    messagebox.showerror(title, msg)

def show_info(title, msg):
    messagebox.showinfo(title, msg)


# ─────────────────────────────────────────────
# Barra de búsqueda
# ─────────────────────────────────────────────

class SearchBar(tk.Frame):
    def __init__(self, parent, placeholder="Buscar...", on_search=None, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        tk.Label(self, text="🔍", bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Segoe UI Emoji", 12)).pack(side="left", padx=(0,4))
        self.var = tk.StringVar()
        self.entry = tk.Entry(
            self, textvariable=self.var,
            bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
            relief="flat", font=FONT_BODY, width=30
        )
        self.entry.pack(side="left", ipady=5)
        self.entry.insert(0, placeholder)
        self.entry.config(fg=TEXT_MUTED)
        self.entry.bind("<FocusIn>",  self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self._placeholder = placeholder
        self._on_search    = on_search
        if on_search:
            self.var.trace_add("write", lambda *_: on_search(self.get()))

    def _on_focus_in(self, e):
        if self.entry.get() == self._placeholder:
            self.entry.delete(0, "end")
            self.entry.config(fg=TEXT_PRIMARY)

    def _on_focus_out(self, e):
        if not self.entry.get():
            self.entry.insert(0, self._placeholder)
            self.entry.config(fg=TEXT_MUTED)

    def get(self):
        val = self.var.get()
        return "" if val == self._placeholder else val
