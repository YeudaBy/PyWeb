from typing import List, TYPE_CHECKING
from pyweb_api.DOM import HTMLDocumentElement

if TYPE_CHECKING:
    from pyweb_api.DOM import HTMLElement


class Document:

    def __init__(self):
        self.children: List['HTMLElement' | None] = []
        doc_el = HTMLDocumentElement()
        self.children.append(doc_el)

    def get_element_by_id(self, _id: str) :
        def recurse_search(element: 'HTMLElement'):
            if hasattr(element, "id") and element.id == _id:
                return element
            for child in element.children:
                if isinstance(child, 'HTMLElement'):
                    result = recurse_search(child)
                    if result:
                        return result
            return None

        root = self.children[0] if self.children else None
        if root:
            return recurse_search(root)
        return None

    def create_element(self, tag_name: str) -> 'HTMLElement':
        from pyweb_api.DOM import HTMLElement, get_cls_by_tag
        cls = get_cls_by_tag(tag_name)
        if cls:
            el = cls()
        else:
            el = HTMLElement(tag_name)
        self.children[0].append_child(el)
        return el

