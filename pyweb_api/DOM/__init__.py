from typing import Type

from pyweb_api.DOM.HTMLBlockElement import HTMLDivElement, HTMLSectionElement, HTMLArticleElement, HTMLHeaderElement, \
    HTMLFooterElement, HTMLMainElement, HTMLNavElement, HTMLAsideElement, HTMLULElement, HTMLOLElement, HTMLLIElement
from pyweb_api.DOM.HTMLElement import HTMLElement
from pyweb_api.DOM.HTMLInteractiveElement import HTMLButtonElement, HTMLFormElement, HTMLTextAreaElement, HTMLInputElement
from pyweb_api.DOM.HTMLMediaElement import HTMLIMGElement
from pyweb_api.DOM.HTMLMetaElement import HTMLScriptElement, HTMLTitleElement
from pyweb_api.DOM.HTMLTextElement import HTMLH1Element, HTMLH2Element, HTMLH3Element, HTMLH4Element, HTMLH5Element, \
    HTMLH6Element, HTMLPElementHTML, HTMLSpanElement, HTMLStrongElement, HTMLAElement
from pyweb_api.DOM.main import HTMLDocumentElement
from pyweb_api.DOM.HTMLEvent import Event

# Expose standard DOM names and aliases
HTMLElement = HTMLElement
HTMLEvent = Event
Event = Event
HTMLDivElement = HTMLDivElement
HTMLPElementHTML = HTMLPElementHTML
HTMLButtonElement = HTMLButtonElement
HTMLAElement = HTMLAElement
HTMLH1Element = HTMLH1Element
HTMLH2Element = HTMLH2Element
HTMLH3Element = HTMLH3Element
HTMLH4Element = HTMLH4Element
HTMLH5Element = HTMLH5Element
HTMLH6Element = HTMLH6Element
HTMLInputElement = HTMLInputElement
HTMLFormElement = HTMLFormElement
HTMLTextAreaElement = HTMLTextAreaElement
HTMLScriptElement = HTMLScriptElement
HTMLTitleElement = HTMLTitleElement
HTMLIMGElement = HTMLIMGElement
HTMLDocumentElement = HTMLDocumentElement
HTMLSectionElement = HTMLSectionElement
HTMLHeaderElement = HTMLHeaderElement
HTMLMainElement = HTMLMainElement

# Aliases used by tests and developer scripts
Element = HTMLElement
Div = HTMLDivElement
P = HTMLPElementHTML
Button = HTMLButtonElement
A = HTMLAElement
H1 = HTMLH1Element
H2 = HTMLH2Element
H3 = HTMLH3Element
H4 = HTMLH4Element
H5 = HTMLH5Element
H6 = HTMLH6Element
Input = HTMLInputElement
Form = HTMLFormElement
TextArea = HTMLTextAreaElement
Script = HTMLScriptElement
Title = HTMLTitleElement
IMG = HTMLIMGElement
Document = HTMLDocumentElement
Section = HTMLSectionElement
Header = HTMLHeaderElement
Main = HTMLMainElement

TAG_MAP = {
    # HTMLBlockElement
    "div": HTMLDivElement,
    "section": HTMLSectionElement,
    "article": HTMLArticleElement,
    "header": HTMLHeaderElement,
    "footer": HTMLFooterElement,
    "main": HTMLMainElement,
    "nav": HTMLNavElement,
    "aside": HTMLAsideElement,
    "ul": HTMLULElement,
    "ol": HTMLOLElement,
    "li": HTMLLIElement,

    # HTMLTextElement
    "h1": HTMLH1Element,
    "h2": HTMLH2Element,
    "h3": HTMLH3Element,
    "h4": HTMLH4Element,
    "h5": HTMLH5Element,
    "h6": HTMLH6Element,
    "p": HTMLPElementHTML,
    "span": HTMLSpanElement,
    "strong": HTMLStrongElement,
    "a": HTMLAElement,

    # HTMLInteractiveElement
    "button": HTMLButtonElement,
    "form": HTMLFormElement,
    "textarea": HTMLTextAreaElement,
    "input": HTMLInputElement,

    # HTMLMediaElement
    "img": HTMLIMGElement,

    # HTMLMetaElement
    "script": HTMLScriptElement,
    "title": HTMLTitleElement,

    # main
    "document": HTMLDocumentElement
}


def get_cls_by_tag(tag: str) -> Type[HTMLElement] | None:
    cls = TAG_MAP.get(tag)
    if cls is not None:
        return cls
    print(f"tag {tag} is unknown")


def get_globals(cls):
    from pyweb_api.Window.main import Window
    w = Window(cls)
    return {
        "Window": w,
        "Document": w.document
    }
