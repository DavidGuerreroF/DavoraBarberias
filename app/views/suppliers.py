"""
Vista de Proveedores — CRUD completo.
"""

import tkinter as tk
from app.core.theme import *
from app.core.widgets import (
    AppButton, LabeledEntry, LabeledCombo, LabeledText,
    AppTable, SearchBar, ask_confirm, show_error, show_info
)
from app.db import crud


class SuppliersView(tk.Frame):
    def __init__(self, parent, navigate=None, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self._navigate = navigate
        self._selected_id = None
        self._build()
        self.refresh()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG_DARK, pady=PAD)
        hdr.pack(fill="x", padx=PAD_LG)
        tk.Label(hdr, text="🏭  Proveedores", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=FONT_TITLE).pack(side="left")
        AppButton(hdr, text="＋ Nuevo", command=self._new, style="primary").pack(side="right", padx=4)
        AppButton(hdr, text="🔄 Refrescar", command=self.refresh, style="ghost").pack(side="right", padx=4)

        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.rowconfigure(1, weight=1)

        # Búsqueda
        top = tk.Frame(body, bg=BG_DARK)
        top.grid(row=0, column=0, sticky="ew", pady=(0, PAD_SM))
        SearchBar(top, on_search=lambda q: self.refresh(q)).pack(side="left")

        # Tabla
        cols = [
            ("code",  "Código",        110, "w"),
            ("id_no", "Identificación",140, "w"),
            ("dtype", "Tipo Doc",       90, "center"),
            ("name",  "Nombre",        240, "w"),
            ("phone", "Teléfono",      110, "w"),
            ("email", "Email",         200, "w"),
        ]
        self._table = AppTable(body, columns=cols)
        self._table.grid(row=1, column=0, sticky="nsew")
        self._table.bind_double(self._on_select)
        self._table.bind_select(self._on_row_click)

        # Panel formulario
        self._panel = tk.Frame(body, bg=BG_CARD, width=320, padx=PAD, pady=PAD)
        self._panel.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(PAD, 0))
        self._panel.grid_propagate(False)
        self._build_form()

    def _build_form(self):
        p = self._panel
        tk.Label(p, text="Detalle del Proveedor", bg=BG_CARD, fg=ACCENT,
                 font=FONT_HEAD).pack(anchor="w", pady=(0, PAD_SM))

        self._f_code  = LabeledEntry(p, "Código *");              self._f_code.pack(fill="x", pady=2)
        self._f_name  = LabeledEntry(p, "Nombre / Razón Social *"); self._f_name.pack(fill="x", pady=2)

        r1 = tk.Frame(p, bg=BG_CARD); r1.pack(fill="x", pady=2)
        self._f_dtype = LabeledCombo(r1, "Tipo Documento", width=13,
                                     values=["CC","NIT","CE","RUC","Pasaporte","Otro"])
        self._f_dtype.pack(side="left", expand=True, fill="x", padx=(0,4))
        self._f_idno  = LabeledEntry(r1, "Número ID", width=130)
        self._f_idno.pack(side="left", expand=True, fill="x")

        self._f_phone = LabeledEntry(p, "Teléfono");    self._f_phone.pack(fill="x", pady=2)
        self._f_email = LabeledEntry(p, "Email");       self._f_email.pack(fill="x", pady=2)
        self._f_addr  = LabeledText(p, "Dirección", height=3); self._f_addr.pack(fill="x", pady=2)

        tk.Frame(p, bg=BG_INPUT, height=1).pack(fill="x", pady=PAD_SM)

        btn_row = tk.Frame(p, bg=BG_CARD); btn_row.pack(fill="x")
        AppButton(btn_row, text="💾 Guardar",  command=self._save,   style="success").pack(side="left", padx=(0,4))
        AppButton(btn_row, text="🗑 Eliminar", command=self._delete, style="danger").pack(side="left", padx=(0,4))
        AppButton(btn_row, text="✖ Limpiar",  command=self._clear,  style="ghost").pack(side="left")

    def refresh(self, search=""):
        suppliers = crud.get_all_suppliers()
        if search:
            sl = search.lower()
            suppliers = [s for s in suppliers if sl in s["name"].lower()
                         or sl in (s.get("supplier_code","")).lower()
                         or sl in (s.get("identification_number","") or "").lower()]
        self._table.clear()
        self._raw = suppliers
        for i, s in enumerate(suppliers):
            tag = "even" if i % 2 == 0 else "odd"
            self._table.tree.insert("", "end", iid=str(s["id"]), tags=(tag,), values=(
                s["supplier_code"],
                s.get("identification_number",""),
                s.get("document_type",""),
                s["name"],
                s.get("phone",""),
                s.get("email",""),
            ))

    def _on_row_click(self):
        sel = self._table.tree.selection()
        if sel:
            self._load_to_form(int(sel[0]))

    def _on_select(self):
        self._on_row_click()

    def _load_to_form(self, sid: int):
        self._selected_id = sid
        s = crud.get_supplier(sid)
        if not s: return
        self._f_code.set(s["supplier_code"])
        self._f_name.set(s["name"])
        self._f_dtype.set(s.get("document_type",""))
        self._f_idno.set(s.get("identification_number",""))
        self._f_phone.set(s.get("phone",""))
        self._f_email.set(s.get("email",""))
        self._f_addr.set(s.get("address",""))

    def _new(self):
        self._selected_id = None
        self._clear()
        self._f_code.entry.focus_set()

    def _clear(self):
        self._selected_id = None
        for f in (self._f_code, self._f_name, self._f_idno,
                  self._f_phone, self._f_email):
            f.clear()
        self._f_dtype.clear()
        self._f_addr.clear()

    def _save(self):
        code = self._f_code.get().strip()
        name = self._f_name.get().strip()
        if not code:
            show_error("Error", "El código del proveedor es obligatorio.")
            return
        if not name:
            show_error("Error", "El nombre es obligatorio.")
            return
        data = {
            "supplier_code":         code,
            "name":                  name,
            "document_type":         self._f_dtype.get(),
            "identification_number": self._f_idno.get(),
            "phone":                 self._f_phone.get(),
            "email":                 self._f_email.get(),
            "address":               self._f_addr.get(),
        }
        try:
            if self._selected_id:
                crud.update_supplier(self._selected_id, data)
                show_info("Éxito", "Proveedor actualizado.")
            else:
                crud.create_supplier(data)
                show_info("Éxito", "Proveedor creado.")
            self._clear()
            self.refresh()
        except Exception as e:
            show_error("Error al guardar", str(e))

    def _delete(self):
        if not self._selected_id:
            show_error("Error", "Seleccione un proveedor.")
            return
        if ask_confirm("Eliminar", "¿Eliminar este proveedor? Esta acción no se puede deshacer."):
            try:
                crud.delete_supplier(self._selected_id)
                self._clear()
                self.refresh()
            except Exception as e:
                show_error("Error al eliminar", str(e))
