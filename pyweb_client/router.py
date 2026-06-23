from abc import ABC, abstractmethod
from typing import Union, Dict
from pyweb_api.DOM import HTMLElement

class SchemeResponse:
    def __init__(self, content: Union[str, HTMLElement], content_type: str = "text/html"):
        self.content = content
        self.content_type = content_type


class ISchemeHandler(ABC):
    @abstractmethod
    async def handle(self, url_or_request: Union[str, 'Request']) -> SchemeResponse:
        pass


class AppSchemeHandler(ISchemeHandler):
    def __init__(self, client):
        self.client = client

    async def handle(self, url_or_request: Union[str, 'Request']) -> SchemeResponse:
        from pyweb_api.network import Request
        url = url_or_request.url if isinstance(url_or_request, Request) else url_or_request
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
    async def handle(self, url_or_request: Union[str, 'Request']) -> SchemeResponse:
        from pyweb_api.network import Request
        url = url_or_request.url if isinstance(url_or_request, Request) else url_or_request
        file_path = url[len("file://"):]
        with open(file_path, 'r', encoding="utf-8") as f:
            content = f.read()
        return SchemeResponse(content)


class HttpSchemeHandler(ISchemeHandler):
    async def handle(self, url_or_request: Union[str, 'Request']) -> SchemeResponse:
        from pyweb_client.network import fetch_text
        content = await fetch_text(url_or_request)
        return SchemeResponse(content)


class RelativeSchemeHandler(ISchemeHandler):
    def __init__(self, client):
        self.client = client

    async def handle(self, url_or_request: Union[str, 'Request']) -> SchemeResponse:
        from pyweb_api.network import Request
        from urllib.parse import urljoin
        
        if isinstance(url_or_request, Request):
            url = url_or_request.url
        else:
            url = url_or_request

        current_url = self.client.window.location.href
        if not current_url:
            raise ValueError("No active page to resolve relative URL")
        full_url = urljoin(current_url, url)
        
        if isinstance(url_or_request, Request):
            url_or_request.url = full_url
            return await self.client.router.resolve(url_or_request)
        else:
            return await self.client.router.resolve(full_url)


class ProtocolRouter:
    def __init__(self):
        self._handlers: Dict[str, ISchemeHandler] = {}

    def register_handler(self, scheme: str, handler: ISchemeHandler):
        self._handlers[scheme] = handler

    async def resolve(self, url_or_request: Union[str, 'Request']) -> SchemeResponse:
        from pyweb_api.network import Request
        if isinstance(url_or_request, Request):
            url = url_or_request.url
        else:
            url = url_or_request

        if "://" in url:
            scheme = url.split("://", 1)[0]
        elif url.startswith("/") or not url.startswith("http"):
            scheme = "relative"
        else:
            scheme = "unknown"

        handler = self._handlers.get(scheme)
        if not handler:
            if "relative" in self._handlers:
                return await self._handlers["relative"].handle(url_or_request)
            raise ValueError(f"No handler registered for scheme: {scheme}")
        return await handler.handle(url_or_request)
