from html.parser import HTMLParser

from typing import TYPE_CHECKING



class PyHTMLParser(HTMLParser):
    def __init__(self):
        from pyweb_api.DOM import HTMLElement
        super().__init__()
        self.root = HTMLElement("root")
        self.current = self.root
        self.stylesheets = []

    def handle_starttag(self, tag, attrs):
        from pyweb_api.DOM import HTMLElement
        from pyweb_api.DOM import get_cls_by_tag
        element_cls = get_cls_by_tag(tag)
        if not element_cls:
            el = HTMLElement(tag, dict(attrs), parent=self.current)
        else:
            el = element_cls(dict(attrs), self.current)
        self.current.append_child(el)
        
        void_elements = {
            "area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"
        }
        if tag.lower() not in void_elements:
            self.current = el

    def handle_endtag(self, tag):
        void_elements = {
            "area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"
        }
        if tag.lower() in void_elements:
            return
            
        if self.current.parent:
            self.current = self.current.parent

    def handle_data(self, data):
        if self.current.tag == "style":
            from pyweb_api.css_engine import parse_stylesheet
            self.stylesheets.append(parse_stylesheet(data))
            
        if data.strip():
            self.current.append_child(data.strip())
