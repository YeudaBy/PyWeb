import tkinter as tk
from tkinter import Widget

from pyweb_api.DOM import HTMLEvent
from pyweb_api.DOM.HTMLBlockElement import HTMLBLockElement
from pyweb_api.DOM.HTMLElement import HTMLElement


class HTMLInteractiveElement(HTMLElement):
    def __init__(self, tag, attrs=None, children=None):
        super().__init__(tag, attrs, children)
        self.event_handlers = {}

    def add_event_listener(self, type_, handler, phase="bubble"):
        key = (type_, phase)
        if key not in self.event_handlers:
            self.event_handlers[key] = []
        self.event_handlers[key].append(handler)

    def dispatch_event(self, event: HTMLEvent):
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

    def get_default_styles(self):
        return {
            "cursor": "pointer" if self.attrs.get("disabled") == True else "not-allowed"
        }

    def render(self, parent_widget: Widget, context):
        raise NotImplementedError("Should implement by HTMLInteractiveElement subclass")

    @property
    def disabled(self):
        return self.attrs.get("disabled") == True


class HTMLButtonElement(HTMLInteractiveElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("button", attrs, children)

    def render(self, parent_widget, context):
        label = self.attrs.get("value", "Click")
        btn = tk.Button(
            parent_widget,
            text=label,
            command=self.event_handlers.get("click"),
            cursor="hand2" if self.attrs.get("disabled") == True else "X_cursor"
        )
        btn.pack(pady=5)
        return btn


class HTMLFormElement(HTMLInteractiveElement, HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("form", attrs, children)


class HTMLInputElement(HTMLInteractiveElement, HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("input", attrs, children)

    def render(self, parent_widget, context):
        btn = tk.Entry(
            parent_widget,
            cursor="xterm" if self.attrs.get("disabled") == True else "X_cursor",
            width=60, relief="sunken", bd=2, bg="white"
        )
        btn.pack(pady=5)
        # todo handle value
        return btn

class HTMLTextAreaElement(HTMLInteractiveElement, HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("textarea", attrs, children)

    def render(self, parent_widget, context):
        btn = tk.Text(
            parent_widget,
            cursor="xterm" if self.attrs.get("disabled") == True else "X_cursor",
            width=60, relief="sunken", bd=2, bg="white"
        )
        btn.pack(pady=5)
        # todo handle value
        return btn
