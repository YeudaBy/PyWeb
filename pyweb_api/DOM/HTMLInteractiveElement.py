from PyQt6.QtWidgets import QWidget, QPushButton, QLineEdit, QTextEdit
from PyQt6.QtCore import Qt

from pyweb_api.DOM import HTMLEvent
from pyweb_api.DOM.HTMLBlockElement import HTMLBLockElement
from pyweb_api.DOM.HTMLElement import HTMLElement


class HTMLInteractiveElement(HTMLElement):
    def __init__(self, tag, attrs=None, children=None):
        super().__init__(tag, attrs, children)

    def get_default_styles(self):
        return {
            "cursor": "pointer" if self.attrs.get("disabled") == True else "not-allowed"
        }

    def render(self, parent_widget: QWidget, context):
        raise NotImplementedError("Should implement by HTMLInteractiveElement subclass")

    @property
    def disabled(self):
        return self.attrs.get("disabled") == True


class HTMLButtonElement(HTMLInteractiveElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("button", attrs, children)

    def render(self, parent_widget, context):
        label = self.attrs.get("value", "Click")
        
        def click_callback():
            from pyweb_api.DOM.HTMLEvent import Event
            event = Event("click", self)
            self.dispatch_event(event)

        btn = QPushButton(label, parent_widget)
        btn.clicked.connect(click_callback)
        if self.attrs.get("disabled") == True:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn


class HTMLFormElement(HTMLInteractiveElement, HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("form", attrs, children)

    def render(self, parent_widget, context):
        return HTMLBLockElement.render(self, parent_widget, context)


class HTMLInputElement(HTMLInteractiveElement, HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("input", attrs, children)

    def render(self, parent_widget, context):
        btn = QLineEdit(parent_widget)
        val = self.attrs.get("value", "")
        if val:
            btn.setText(val)
        return btn


class HTMLTextAreaElement(HTMLInteractiveElement, HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("textarea", attrs, children)

    def render(self, parent_widget, context):
        btn = QTextEdit(parent_widget)
        val = "".join([c if isinstance(c, str) else "" for c in self.children])
        if val:
            btn.setPlainText(val)
        return btn
