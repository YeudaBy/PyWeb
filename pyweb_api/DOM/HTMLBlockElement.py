import tkinter as tk

from pyweb_api.DOM.HTMLElement import HTMLElement


class HTMLBLockElement(HTMLElement):
    def get_default_styles(self):
        return {
            'display': "block"
        }

    def render(self, parent_widget, context) -> tk.Widget:
        frame = tk.Frame(parent_widget, name=self.tag)
        frame.pack(fill="x", padx=5, pady=5)
        return frame


class HTMLDivElement(HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("div", attrs, children)


class HTMLSectionElement(HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("section", attrs, children)


class HTMLArticleElement(HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("article", attrs, children)


class HTMLHeaderElement(HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("header", attrs, children)


class HTMLFooterElement(HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("footer", attrs, children)


class HTMLMainElement(HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("main", attrs, children)


class HTMLNavElement(HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("nav", attrs, children)


class HTMLAsideElement(HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("aside", attrs, children)


class HTMLULElement(HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("ul", attrs, children)


class HTMLOLElement(HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("ol", attrs, children)


class HTMLLIElement(HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("li", attrs, children)
