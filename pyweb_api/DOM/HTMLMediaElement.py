from tkinter import Widget
import tkinter as tk

from PIL import ImageTk, Image

from pyweb_api.DOM.HTMLElement import HTMLElement
from pyweb_client.network import fetch_binary


class HTMLMediaElement(HTMLElement):
    def get_default_styles(self):
        return {
            'display': "inline"
        }

class HTMLIMGElement(HTMLMediaElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("img", attrs, children)

    def render(self, parent_widget: Widget, context):
        src = self.attrs.get("src", "-")

        image = None
        if src.startswith("http"):
            image = Image.open(fetch_binary(src))
        elif src.startswith("/") or src.startswith("file://"):
            image = Image.open(src)

        img = ImageTk.PhotoImage(image)
        panel = tk.Label(parent_widget, image=img)
        panel.pack(side="bottom", fill="both", expand=0)
