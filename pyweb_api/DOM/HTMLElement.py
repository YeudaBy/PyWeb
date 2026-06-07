from tkinter import Widget
from typing import Optional, Dict, List

from pyweb_api.DOM import HTMLEvent


class HTMLElement:
    def __init__(self,
                 tag: str,
                 attrs: Optional[Dict[str, str]] = None,
                 parent=None,
                 _id: str | None = None):
        self.tag = tag
        self.id = _id
        self.attrs = attrs or {}
        self.children: List[HTMLElement | str] = []
        self.parent = parent

    def render(self, parent_widget: Widget, context) -> Widget:
        raise NotImplementedError("Subclasses should implement this")

    def get_default_styles(self):
        raise NotImplementedError("Subclasses should implement this")

    def append_child(self, child: 'Element | str'):
        if isinstance(child, HTMLElement):
            child.parent = self
        self.children.append(child)
        return child



    def set_text(self, new_text: str):
        self.children = [new_text]
        if hasattr(self, "_tk_widget") and self._tk_widget:
            self._tk_widget.config(text=new_text)

    def _get_style_dict(self) -> Dict[str, str]:
        styles = {}

        for k, v in self.attrs.items():
            if k not in ["style", "id", "class"]:
                styles[k] = v

        style_attr = self.attrs.get("style", "")
        for rule in style_attr.split(";"):
            if ":" in rule:
                key, value = rule.split(":", 1)
                styles[key.strip()] = value.strip()

        return styles

    def _get_ancestry_path(self):
        current: HTMLElement = self.parent
        path: List[HTMLElement | None] = []
        while current is not None:
            path.append(current)
            current = current.parent
        return path

    def __repr__(self):
        return f"<{self.tag} {self.attrs} children={len(self.children)}/>"
