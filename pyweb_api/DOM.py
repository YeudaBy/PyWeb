from typing import List, Dict, Optional

class Event:
    def __init__(self, type_, target):
        self.type = type_
        self.target = target
        self.current_target = None
        self._stopped = False

    def stop_propagation(self):
        self._stopped = True



class Element:
    def __init__(self,
                 tag: str,
                 attrs: Optional[Dict[str, str]] = None,
                 parent=None,
                 _id: str | None = None):
        self.tag = tag
        self.id = _id
        self.attrs = attrs or {}
        self.children: List[Element | str] = []
        self.parent = parent
        self.listeners = {}

    def append_child(self, child: 'Element | str'):
        if isinstance(child, Element):
            child.parent = self
        self.children.append(child)
        return child

    def add_event_listener(self, type_, handler, phase="bubble"):
        key = (type_, phase)
        if key not in self.listeners:
            self.listeners[key] = []
        self.listeners[key].append(handler)

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
        for handler in self.listeners.get((event.type, "bubble"), []):
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
        current: Element = self.parent
        path: List[Element | None] = []
        while current is not None:
            path.append(current)
            current = current.parent
        return path

    def __repr__(self):
        return f"<{self.tag} {self.attrs} children={len(self.children)}/>"


class Input(Element):
    def __init__(self, attrs=None, parent=None):
        super().__init__('button', attrs, parent)


class Div(Element):
    def __init__(self, attrs=None, parent=None):
        super().__init__('div', attrs, parent)


class P(Element):
    def __init__(self, attrs=None, parent=None):
        super().__init__('p', attrs, parent)


class Button(Element):
    def __init__(self, attrs=None, parent=None):
        super().__init__('button', attrs, parent)


class A(Element):
    def __init__(self, attrs=None, parent=None):
        super().__init__('a', attrs, parent)


class H1(Element):
    def __init__(self, attrs=None, parent=None):
        super().__init__('h1', attrs, parent)


class H2(Element):
    def __init__(self, attrs=None, parent=None):
        super().__init__('h2', attrs, parent)


class H3(Element):
    def __init__(self, attrs=None, parent=None):
        super().__init__('h3', attrs, parent)


class DocumentEL(Element):
    def __init__(self, attrs=None):
        super().__init__("document", attrs)


TAG_MAP = {
    "div": Div,
    "p": P,
    "button": Button,
    "input": Input,
    "a": A,
    "h1": H1,
    "h2": H2,
    "h3": H3,
    "document": DocumentEL
}