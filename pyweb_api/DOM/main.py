from PyQt6.QtWidgets import QWidget

from pyweb_api.DOM import HTMLElement


class HTMLDocumentElement(HTMLElement):
    def __init__(self, attrs=None):
        super().__init__("document", attrs, None)
        self._cookies = {}

    @property
    def cookie(self) -> str:
        return "; ".join([f"{k}={v}" for k, v in self._cookies.items()])

    @cookie.setter
    def cookie(self, cookie_str: str):
        if not cookie_str:
            return
        parts = cookie_str.split(";")
        if parts:
            kv = parts[0].strip()
            if "=" in kv:
                k, v = kv.split("=", 1)
                self._cookies[k.strip()] = v.strip()

    def render(self, parent_widget: QWidget, context) -> QWidget:
        pass
