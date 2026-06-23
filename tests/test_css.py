import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyweb_api.DOM.HTMLElement import HTMLElement
from pyweb_api.css_engine import (
    CSSRule,
    parse_stylesheet,
    match_selector,
    resolve_styles
)


class TestCSSEngine(unittest.TestCase):
    def test_stylesheet_parsing(self):
        css = """
        h1 { color: red; font-size: 24px; }
        .btn, #submit { background-color: blue; }
        div p { margin: 10px; }
        """
        rules = parse_stylesheet(css)
        self.assertEqual(len(rules), 4)
        
        self.assertEqual(rules[0].selector, "h1")
        self.assertEqual(rules[0].declarations["color"], "red")
        self.assertEqual(rules[0].declarations["font-size"], "24px")
        
        self.assertEqual(rules[1].selector, ".btn")
        self.assertEqual(rules[2].selector, "#submit")
        self.assertEqual(rules[3].selector, "div p")

    def test_selector_matching(self):
        parent = HTMLElement("div", {"class": "container"})
        child = HTMLElement("p", {"id": "lead", "class": "btn active"}, parent=parent)
        parent.children.append(child)
        
        # Tag match
        self.assertTrue(match_selector("p", child))
        self.assertTrue(match_selector("div", parent))
        
        # ID match
        self.assertTrue(match_selector("#lead", child))
        self.assertFalse(match_selector("#other", child))
        
        # Class match
        self.assertTrue(match_selector(".btn", child))
        self.assertTrue(match_selector(".active", child))
        self.assertTrue(match_selector(".container", parent))
        
        # Descendant match
        self.assertTrue(match_selector("div p", child))
        self.assertFalse(match_selector("span p", child))

    def test_specificity_and_cascading(self):
        element = HTMLElement("h1", {"id": "title", "class": "header", "style": "color: purple;"})
        
        css = """
        h1 { color: red; font-size: 20px; }
        .header { color: blue; font-size: 22px; }
        #title { color: green; font-size: 24px; }
        """
        sheets = [parse_stylesheet(css)]
        
        # Resolve styles
        resolve_styles(element, sheets)
        
        # Inline style (purple) should override everything
        self.assertEqual(element.resolved_style["color"], "purple")
        
        # ID style (24px) should override Class (22px) and Tag (20px)
        self.assertEqual(element.resolved_style["font-size"], "24px")

    def test_style_inheritance(self):
        parent = HTMLElement("div", {"style": "color: blue; font-family: Arial; margin: 20px;"})
        child = HTMLElement("p", {}, parent=parent)
        parent.children.append(child)
        
        resolve_styles(parent, [])
        
        # Parent should have its styles resolved
        self.assertEqual(parent.resolved_style["color"], "blue")
        self.assertEqual(parent.resolved_style["font-family"], "Arial")
        self.assertEqual(parent.resolved_style["margin"], "20px")
        
        # Child should inherit inheritable properties (color, font-family) but not margin
        self.assertEqual(child.resolved_style["color"], "blue")
        self.assertEqual(child.resolved_style["font-family"], "Arial")
        self.assertNotIn("margin", child.resolved_style)


if __name__ == '__main__':
    unittest.main()
