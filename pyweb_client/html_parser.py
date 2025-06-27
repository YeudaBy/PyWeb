from html.parser import HTMLParser
from pyweb_api.DOM import Element, TAG_MAP

class PyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = Element("root")
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        element_cls = TAG_MAP.get(tag)
        if not element_cls:
            el = Element(tag, dict(attrs), parent=self.current)
        else:
            el = element_cls(dict(attrs), parent=self.current)
        self.current.append_child(el)
        self.current = el

    def handle_endtag(self, tag):
        if self.current.parent:
            self.current = self.current.parent

    def handle_data(self, data):
        if data.strip():
            self.current.append_child(data.strip())
