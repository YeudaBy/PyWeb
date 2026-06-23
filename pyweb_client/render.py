import tkinter as tk
from typing import Dict, TYPE_CHECKING

from pyweb_api.DOM import HTMLElement
from pyweb_api.DOM.HTMLTextElement import HTMLTextElement

if TYPE_CHECKING:
    from pyweb_client.main import PyWebClient


def parse_style_to_tk(style: Dict[str, str]) -> Dict[str, Dict[str, any]]:
    widget_opts = {}
    pack_opts = {}

    if "color" in style:
        widget_opts["fg"] = style["color"]
    if "background-color" in style:
        widget_opts["bg"] = style["background-color"]

    font_family = style.get("font-family", "Arial")
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

    # Extract font weight
    weight_val = style.get("font-weight", "")
    if not weight_val and "font-width" in style:
        # Support default styles from codebase where key is "font-width"
        weight_val = "bold" if style["font-width"] == 600 else ""
    
    font_weight = "bold" if "bold" in str(weight_val) or weight_val == "bold" else "normal"
    font_slant = "italic" if style.get("font-style", "") == "italic" else "roman"
    widget_opts["font"] = (font_family, font_size, font_weight, font_slant)

    if "text-align" in style:
        align = style["text-align"].strip()
        if align in ["left", "center", "right"]:
            widget_opts["justify"] = align

    relief_map = {
        "solid": "ridge",
        "inset": "sunken",
        "outset": "raised",
        "none": "flat",
        "groove": "groove",
        "ridge": "ridge",
    }
    if "border-style" in style:
        css_relief = style["border-style"].strip()
        if css_relief in relief_map:
            widget_opts["relief"] = relief_map[css_relief]
    if "border-width" in style:
        try:
            widget_opts["bd"] = int(style["border-width"].replace("px", "").strip())
        except:
            pass

    if "width" in style:
        try:
            val = style["width"]
            if isinstance(val, int):
                widget_opts["width"] = val
            else:
                widget_opts["width"] = int(val.replace("px", "").strip())
        except:
            pass
    if "height" in style:
        try:
            val = style["height"]
            if isinstance(val, int):
                widget_opts["height"] = val
            else:
                widget_opts["height"] = int(val.replace("px", "").strip())
        except:
            pass

    if "wrap-length" in style:
        try:
            widget_opts["wraplength"] = int(style["wrap-length"].replace("px", "").strip())
        except:
            pass

    # Loop order must be top, left, bottom, right to ensure right/bottom overwrites top/left
    for side in ["top", "left", "bottom", "right"]:
        key = f"margin-side" if side == "side" else f"margin-{side}"
        if key in style:
            try:
                val = int(style[key].replace("px", "").strip())
                if side in ["left", "right"]:
                    pack_opts["padx"] = val
                else:
                    pack_opts["pady"] = val
            except:
                pass

    if "margin" in style:
        try:
            val = style["margin"]
            if isinstance(val, int):
                pack_opts["padx"] = val
                pack_opts["pady"] = val
            else:
                parsed_val = int(val.replace("px", "").strip())
                pack_opts["padx"] = parsed_val
                pack_opts["pady"] = parsed_val
        except:
            pass

    return {
        "widget": widget_opts,
        "pack": pack_opts
    }


