import re
from typing import Dict, List, Any

# Inheritable CSS properties according to W3C standards
INHERITABLE_PROPERTIES = {
    "color",
    "font-family",
    "font-size",
    "font-weight",
    "font-style",
    "line-height",
    "text-align",
    "visibility"
}


class CSSRule:
    def __init__(self, selector: str, declarations: Dict[str, str]):
        self.selector = selector.strip()
        self.declarations = declarations
        self.specificity = self._calculate_specificity(self.selector)

    def _calculate_specificity(self, selector: str) -> int:
        if not selector:
            return 0
        ids = selector.count("#")
        classes = selector.count(".")
        
        parts = selector.split()
        tags = 0
        for part in parts:
            if not part.startswith("#") and not part.startswith("."):
                # Simple check for tag name selector
                tags += 1
        return ids * 100 + classes * 10 + tags * 1


def match_single_selector(sel: str, element) -> bool:
    if not sel or not element or isinstance(element, str):
        return False
    if sel.startswith("#"):
        return element.attrs.get("id") == sel[1:]
    elif sel.startswith("."):
        classes = element.attrs.get("class", "").split()
        return sel[1:] in classes
    else:
        return element.tag.lower() == sel.lower()


def match_selector(selector: str, element) -> bool:
    parts = selector.split()
    if not parts or not element or isinstance(element, str):
        return False
        
    # Match the last selector part (right-to-left matching)
    if not match_single_selector(parts[-1], element):
        return False
        
    # Match ancestor parts (if descendant selector, e.g. "div p")
    if len(parts) > 1:
        curr = element.parent
        ancestor_selector = parts[0]
        matched_ancestor = False
        while curr:
            if match_single_selector(ancestor_selector, curr):
                matched_ancestor = True
                break
            curr = curr.parent
        if not matched_ancestor:
            return False
            
    return True


def parse_stylesheet(css_text: str) -> List[CSSRule]:
    rules = []
    # Strip comments
    css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
    
    # Match selector { declarations }
    pattern = re.compile(r'([^{]+)\s*\{\s*([^}]+)\s*\}')
    for match in pattern.finditer(css_text):
        selectors_str, decls_str = match.groups()
        selectors = [s.strip() for s in selectors_str.split(",") if s.strip()]
        
        declarations = {}
        for decl in decls_str.split(";"):
            if ":" in decl:
                k, v = decl.split(":", 1)
                declarations[k.strip().lower()] = v.strip()
                
        for selector in selectors:
            rules.append(CSSRule(selector, declarations))
    return rules


def resolve_styles(element, stylesheets: List[List[CSSRule]], parent_resolved_styles: Dict[str, str] = None):
    if isinstance(element, str):
        return

    # 1. Start with default styles
    resolved = {}
    try:
        resolved.update(element.get_default_styles())
    except:
        pass
        
    # 2. Collect matching CSS rules
    matching_rules = []
    for sheet in stylesheets:
        for rule in sheet:
            if match_selector(rule.selector, element):
                matching_rules.append(rule)
                
    # 3. Sort by specificity
    matching_rules.sort(key=lambda r: r.specificity)
    
    # 4. Apply rules in specificity order
    for rule in matching_rules:
        resolved.update(rule.declarations)
        
    # 5. Apply inline styles (highest priority, specificity = 1000)
    inline_style_attr = element.attrs.get("style", "")
    if inline_style_attr:
        for rule in inline_style_attr.split(";"):
            if ":" in rule:
                k, v = rule.split(":", 1)
                resolved[k.strip().lower()] = v.strip()
                
    # 6. Inherit from parent
    if parent_resolved_styles:
        for prop in INHERITABLE_PROPERTIES:
            if prop not in resolved and prop in parent_resolved_styles:
                resolved[prop] = parent_resolved_styles[prop]
                
    # Set resolved style directly on the element (UI library agnostic)
    element.resolved_style = resolved
    
    # 7. Recursively resolve children styles
    for child in element.children:
        if not isinstance(child, str):
            resolve_styles(child, stylesheets, resolved)
