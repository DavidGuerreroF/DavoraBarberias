"""
Vista de Grupos de Inventario — CRUD completo.
"""

import tkinter as tk
from app.core.theme import *
from app.core.widgets import (
    AppButton, LabeledEntry, LabeledText,
    AppTable, SearchBar, ask_confirm, show_error, show_info
)
from app.db import crud


class GroupsView(tk.Frame):
    def __init__(self, parent, navigate=None, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self._navigate = navigate
        self._selected_id = None
        self._build()
        self.refresh()

    def _build(self):
        hdr = tk.Frame(self, bg=BG_DARK, pady=PAD)
        hdr.pack(fill="x", padx=PAD_LG)
        tk.Label(hdr, text="🗂️  Grupos de Inventario", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=FONT_TITLE).pack(side="left")
        AppButton(hdr, text="＋ Nuevo", command=self._new, style="primary").pack(side="right", padx=4)

        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.rowconfigure(1, weight=1)

        top = tk.Frame(body, bg=BG_DARK)
        top.grid(row=0, column=0, sticky="ew", pady=(0, PAD_SM))
        SearchBar(top, on_search=lambda q: self.refresh(q)).pack(side="left")

        cols = [
            ("code", "Código",      140, "w"),
            ("name", "Nombre",      280, "w"),
            ("desc", "Descripción", 360, "w"),
            ("date", "Creado",      140, "center"),
        ]
        self._table = AppTable(body, columns=cols)
        self._table.grid(row=1, column=0, sticky="nsew")
        self._table.bind_double(self._on_select)
        self._table.bind_select(self._on_row_click)

        # Formulario
        self._panel = tk.Frame(body, bg=BG_CARD, width=300, padx=PAD, pady=PAD)
        self._panel.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(PAD, 0))
        self._panel.grid_propagate(False)
        self._build_form()

    def _build_form(self):
        p = self._panel
        tk.Label(p, text="Detalle del Grupo", bg=BG_CARD, fg=ACCENT,
                 font=FONT_HEAD).pack(anchor="w", pady=(0, PAD_SM))
        self._f_code = LabeledEntry(p, "Código *");      self._f_code.pack(fill="x", pady=2)
        self._f_name = LabeledEntry(p, "Nombre *");      self._f_name.pack(fill="x", pady=2)
        self._f_desc = LabeledText(p, "Descripción", 4); self._f_desc.pack(fill="x", pady=2)

        tk.Frame(p, bg=BG_INPUT, height=1).pack(fill="x", pady=PAD_SM)
        btn_row = tk.Frame(p, bg=BG_CARD); btn_row.pack(fill="x")
        AppButton(btn_row, text="💾 Guardar",  command=self._save,   style="success").pack(side="left", padx=(0,4))
        AppButton(btn_row, text="🗑 Eliminar", command=self._delete, style="danger").pack(side="left", padx=(0,4))
        AppButton(btn_row, text="✖ Limpiar",  command=self._clear,  style="ghost").pack(side="left")

    def refresh(self, search=""):
        groups = crud.get_all_groups()
        if search:
            sl = search.lower()
            groups = [g for g in groups if sl in g["name"].lower() or sl in g["group_code"].lower()]
        self._table.clear()
        for i, g in enumerate(groups):
            tag = "even" if i % 2 == 0 else "odd"
            self._table.tree.insert("", "end", iid=str(g["id"]), tags=(tag,), values=(
                g["group_code"], g["name"],
                g.get("description",""),
                (g.get("created_at","") or "")[:10],
            ))

    def _on_row_click(self):
        sel = self._table.tree.selection()
        if sel:
            self._load_to_form(int(sel[0]))

    def _on_select(self):
        self._on_row_click()

    def _load_to_form(self, gid: int):
        self._selected_id = gid
        g = crud.get_group(gid)
        if not g: return
        self._f_code.set(g["group_code"])
        self._f_name.set(g["name"])
        self._f_desc.set(g.get("description",""))

    def _new(self):
        self._selected_id = None
        self._clear()
        self._f_code.entry.focus_set()

    def _clear(self):
        self._selected_id = None
        self._f_code.clear()
        self._f_name.clear()
        self._f_desc.clear()

    def _save(self):
        code = self._f_code.get().strip()
        name = self._f_name.get().strip()
        if not code:
            show_error("Error", "El código del grupo es obligatorio.")
            return
        if not name:
            show_error("Error", "El nombre es obligatorio.")
            return
        try:
            if self._selected_id:
                crud.update_group(self._selected_id, code, name, self._f_desc.get())
                show_info("Éxito", "Grupo actualizado.")
            else:
                crud.create_group(code, name, self._f_desc.get())
                show_info("Éxito", "Grupo creado.")
            self._clear()
            self.refresh()
        except Exception as e:
            show_error("Error al guardar", str(e))

    def _delete(self):
        if not self._selected_id:
            show_error("Error", "Seleccione un grupo.")
            return
        if ask_confirm("Eliminar", "¿Eliminar este grupo? Los productos quedarán sin grupo."):
            try:
                crud.delete_group(self._selected_id)
                self._clear()
                self.refresh()
            except Exception as e:
                show_error("Error al eliminar", str(e))
