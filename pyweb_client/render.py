from typing import Dict, TYPE_CHECKING
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

from pyweb_api.DOM import HTMLElement
from pyweb_api.DOM.HTMLTextElement import HTMLTextElement

if TYPE_CHECKING:
    from pyweb_client.main import PyWebClient


def parse_style_to_qss(style: Dict[str, str]) -> str:
    qss_parts = []
    
    if "color" in style:
        qss_parts.append(f"color: {style['color']}")
    if "background-color" in style:
        qss_parts.append(f"background-color: {style['background-color']}")
    if "text-align" in style:
        align = style["text-align"].strip().lower()
        if align in ["left", "center", "right"]:
            qss_parts.append(f"qproperty-alignment: 'Align{align.capitalize()}'")

    font_family = style.get("font-family", "Arial")
    if font_family == "Ariel":
        font_family = "Arial"
    qss_parts.append(f"font-family: '{font_family}'")

    font_size = 12
    if "font-size" in style:
        try:
            val = style["font-size"]
            if isinstance(val, int):
                font_size = val
            elif isinstance(val, str):
                for unit in ["px", "pt", "em", "rem"]:
                    val = val.replace(unit, "")
                font_size = int(float(val.strip()))
        except:
            pass
    qss_parts.append(f"font-size: {font_size}pt")

    weight_val = style.get("font-weight", "")
    if not weight_val and "font-width" in style:
        weight_val = "bold" if style["font-width"] == 600 else ""
    font_weight = "bold" if "bold" in str(weight_val) or weight_val == "bold" else "normal"
    qss_parts.append(f"font-weight: {font_weight}")

    if style.get("font-style", "") == "italic":
        qss_parts.append("font-style: italic")

    if "border-style" in style:
        qss_parts.append(f"border-style: {style['border-style']}")
    if "border-width" in style:
        qss_parts.append(f"border-width: {style['border-width']}")
    if "border-color" in style:
        qss_parts.append(f"border-color: {style['border-color']}")

    if "width" in style:
        qss_parts.append(f"width: {style['width']}")
    if "height" in style:
        qss_parts.append(f"height: {style['height']}")

    for side in ["top", "left", "bottom", "right"]:
        margin_key = f"margin-{side}"
        if margin_key in style:
            qss_parts.append(f"margin-{side}: {style[margin_key]}")
        padding_key = f"padding-{side}"
        if padding_key in style:
            qss_parts.append(f"padding-{side}: {style[padding_key]}")

    if "margin" in style:
        qss_parts.append(f"margin: {style['margin']}")
    if "padding" in style:
        qss_parts.append(f"padding: {style['padding']}")

    return "; ".join(qss_parts) + ";"


def add_to_parent_layout(parent_widget, child_widget):
    layout = parent_widget.layout()
    if layout is None:
        layout = QVBoxLayout(parent_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
    layout.addWidget(child_widget)


def render_element(parent_qt_widget: QWidget, element: 'HTMLElement', context: 'PyWebClient'):
    if isinstance(element, str):
        lbl = QLabel(element, parent_qt_widget)
        lbl.setWordWrap(True)
        add_to_parent_layout(parent_qt_widget, lbl)
        return

    tag = element.tag
    widget = None

    if tag in ["script", "style"]:
        if context and hasattr(context, "window") and context.window:
            context.window.console.log("Unknown tag: ", tag)
        return

    # Parse styles
    styles = element._get_style_dict()
    qss = parse_style_to_qss(styles)

    from pyweb_api.DOM import get_cls_by_tag
    cls_t = get_cls_by_tag(tag)

    if tag in ["ul", "ol"]:
        widget = QWidget(parent_qt_widget)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        element._qt_widget = widget

        for idx, child in enumerate(element.children):
            if isinstance(child, HTMLElement) and child.tag == "li":
                li_text = "".join([c if isinstance(c, str) else "" for c in child.children])
                prefix = "• " if tag == "ul" else f"{idx + 1}. "
                li_label = QLabel(prefix + li_text, widget)
                li_label.setWordWrap(True)
                li_styles = child._get_style_dict()
                li_qss = parse_style_to_qss(li_styles)
                li_label.setStyleSheet(li_qss)
                layout.addWidget(li_label)
        
        add_to_parent_layout(parent_qt_widget, widget)
        widget.setStyleSheet(qss)
        return

    elif tag == "li":
        return

    if cls_t is not None:
        widget = element.render(parent_qt_widget, context)
    else:
        if context and hasattr(context, "window") and context.window:
            context.window.console.log(f"UNKNOWN EL TAG: {tag}")
        widget = QWidget(parent_qt_widget)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    if widget:
        element._qt_widget = widget
        widget.setStyleSheet(qss)
        add_to_parent_layout(parent_qt_widget, widget)

        # Recursively render children
        for child in element.children:
            if isinstance(child, str) and isinstance(element, HTMLTextElement):
                continue
            render_element(widget, child, context)
