from tkinter import Widget

from pyweb_api.DOM import HTMLElement


class HTMLDocumentElement(HTMLElement):
    def __init__(self, attrs=None):
        super().__init__("document", attrs, None)

    def render(self, parent_widget: Widget, context) -> Widget:
        pass
