from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

from pyweb_api.DOM.HTMLElement import HTMLElement
from pyweb_api.DOM.HTMLInteractiveElement import HTMLInteractiveElement


class HTMLTextElement(HTMLElement):
    def get_default_styles(self):
        return {
            "display": "inline",
            "cursor": "text",
            "color": "black"
        }

    def render(self, parent_widget, context):
        from PyQt6.QtWidgets import QWidget
        styles = self._get_style_dict()
        has_elements = any(not isinstance(c, str) for c in self.children)
        if not has_elements:
            lbl = QLabel(self.text, parent_widget)
            lbl.setWordWrap(True)
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            return lbl
        else:
            return QWidget(parent_widget)

    @property
    def text(self):
        return "".join([c if isinstance(c, str) else "" for c in self.children])


class HTMLHeadingElement(HTMLTextElement):
    def get_default_styles(self):
        s = super().get_default_styles()
        s["font-size"] = 16
        s["font-width"] = 600
        return s


class HTMLH1Element(HTMLHeadingElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("h1", attrs, children)

    def get_default_styles(self):
        s = super().get_default_styles()
        s["font-size"] = 22
        return s


class HTMLH2Element(HTMLHeadingElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("h2", attrs, children)

    def get_default_styles(self):
        s = super().get_default_styles()
        s["font-size"] = 18
        return s


class HTMLH3Element(HTMLHeadingElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("h3", attrs, children)

    def get_default_styles(self):
        s = super().get_default_styles()
        s["font-size"] = 16
        return s


class HTMLH4Element(HTMLHeadingElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("h4", attrs, children)

    def get_default_styles(self):
        s = super().get_default_styles()
        s["font-size"] = 16
        return s


class HTMLH5Element(HTMLHeadingElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("h5", attrs, children)

    def get_default_styles(self):
        s = super().get_default_styles()
        s["font-size"] = 14
        return s


class HTMLH6Element(HTMLHeadingElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("h6", attrs, children)

    def get_default_styles(self):
        s = super().get_default_styles()
        s["font-size"] = 12
        return s


class HTMLPElementHTML(HTMLTextElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("p", attrs, children)


class HTMLSpanElement(HTMLTextElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("span", attrs, children)

    def get_default_styles(self):
        return {
            "display": "inline"
        }


class HTMLStrongElement(HTMLTextElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("strong", attrs, children)

    def get_default_styles(self):
        return {
            "display": "inline",
            "font-width": 600
        }


class HTMLAElement(HTMLTextElement, HTMLInteractiveElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("a", attrs, children)

    def get_default_styles(self):
        return {
            "display": "inline",
            "text-decoration": "underline",
            "color": "blue",
            "cursor": "pointer"
        }

    def render(self, parent_widget, context):
        from PyQt6.QtWidgets import QWidget
        link_url = self.attrs.get('href', '#')
        has_elements = any(not isinstance(c, str) for c in self.children)
        if not has_elements:
            lbl = QLabel(self.text, parent_widget)
            lbl.setWordWrap(True)
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            lbl.mousePressEvent = lambda e: context.window.location.navigate(link_url)
            return lbl
        else:
            widget = QWidget(parent_widget)
            widget.setCursor(Qt.CursorShape.PointingHandCursor)
            widget.mousePressEvent = lambda e: context.window.location.navigate(link_url)
            return widget
