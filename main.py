"""
Entry point del Sistema de Inventarios.
Ejecutar con:  python main.py
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Asegurar que la raíz del proyecto esté en sys.path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def main():
    # Inicializar base de datos
    try:
        from app.db.database import init_db
        init_db()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error de Base de Datos",
                             f"No se pudo inicializar la base de datos:\n{e}")
        root.destroy()
        sys.exit(1)

    # Lanzar ventana principal
    try:
        from app.views.main_window import MainWindow
        app = MainWindow()

        # Icono y estilo de tkinter
        try:
            # Intentar usar el icono si existe
            icon_path = os.path.join(ROOT, "app", "resources", "icon.ico")
            if os.path.exists(icon_path):
                app.iconbitmap(icon_path)
        except Exception:
            pass

        # Estilo de ttk global (scrollbars, comboboxes, etc.)
        _apply_global_ttk_style()

        app.mainloop()
    except Exception as e:
        import traceback
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error de Aplicación",
                             f"Error al iniciar:\n{e}\n\n{traceback.format_exc()}")
        root.destroy()
        sys.exit(1)


def _apply_global_ttk_style():
    """Aplica el tema oscuro a los widgets ttk globales."""
    import tkinter.ttk as ttk
    from app.core.theme import (
        BG_DARK, BG_CARD, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT
    )
    s = ttk.Style()
    s.theme_use("clam")

    # Scrollbars
    s.configure("Vertical.TScrollbar",
                 background=BG_CARD, troughcolor=BG_DARK,
                 arrowcolor=TEXT_SECONDARY, bordercolor=BG_DARK)
    s.configure("Horizontal.TScrollbar",
                 background=BG_CARD, troughcolor=BG_DARK,
                 arrowcolor=TEXT_SECONDARY, bordercolor=BG_DARK)

    # Combobox
    s.configure("TCombobox",
                 fieldbackground=BG_INPUT,
                 background=BG_CARD,
                 foreground=TEXT_PRIMARY,
                 arrowcolor=TEXT_SECONDARY,
                 selectbackground=ACCENT,
                 selectforeground=BG_DARK)
    s.map("TCombobox",
          fieldbackground=[("readonly", BG_INPUT)],
          selectbackground=[("readonly", BG_INPUT)],
          foreground=[("readonly", TEXT_PRIMARY)])

    # PanedWindow sash
    s.configure("Sash", sashthickness=6, background=BG_CARD)


if __name__ == "__main__":
    main()
