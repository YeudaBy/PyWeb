import tkinter as tk

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
        styles = self._get_style_dict()
        font_family = styles.get("font-family", "Arial")
        if font_family == "Ariel":
            font_family = "Arial"
        font_size = 12
        if "font-size" in styles:
            try:
                val = styles["font-size"]
                if isinstance(val, int):
                    font_size = val
                elif isinstance(val, str):
                    for unit in ["px", "pt", "em", "rem"]:
                        val = val.replace(unit, "")
                    font_size = int(float(val.strip()))
            except:
                pass
        weight = "bold" if styles.get("font-weight") == "bold" or styles.get("font-width") == 600 else "normal"
        
        if self.tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            weight = "bold"
            font = (font_family, font_size, weight)
        else:
            font = (font_family, font_size)

        lbl = tk.Label(
            parent_widget,
            text=self.text,
            wraplength=600,
            cursor="xterm",
            fg=styles.get("color", "black"),
            font=font
        )
        lbl.pack(anchor="w", pady=4)
        return lbl

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
        styles = self.get_default_styles()
        font = ("Arial", 12, "underline")  # todo
        link_url = self.attrs.get('href', '#')
        lbl = tk.Label(parent_widget,
                       text=self.text,
                       cursor="hand2",  # todo
                       font=font,
                       fg=styles.get("color", "blue")
                       )
        lbl.bind("<Button-1>", lambda e: context.window.location.navigate(link_url))
        lbl.pack(anchor="w", pady=4)
        return lbl
