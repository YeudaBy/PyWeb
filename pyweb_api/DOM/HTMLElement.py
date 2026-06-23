from PyQt6.QtWidgets import QWidget
from typing import Optional, Dict, List, Any

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
        self.event_handlers = {}
        self.resolved_style: Dict[str, str] = {}

    @property
    def listeners(self):
        return self.event_handlers

    def add_event_listener(self, type_, handler, phase="bubble"):
        key = (type_, phase)
        if key not in self.event_handlers:
            self.event_handlers[key] = []
        self.event_handlers[key].append(handler)

    def dispatch_event(self, event):
        path = self._get_ancestry_path()

        # CAPTURING PHASE
        for el in reversed(path):
            event.current_target = el
            handlers = el.listeners.get((event.type, "capture"), [])
            for handler in handlers:
                handler(event)
                if event._stopped:
                    return

        # TARGET PHASE
        event.current_target = self
        for handler in self.event_handlers.get((event.type, "bubble"), []):
            handler(event)
            if event._stopped:
                return

        # BUBBLING PHASE
        for el in path:
            event.current_target = el
            handlers = el.listeners.get((event.type, "bubble"), [])
            for handler in handlers:
                handler(event)
                if event._stopped:
                    return

    def render(self, parent_widget: QWidget, context) -> QWidget:
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
        if hasattr(self, "_qt_widget") and self._qt_widget:
            if hasattr(self._qt_widget, "setText"):
                self._qt_widget.setText(new_text)

    def _get_style_dict(self) -> Dict[str, str]:
        if hasattr(self, "resolved_style") and self.resolved_style:
            return self.resolved_style

        styles = {}
        
        try:
            styles.update(self.get_default_styles())
        except:
            pass

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
