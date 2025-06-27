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


class Window:
    def __init__(self):
        pass
