import tkinter as tk
from typing import Dict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyweb_client.main import PyWebClient
    from pyweb_api.DOM import HTMLElement


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
            font_size = int(style["font-size"].replace("px", "").strip())
        except:
            pass
    font_weight = "bold" if style.get("font-weight", "") == "bold" else "normal"
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
            widget_opts["width"] = int(style["width"].replace("px", "").strip())
        except:
            pass
    if "height" in style:
        try:
            widget_opts["height"] = int(style["height"].replace("px", "").strip())
        except:
            pass

    if "wrap-length" in style:
        try:
            widget_opts["wraplength"] = int(style["wrap-length"].replace("px", "").strip())
        except:
            pass

    for side in ["top", "right", "bottom", "left"]:
        key = f"margin-{side}"
        if key in style:
            val = int(style[key].replace("px", "").strip())
            if side in ["left", "right"]:
                pack_opts["padx"] = val
            else:
                pack_opts["pady"] = val

    # shorthand: margin
    if "margin" in style:
        try:
            val = int(style["margin"].replace("px", "").strip())
            pack_opts["padx"] = val
            pack_opts["pady"] = val
        except:
            pass

    return {
        "widget": widget_opts,
        "pack": pack_opts
    }


def render_element(parent_tk_widget: tk.Widget, element: 'HTMLElement', context: 'PyWebClient'):
    if isinstance(element, str):
        lbl = tk.Label(parent_tk_widget, text=element, wraplength=500)
        lbl.pack(anchor="w", padx=5, pady=2)
        return

    tag = element.tag
    widget = None

    from pyweb_api.DOM import get_cls_by_tag
    cls_t = get_cls_by_tag(tag)
    if cls_t is not None:
        cls = cls_t()
        print(cls_t, cls)
        widget = cls.render(parent_tk_widget, context)

    if widget:
        element._tk_widget = widget
        widget.pack(fill="x")

    for child in element.children:
        render_element(widget, child, context)

#  elif tag in ["ul", "ol"]:
#         widget = tk.Frame(parent_tk_widget, **widget_opts)
#         for idx, child in enumerate(element.children):
#             if isinstance(child, Element) and child.tag == "li":
#                 li_text = "".join([c if isinstance(c, str) else "" for c in child.children])
#                 prefix = "• " if tag == "ul" else f"{idx + 1}. "
#                 li_label = tk.Label(widget, text=prefix + li_text, anchor="w", justify="left")
#                 li_label.pack(anchor="w", padx=10)
#     elif tag == "li":
#         return  # already handled in ul/ol
#     elif tag == "br":
#         widget = tk.Label(parent_tk_widget, text="")
#     elif tag == "hr":
#         widget = tk.Frame(parent_tk_widget, height=2, bg="gray")
#     elif tag == "img":
#         src = element.attrs.get("src", "")
#         try:
#             if src.startswith("http"):
#                 with request.urlopen(src) as u:
#                     raw_data = u.read()
#                 im = Image.open(io.BytesIO(raw_data))
#             else:
#                 im = Image.open(src)
#             im = im.resize((150, 100))
#             photo = ImageTk.PhotoImage(im)
#             widget = tk.Label(parent_tk_widget, image=photo)
#             widget.image = photo
#         except Exception:
#             widget = tk.Label(parent_tk_widget, text="[Image Load Error]")
