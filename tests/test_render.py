import unittest
import sys
import os

# Add the project root to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import Mock
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt
from pyweb_client.render import parse_style_to_qss, render_element
from pyweb_api.DOM import Element, Div, P, H1, H2, H3, Button, A


class TestStyleParsing(unittest.TestCase):
    def test_parse_color_styles(self):
        """Test parsing color styles"""
        style = {"color": "red", "background-color": "blue"}
        result = parse_style_to_qss(style)
        
        self.assertIn("color: red", result)
        self.assertIn("background-color: blue", result)
    
    def test_parse_font_styles(self):
        """Test parsing font styles"""
        style = {
            "font-family": "Arial",
            "font-size": "16px",
            "font-weight": "bold",
            "font-style": "italic"
        }
        result = parse_style_to_qss(style)
        
        self.assertIn("font-family: 'Arial'", result)
        self.assertIn("font-size: 16pt", result)
        self.assertIn("font-weight: bold", result)
        self.assertIn("font-style: italic", result)
    
    def test_parse_font_defaults(self):
        """Test font parsing with defaults"""
        style = {}
        result = parse_style_to_qss(style)
        
        self.assertIn("font-family: 'Arial'", result)
        self.assertIn("font-size: 12pt", result)
        self.assertIn("font-weight: normal", result)
    
    def test_parse_text_align(self):
        """Test text alignment parsing"""
        for align in ["left", "center", "right"]:
            style = {"text-align": align}
            result = parse_style_to_qss(style)
            self.assertIn(f"qproperty-alignment: 'Align{align.capitalize()}'", result)
    
    def test_parse_border_styles(self):
        """Test border style parsing"""
        style = {"border-style": "solid", "border-width": "2px", "border-color": "black"}
        result = parse_style_to_qss(style)
        
        self.assertIn("border-style: solid", result)
        self.assertIn("border-width: 2px", result)
        self.assertIn("border-color: black", result)
    
    def test_parse_dimensions(self):
        """Test width and height parsing"""
        style = {"width": "100px", "height": "50px"}
        result = parse_style_to_qss(style)
        
        self.assertIn("width: 100px", result)
        self.assertIn("height: 50px", result)
    
    def test_parse_margins(self):
        """Test margin parsing"""
        style = {"margin-left": "10px", "margin-right": "15px"}
        result = parse_style_to_qss(style)
        
        self.assertIn("margin-left: 10px", result)
        self.assertIn("margin-right: 15px", result)
    
    def test_parse_margin_shorthand(self):
        """Test shorthand margin parsing"""
        style = {"margin": "20px"}
        result = parse_style_to_qss(style)
        
        self.assertIn("margin: 20px", result)


class TestRenderElement(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.app = QApplication.instance() or QApplication([])
        self.parent_widget = QWidget()
        
        # Mock PyWebClient
        self.mock_client = Mock()
        self.mock_client.window = Mock()
        self.mock_client.window.console = Mock()
        self.mock_client.window.location = Mock()
        
        # Ensure we clean up after each test
        self.addCleanup(self.cleanup_qt)
    
    def cleanup_qt(self):
        """Clean up Qt resources"""
        try:
            self.parent_widget.deleteLater()
        except:
            pass
    
    def test_render_string_element(self):
        """Test rendering string elements"""
        render_element(self.parent_widget, "Hello World", self.mock_client)
        
        layout = self.parent_widget.layout()
        self.assertEqual(layout.count(), 1)
        lbl = layout.itemAt(0).widget()
        self.assertEqual(lbl.text(), "Hello World")
    
    def test_render_div_element(self):
        """Test rendering div elements"""
        div = Div({"id": "test-div"})
        render_element(self.parent_widget, div, self.mock_client)
        
        layout = self.parent_widget.layout()
        self.assertEqual(layout.count(), 1)
        widget = layout.itemAt(0).widget()
        self.assertIsNotNone(widget)
    
    def test_render_p_element(self):
        """Test rendering paragraph elements"""
        p = P()
        p.append_child("Test paragraph")
        render_element(self.parent_widget, p, self.mock_client)
        
        layout = self.parent_widget.layout()
        self.assertEqual(layout.count(), 1)
        p_widget = layout.itemAt(0).widget()
        self.assertEqual(p_widget.text(), "Test paragraph")
    
    def test_render_header_elements(self):
        """Test rendering header elements with different font sizes"""
        headers = [
            (H1(), "h1", 22),
            (H2(), "h2", 18),
            (H3(), "h3", 16)
        ]
        
        for header, tag, expected_size in headers:
            header.append_child(f"Header {tag}")
            
            temp_parent = QWidget()
            render_element(temp_parent, header, self.mock_client)
            
            layout = temp_parent.layout()
            lbl = layout.itemAt(0).widget()
            self.assertEqual(lbl.text(), f"Header {tag}")
            self.assertIn(f"font-size: {expected_size}pt", lbl.styleSheet())
            temp_parent.deleteLater()
    
    def test_render_button_element(self):
        """Test rendering button elements"""
        button = Button({"value": "Click Me"})
        render_element(self.parent_widget, button, self.mock_client)
        
        layout = self.parent_widget.layout()
        btn = layout.itemAt(0).widget()
        self.assertEqual(btn.text(), "Click Me")
    
    def test_render_link_element(self):
        """Test rendering link elements"""
        link = A({"href": "https://example.com"})
        link.append_child("Click here")
        render_element(self.parent_widget, link, self.mock_client)
        
        layout = self.parent_widget.layout()
        lbl = layout.itemAt(0).widget()
        self.assertEqual(lbl.text(), "Click here")
        self.assertEqual(lbl.cursor().shape(), Qt.CursorShape.PointingHandCursor)
    
    def test_render_unknown_element(self):
        """Test rendering unknown elements"""
        unknown = Element("unknown-tag")
        render_element(self.parent_widget, unknown, self.mock_client)
        
        layout = self.parent_widget.layout()
        widget = layout.itemAt(0).widget()
        self.assertIsNotNone(widget)
    
    def test_render_nested_elements(self):
        """Test rendering nested elements"""
        div = Div()
        p = P()
        p.append_child("Nested content")
        div.append_child(p)
        
        render_element(self.parent_widget, div, self.mock_client)
        
        layout = self.parent_widget.layout()
        div_widget = layout.itemAt(0).widget()
        self.assertIsNotNone(div_widget.layout())
        
        p_widget = div_widget.layout().itemAt(0).widget()
        self.assertEqual(p_widget.text(), "Nested content")
    
    def test_render_script_tags_ignored(self):
        """Test that script tags are ignored"""
        script = Element("script")
        script.append_child("console.log('test');")
        
        render_element(self.parent_widget, script, self.mock_client)
        
        layout = self.parent_widget.layout()
        self.assertTrue(layout is None or layout.count() == 0)
    
    def test_render_ul_element(self):
        """Test rendering unordered list"""
        ul = Element("ul")
        li1 = Element("li")
        li1.append_child("Item 1")
        li2 = Element("li")
        li2.append_child("Item 2")
        ul.append_child(li1)
        ul.append_child(li2)
        
        render_element(self.parent_widget, ul, self.mock_client)
        
        layout = self.parent_widget.layout()
        ul_widget = layout.itemAt(0).widget()
        ul_layout = ul_widget.layout()
        self.assertEqual(ul_layout.count(), 2)
        
        self.assertEqual(ul_layout.itemAt(0).widget().text(), "• Item 1")
        self.assertEqual(ul_layout.itemAt(1).widget().text(), "• Item 2")


if __name__ == '__main__':
    unittest.main()