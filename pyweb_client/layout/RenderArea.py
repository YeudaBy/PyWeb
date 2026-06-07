import tkinter as tk
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyweb_client.main import PyWebClient


class RenderArea:
    def __init__(self, root, cl: 'PyWebClient'):
        self.root = root
        self.cl = cl
        self._render_area_canvas = None
        self.widget = None
        self._vsb = None

    def render_init(self):
        self._render_area_canvas = tk.Canvas(self.root, borderwidth=0)
        self.widget = tk.Frame(self._render_area_canvas)
        self._vsb = tk.Scrollbar(self.root, orient="vertical", command=self._render_area_canvas.yview)
        self._render_area_canvas.configure(yscrollcommand=self._vsb.set)


        # self._vsb.pack(side="right", fill="y", pady=(10, 0))
        # self._render_area_canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(10, 0))

        self._render_area_canvas.create_window((0, 0), window=self.widget, anchor="nw")

        self.widget.bind("<Configure>", self._on_render_area_conf)

        # Bind mouse wheel scrolling
        self.root.bind_all("<MouseWheel>", self._on_mouse_wheel)  # For Windows and MacOS
        self.root.bind_all("<Button-4>", self._on_mouse_wheel)  # For Linux (scroll up)
        self.root.bind_all("<Button-5>", self._on_mouse_wheel)  # For Linux (scroll down)


    def clear(self):
        for widget in self.widget.winfo_children():
            widget.destroy()

    def _on_render_area_conf(self, event):
        self._render_area_canvas.configure(scrollregion=self._render_area_canvas.bbox("all"))

    def _on_mouse_wheel(self, event):
        self.cl.window.console.log(f"Mouse Wheel Event: {event}")

        scroll_val = 0
        if event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):  # Scroll Down
            scroll_val = 1
        elif event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):  # Scroll Up
            scroll_val = -1

        if scroll_val != 0:
            self._render_area_canvas.yview_scroll(scroll_val, "units")
