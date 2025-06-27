from typing import List

from pyweb_api.DOM import Element, DocumentEL


class Document:

    def __init__(self):
        self.children = List[Element | None] = []
        doc_el = DocumentEL()
        self.children.append(doc_el)

    def get_element_by_id(self, _id: str) -> Element | None:
        def recurse_search(element: Element) -> Element | None:
            if hasattr(element, "id") and element.id == _id:
                return element
            for child in element.children:
                if isinstance(child, Element):
                    result = recurse_search(child)
                    if result:
                        return result
            return None

        root = self.children[0] if self.children else None
        if root:
            return recurse_search(root)
        return None

    def create_element(self, tag_name: str) -> Element:
        el = Element(tag_name)
        self.children[0].children.append(el)
        return el


class Location:
    def __init__(self, on_location_change):
        self.history = []
        self.current_index = -1
        self._current_url = None
        self.on_location_change = on_location_change

    def navigate(self, url: str):
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]

        self.history.append(url)
        self.current_index += 1
        self._current_url = url
        self.on_location_change(url)

    def back(self):
        if self.current_index > 0:
            self.current_index -= 1
            self._current_url = self.history[self.current_index]
            self.on_location_change(self._current_url)
            return self._current_url
        self.on_location_change(None)
        return None

    def forward(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self._current_url = self.history[self.current_index]
            self.on_location_change(self._current_url)
            return self._current_url
        self.on_location_change(None)
        return None

    @property
    def href(self):
        return self._current_url


class Console:
    def __init__(self, write_to_console):
        self.write_to_console = write_to_console

    def log(self, *args):
        print(self._args_to_str(args))
        self.write_to_console("log", self._args_to_str(args))

    def error(self, *args):
        print("---ERROR:", self._args_to_str(args))
        self.write_to_console("error", self._args_to_str(args))

    def warn(self, *args):
        print("---WARN:", self._args_to_str(args))
        self.write_to_console("warn", self._args_to_str(args))

    def _args_to_str(*args):
        return " ".join([str(a) for a in args])


class Window:
    def __init__(self):
        pass