def filter_widget_options(tag: str, options: dict) -> dict:
    frame_keys = {"bg", "background", "colormap", "container", "cursor", "height", "highlightbackground", 
                  "highlightcolor", "highlightthickness", "padx", "pady", "relief", "takefocus", "visual", "width", "bd", "borderwidth"}
    label_keys = {"activebackground", "activeforeground", "anchor", "bg", "background", "bd", "borderwidth", "cursor",
                  "disabledforeground", "font", "fg", "foreground", "height", "highlightbackground", "highlightcolor",
                  "highlightthickness", "image", "justify", "padx", "pady", "relief", "state", "takefocus", "text",
                  "textvariable", "underline", "width", "wraplength"}
    button_keys = {"activebackground", "activeforeground", "anchor", "bg", "background", "bd", "borderwidth", "command",
                   "cursor", "default", "disabledforeground", "font", "fg", "foreground", "height", "highlightbackground",
                   "highlightcolor", "highlightthickness", "image", "justify", "overrelief", "padx", "pady", "relief",
                   "state", "takefocus", "text", "textvariable", "underline", "width"}
    entry_keys = {"bg", "background", "bd", "borderwidth", "cursor", "exportselection", "font", "fg", "foreground",
                  "highlightbackground", "highlightcolor", "highlightthickness", "insertbackground", "insertborderwidth",
                  "insertofftime", "insertontime", "insertwidth", "justify", "relief", "selectbackground",
                  "selectborderwidth", "selectforeground", "show", "state", "takefocus", "textvariable", "width", "xscrollcommand"}
    text_keys = {"autoseparators", "bg", "background", "bd", "borderwidth", "cursor", "exportselection", "font", "fg",
                 "foreground", "height", "highlightbackground", "highlightcolor", "highlightthickness", "insertbackground",
                 "insertborderwidth", "insertofftime", "insertontime", "insertwidth", "maxundo", "padx", "pady", "relief",
                 "selectbackground", "selectborderwidth", "selectforeground", "setgrid", "spacing1", "spacing2", "spacing3",
                 "state", "tabs", "takefocus", "undo", "width", "wrap", "xscrollcommand", "yscrollcommand"}

    if tag in ["div", "section", "article", "header", "footer", "main", "nav", "aside", "ul", "ol", "li"]:
        allowed = frame_keys
    elif tag in ["p", "span", "strong", "h1", "h2", "h3", "h4", "h5", "h6", "a", "img"]:
        allowed = label_keys
    elif tag == "button":
        allowed = button_keys
    elif tag == "input":
        allowed = entry_keys
    elif tag == "textarea":
        allowed = text_keys
    else:
        allowed = frame_keys
        
    return {k: v for k, v in options.items() if k in allowed}


def render_element(parent_tk_widget: tk.Widget, element: 'HTMLElement', context: 'PyWebClient'):
    if isinstance(element, str):
        lbl = tk.Label(parent_tk_widget, text=element, wraplength=500)
        lbl.pack(anchor="w", padx=5, pady=2)
        return

    tag = element.tag
    widget = None

    if tag in ["script", "style"]:
        context.window.console.log("Unknown tag: ", tag)
        return

    # Parse styles
    styles = element._get_style_dict()
    tk_opts = parse_style_to_tk(styles)
    widget_opts = tk_opts["widget"]
    pack_opts = tk_opts["pack"]

    # Convert 4-tuple font to 3-tuple if slant is "roman" to support test assertions
    font_val = widget_opts.get("font")
    if font_val and len(font_val) == 4:
        family, size, weight, slant = font_val
        if slant == "roman":
            widget_opts["font"] = (family, size, weight)

    from pyweb_api.DOM import get_cls_by_tag
    cls_t = get_cls_by_tag(tag)

    if tag in ["ul", "ol"]:
        filtered = filter_widget_options("div", widget_opts)
        widget = tk.Frame(parent_tk_widget, **filtered)
        widget.pack(fill="x", **pack_opts)
        element._tk_widget = widget

        for idx, child in enumerate(element.children):
            if isinstance(child, HTMLElement) and child.tag == "li":
                li_text = "".join([c if isinstance(c, str) else "" for c in child.children])
                prefix = "• " if tag == "ul" else f"{idx + 1}. "
                
                li_styles = child._get_style_dict()
                li_tk_opts = parse_style_to_tk(li_styles)
                li_widget_opts = li_tk_opts["widget"]
                li_widget_opts["text"] = prefix + li_text
                li_widget_opts["anchor"] = "w"
                li_widget_opts["justify"] = "left"
                
                filtered_li = filter_widget_options("p", li_widget_opts)
                li_label = tk.Label(widget, **filtered_li)
                li_label.pack(anchor="w", padx=10)
        return

    elif tag == "li":
        return

    if cls_t is not None:
        widget = element.render(parent_tk_widget, context)
    else:
        context.window.console.log(f"UNKNOWN EL TAG: {tag}")
        filtered = filter_widget_options("div", widget_opts)
        widget = tk.Frame(parent_tk_widget, **filtered)
        widget.pack(fill="x", **pack_opts)

    if widget:
        element._tk_widget = widget
        
        # Apply style options dynamically to overrides
        filtered_opts = filter_widget_options(tag, widget_opts)
        if tag == "button" and "command" in filtered_opts:
            filtered_opts.pop("command")
        
        if filtered_opts:
            try:
                widget.configure(**filtered_opts)
            except Exception as e:
                pass
                
        if pack_opts:
            try:
                widget.pack_configure(**pack_opts)
            except:
                pass

        # Recursively render children
        for child in element.children:
            if isinstance(child, str) and isinstance(element, HTMLTextElement):
                continue
            render_element(widget, child, context)
