from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap

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

    def render(self, parent_widget: QWidget, context):
        src = self.attrs.get("src", "-")
        from urllib.parse import urljoin
        current_url = context.window.location.href if (context and hasattr(context, "window") and context.window) else None
        
        if not src.startswith("http") and not src.startswith("file://") and not src.startswith("data:"):
            if current_url:
                src = urljoin(current_url, src)

        image_bytes = None
        try:
            if src.startswith("http"):
                image_bytes = fetch_binary(src).getvalue()
            elif src.startswith("/") or src.startswith("file://"):
                path = src[len("file://"):] if src.startswith("file://") else src
                with open(path, "rb") as f:
                    image_bytes = f.read()
            else:
                with open(src, "rb") as f:
                    image_bytes = f.read()
        except Exception as e:
            if context and hasattr(context, "window") and context.window:
                context.window.console.warn(f"Failed to load image '{src}': {e}")

        pixmap = QPixmap()
        if image_bytes:
            pixmap.loadFromData(image_bytes)

        if not pixmap.isNull():
            try:
                styles = self._get_style_dict()
                width = int(styles.get("width", "150").replace("px", "").strip())
                height = int(styles.get("height", "100").replace("px", "").strip())
                from PyQt6.QtCore import Qt
                pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            except:
                pass
            
            panel = QLabel(parent_widget)
            panel.setPixmap(pixmap)
            panel.pixmap = pixmap  # Keep reference
            return panel
        else:
            panel = QLabel("[Image]", parent_widget)
            return panel
