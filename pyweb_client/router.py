from abc import ABC, abstractmethod
from typing import Union, Dict
from pyweb_api.DOM import HTMLElement

class SchemeResponse:
    def __init__(self, content: Union[str, HTMLElement], content_type: str = "text/html"):
        self.content = content
        self.content_type = content_type


class ISchemeHandler(ABC):
    @abstractmethod
    def handle(self, url: str) -> SchemeResponse:
        pass


class AppSchemeHandler(ISchemeHandler):
    def __init__(self, client):
        self.client = client

    def handle(self, url: str) -> SchemeResponse:
        if url == "app://home":
            from pyweb_api.DOM import HTMLDivElement, HTMLPElementHTML, HTMLButtonElement
            root_dom_element = HTMLDivElement()
            p = HTMLPElementHTML()
            p.append_child("ברוך הבא ל-PyWeb Client!")
            root_dom_element.append_child(p)

            btn = HTMLButtonElement(attrs={"value": "Click"})

            def click_test(event):
                self.client.window.console.log("Button clicked!")
                btn.set_text("Clicked!")

            root_dom_element.append_child(btn)
            btn.add_event_listener("click", click_test)
            return SchemeResponse(root_dom_element)

        elif url == "app://example_page":
            from pyweb_api.DOM import HTMLDivElement, HTMLPElementHTML, HTMLButtonElement
            root_dom_element = HTMLDivElement()
            p = HTMLPElementHTML()
            p.append_child("זהו דף לדוגמה.")
            root_dom_element.append_child(p)
            btn = HTMLButtonElement(attrs={"value": "חזור לדף הבית"})
            btn.add_event_listener("click", lambda e: self.client.window.location.navigate("app://home"))
            root_dom_element.append_child(btn)
            return SchemeResponse(root_dom_element)

        else:
            raise ValueError(f"Unknown app route: {url}")


class FileSchemeHandler(ISchemeHandler):
    def handle(self, url: str) -> SchemeResponse:
        file_path = url[len("file://"):]
        with open(file_path, 'r', encoding="utf-8") as f:
            content = f.read()
        return SchemeResponse(content)


class HttpSchemeHandler(ISchemeHandler):
    def handle(self, url: str) -> SchemeResponse:
        from pyweb_client.network import fetch_text
        content = fetch_text(url)
        return SchemeResponse(content)


class RelativeSchemeHandler(ISchemeHandler):
    def __init__(self, client):
        self.client = client

    def handle(self, url: str) -> SchemeResponse:
        from urllib.parse import urljoin
        current_url = self.client.window.location.href
        if not current_url:
            raise ValueError("No active page to resolve relative URL")
        full_url = urljoin(current_url, url)
        return self.client.router.resolve(full_url)


class ProtocolRouter:
    def __init__(self):
        self._handlers: Dict[str, ISchemeHandler] = {}

    def register_handler(self, scheme: str, handler: ISchemeHandler):
        self._handlers[scheme] = handler

    def resolve(self, url: str) -> SchemeResponse:
        if "://" in url:
            scheme = url.split("://", 1)[0]
        elif url.startswith("/") or not url.startswith("http"):
            # If it's a relative path/subpath
            scheme = "relative"
        else:
            scheme = "unknown"

        handler = self._handlers.get(scheme)
        if not handler:
            # Check fallback to relative if scheme is not registered
            if "relative" in self._handlers:
                return self._handlers["relative"].handle(url)
            raise ValueError(f"No handler registered for scheme: {scheme}")
        return handler.handle(url)
