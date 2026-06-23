from PyQt6.QtWidgets import QWidget
from typing import TYPE_CHECKING

from pyweb_api.DOM.HTMLElement import HTMLElement
from pyweb_client.network import fetch_text

if TYPE_CHECKING:
    from pyweb_client.main import PyWebClient


class HTMLMetaElement(HTMLElement):
    def get_default_styles(self):
        return {
            'display': "none"
        }


class HTMLTitleElement(HTMLMetaElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("title", attrs, children)

    def render(self, parent_widget: QWidget, context):
        text = " ".join([c if isinstance(c, str) else "" for c in self.children])
        context.root.setWindowTitle(text)


class HTMLScriptElement(HTMLMetaElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("script", attrs, children)

    @property
    def is_python(self):
        return self.attrs.get("type") in ["text/python", "python", "text/pyweb"]

    def render(self, parent_widget: QWidget, context: 'PyWebClient'):
        import sys
        import types
        from pyweb_api.DOM import get_globals

        if not self.is_python:
            context.window.console.warn(f"Ignored script type {self.attrs.get('type')}")
            return

        content = ""
        src = self.attrs.get("src")
        if src is not None:
            if src.startswith("http"):
                content = fetch_text(src)
            elif src.startswith("/") or src.startswith("file://"):
                with open(src, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                context.window.console.warn(f"Ignored python script with src {src}")
        else:
            content = "".join([c if isinstance(c, str) else "" for c in self.children])

        # Create virtual pyweb module and insert into sys.modules
        pyweb_module = types.ModuleType("pyweb")
        pyweb_module.Window = context.window
        pyweb_module.Document = context.window.document
        sys.modules["pyweb"] = pyweb_module

        context.window.console.log(f"executing script: {src or 'inline'}")
        globals_dict = get_globals(context)
        globals_dict["pyweb"] = pyweb_module
        try:
            exec(content, globals_dict)
        except Exception as e:
            context.window.console.error(f"Script error: {e}")
