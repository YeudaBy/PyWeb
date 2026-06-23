from PyQt6.QtWidgets import QWidget, QPushButton, QLineEdit, QTextEdit
from PyQt6.QtCore import Qt

from pyweb_api.DOM import HTMLEvent
from pyweb_api.DOM.HTMLBlockElement import HTMLBLockElement
from pyweb_api.DOM.HTMLElement import HTMLElement


def find_form_controls(element):
    controls = []
    if element.tag in ["input", "textarea", "button"]:
        controls.append(element)
    for child in element.children:
        if isinstance(child, HTMLElement):
            controls.extend(find_form_controls(child))
    return controls


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

    @property
    def form(self):
        parent = self.parent
        while parent:
            if parent.tag == "form":
                return parent
            parent = parent.parent
        return None


class HTMLButtonElement(HTMLInteractiveElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("button", attrs, children)

    def render(self, parent_widget, context):
        label = self.attrs.get("value") or self.attrs.get("label")
        if not label and self.children:
            label = "".join([c if isinstance(c, str) else "" for c in self.children])
        if not label:
            label = "Click"
        
        def click_callback():
            from pyweb_api.DOM.HTMLEvent import Event
            event = Event("click", self)
            self.dispatch_event(event)
            if not event.default_prevented:
                btn_type = self.attrs.get("type", "submit").lower()
                if btn_type == "submit":
                    form = self.form
                    if form:
                        form.submit(context)

        btn = QPushButton(label, parent_widget)
        btn.clicked.connect(click_callback)
        if self.attrs.get("disabled") == True:
            btn.setEnabled(False)
        return btn


class HTMLFormElement(HTMLInteractiveElement, HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("form", attrs, children)

    def render(self, parent_widget, context):
        self._context = context
        return HTMLBLockElement.render(self, parent_widget, context)

    def submit(self, context=None):
        from pyweb_api.DOM.HTMLEvent import Event
        event = Event("submit", self)
        self.dispatch_event(event)
        
        if event.default_prevented:
            return
            
        controls = find_form_controls(self)
        form_data = []
        for ctrl in controls:
            name = ctrl.attrs.get("name")
            if name:
                form_data.append((name, ctrl.value))
                
        action = self.attrs.get("action", "")
        method = self.attrs.get("method", "GET").upper()
        
        window = None
        if context and hasattr(context, "window"):
            window = context.window
        elif getattr(self, "_context", None) and hasattr(self._context, "window"):
            window = self._context.window
        else:
            import sys
            if "pyweb" in sys.modules:
                pyweb_module = sys.modules["pyweb"]
                window = getattr(pyweb_module, "Window", None)
                
        if not window:
            return

        if not action:
            action = window.location.href or "app://home"
            
        from urllib.parse import urlencode, urlparse, urlunparse
        from pyweb_api.network import Request
        
        serialized = urlencode(form_data)
        
        if method == "POST":
            req = Request(
                url=action,
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                body=serialized
            )
            window.location.navigate(req)
        else:
            parsed = urlparse(action)
            query = parsed.query
            if query:
                new_query = query + "&" + serialized if serialized else query
            else:
                new_query = serialized
            
            new_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
            window.location.navigate(new_url)


class HTMLInputElement(HTMLInteractiveElement, HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("input", attrs, children)

    def render(self, parent_widget, context):
        input_type = self.attrs.get("type", "text").lower()
        if input_type == "submit":
            val = self.attrs.get("value", "Submit")
            btn = QPushButton(val, parent_widget)
            
            def submit_click():
                from pyweb_api.DOM.HTMLEvent import Event
                event = Event("click", self)
                self.dispatch_event(event)
                if not event.default_prevented:
                    form = self.form
                    if form:
                        form.submit(context)
            
            btn.clicked.connect(submit_click)
            if self.attrs.get("disabled") == True:
                btn.setEnabled(False)
            return btn
        else:
            line_edit = QLineEdit(parent_widget)
            val = self.attrs.get("value", "")
            if val:
                line_edit.setText(val)
            if input_type == "password":
                line_edit.setEchoMode(QLineEdit.EchoMode.Password)
                
            def return_pressed():
                form = self.form
                if form:
                    form.submit(context)
            
            line_edit.returnPressed.connect(return_pressed)
            if self.attrs.get("disabled") == True:
                line_edit.setEnabled(False)
            return line_edit

    @property
    def value(self):
        if hasattr(self, "_qt_widget") and self._qt_widget:
            from PyQt6.QtWidgets import QLineEdit, QPushButton
            if isinstance(self._qt_widget, QLineEdit):
                return self._qt_widget.text()
            elif isinstance(self._qt_widget, QPushButton):
                return self.attrs.get("value", "")
        return self.attrs.get("value", "")

    @value.setter
    def value(self, val):
        self.attrs["value"] = val
        if hasattr(self, "_qt_widget") and self._qt_widget:
            from PyQt6.QtWidgets import QLineEdit
            if isinstance(self._qt_widget, QLineEdit):
                self._qt_widget.setText(val)


class HTMLTextAreaElement(HTMLInteractiveElement, HTMLBLockElement):
    def __init__(self, attrs=None, children=None):
        super().__init__("textarea", attrs, children)

    def render(self, parent_widget, context):
        btn = QTextEdit(parent_widget)
        val = "".join([c if isinstance(c, str) else "" for c in self.children])
        if val:
            btn.setPlainText(val)
        if self.attrs.get("disabled") == True:
            btn.setEnabled(False)
        return btn

    @property
    def value(self):
        if hasattr(self, "_qt_widget") and self._qt_widget:
            from PyQt6.QtWidgets import QTextEdit
            if isinstance(self._qt_widget, QTextEdit):
                return self._qt_widget.toPlainText()
        return "".join([c if isinstance(c, str) else "" for c in self.children])

    @value.setter
    def value(self, val):
        self.children = [val]
        if hasattr(self, "_qt_widget") and self._qt_widget:
            from PyQt6.QtWidgets import QTextEdit
            if isinstance(self._qt_widget, QTextEdit):
                self._qt_widget.setPlainText(val)
