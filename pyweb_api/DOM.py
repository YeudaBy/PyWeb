class Input(Element):
    def __init__(self, attrs=None, parent=None):
        super().__init__('button', attrs, parent)


class A(Element):
    def __init__(self, attrs=None, parent=None):
        super().__init__('a', attrs, parent)


class DocumentEL(Element):
    def __init__(self, attrs=None):
        super().__init__("document", attrs)


TAG_MAP = {
    "div": Div,
    "section": Div,
    "header": Div,
    "main": Div,
    "html": Div,
    "body": Div,
    "head": Div,
    "p": P,
    "button": Button,
    "input": Input,
    "a": A,
    "h1": H1,
    "h2": H2,
    "h3": H3,
    "h4": H3,
    "h5": H3,
    "document": DocumentEL
}
