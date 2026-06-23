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
        from urllib.parse import urljoin
        current_url = context.window.location.href if (context and hasattr(context, "window") and context.window) else None
        
        if not src.startswith("http") and not src.startswith("file://") and not src.startswith("data:"):
            if current_url:
                src = urljoin(current_url, src)

        image = None
        try:
            if src.startswith("http"):
                image = Image.open(fetch_binary(src))
            elif src.startswith("/") or src.startswith("file://"):
                path = src[len("file://"):] if src.startswith("file://") else src
                image = Image.open(path)
            else:
                image = Image.open(src)
        except Exception as e:
            context.window.console.warn(f"Failed to load image '{src}': {e}")
            import os
            current_dir = os.path.dirname(__file__)
            fallback_path = os.path.join(current_dir, "broken-image.png")
            try:
                image = Image.open(fallback_path)
            except:
                pass

        if image:
            try:
                styles = self._get_style_dict()
                width = int(styles.get("width", "150").replace("px", "").strip())
                height = int(styles.get("height", "100").replace("px", "").strip())
                image = image.resize((width, height))
            except:
                pass
            
            img = ImageTk.PhotoImage(image)
            panel = tk.Label(parent_widget, image=img)
            panel.image = img  # Keep reference to prevent GC
            panel.pack(side="bottom", fill="both", expand=0)
            return panel
        else:
            panel = tk.Label(parent_widget, text="[Image]")
            panel.pack(side="bottom", fill="both", expand=0)
            return panel
