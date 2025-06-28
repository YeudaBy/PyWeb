import unittest
import sys
import os
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyweb_client.render import parse_style_to_tk, filter_widget_options, render_element
from pyweb_api.DOM import Element, Div, P, H1, H2, H3, Button, A


class TestStyleParsing(unittest.TestCase):
    def test_parse_color_styles(self):
        """Test parsing color styles"""
        style = {"color": "red", "background-color": "blue"}
        result = parse_style_to_tk(style)
        
        self.assertEqual(result["widget"]["fg"], "red")
        self.assertEqual(result["widget"]["bg"], "blue")
    
    def test_parse_font_styles(self):
        """Test parsing font styles"""
        style = {
            "font-family": "Arial",
            "font-size": "16px",
            "font-weight": "bold",
            "font-style": "italic"
        }
        result = parse_style_to_tk(style)
        
        expected_font = ("Arial", 16, "bold", "italic")
        self.assertEqual(result["widget"]["font"], expected_font)
    
    def test_parse_font_defaults(self):
        """Test font parsing with defaults"""
        style = {}
        result = parse_style_to_tk(style)
        
        expected_font = ("Arial", 12, "normal", "roman")
        self.assertEqual(result["widget"]["font"], expected_font)
    
    def test_parse_text_align(self):
        """Test text alignment parsing"""
        for align in ["left", "center", "right"]:
            style = {"text-align": align}
            result = parse_style_to_tk(style)
            self.assertEqual(result["widget"]["justify"], align)
    
    def test_parse_border_styles(self):
        """Test border style parsing"""
        style = {"border-style": "solid", "border-width": "2px"}
        result = parse_style_to_tk(style)
        
        self.assertEqual(result["widget"]["relief"], "ridge")
        self.assertEqual(result["widget"]["bd"], 2)
    
    def test_parse_dimensions(self):
        """Test width and height parsing"""
        style = {"width": "100px", "height": "50px"}
        result = parse_style_to_tk(style)
        
        self.assertEqual(result["widget"]["width"], 100)
        self.assertEqual(result["widget"]["height"], 50)
    
    def test_parse_margins(self):
        """Test margin parsing"""
        style = {"margin-left": "10px", "margin-right": "15px"}
        result = parse_style_to_tk(style)
        
        self.assertEqual(result["pack"]["padx"], 15)  # Takes the last value
    
    def test_parse_margin_shorthand(self):
        """Test shorthand margin parsing"""
        style = {"margin": "20px"}
        result = parse_style_to_tk(style)
        
        self.assertEqual(result["pack"]["padx"], 20)
        self.assertEqual(result["pack"]["pady"], 20)


class TestWidgetOptionsFiltering(unittest.TestCase):
    def test_filter_div_options(self):
        """Test filtering options for div (frame)"""
        options = {
            "bg": "red",
            "width": 100,
            "text": "invalid",  # Should be filtered out
            "invalid_option": "test"  # Should be filtered out
        }
        
        result = filter_widget_options("div", options)
        
        self.assertIn("bg", result)
        self.assertIn("width", result)
        self.assertNotIn("text", result)
        self.assertNotIn("invalid_option", result)
    
    def test_filter_p_options(self):
        """Test filtering options for p (label)"""
        options = {
            "text": "Hello",
            "bg": "white",
            "font": ("Arial", 12),
            "command": lambda: None  # Should be filtered out
        }
        
        result = filter_widget_options("p", options)
        
        self.assertIn("text", result)
        self.assertIn("bg", result)
        self.assertIn("font", result)
        self.assertNotIn("command", result)
    
    def test_filter_button_options(self):
        """Test filtering options for button"""
        options = {
            "text": "Click me",
            "bg": "blue",
            "width": 10,
            "wraplength": 100  # Should be filtered out for buttons
        }
        
        result = filter_widget_options("button", options)
        
        self.assertIn("text", result)
        self.assertIn("bg", result)
        self.assertIn("width", result)
        self.assertNotIn("wraplength", result)
    
    def test_filter_unknown_tag(self):
        """Test filtering for unknown tags defaults to frame"""
        options = {
            "bg": "red",
            "text": "should be filtered"
        }
        
        result = filter_widget_options("unknown", options)
        
        self.assertIn("bg", result)
        self.assertNotIn("text", result)


class TestRenderElement(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.parent_widget = tk.Frame(self.root)
        
        # Mock PyWebClient
        self.mock_client = Mock()
        self.mock_client.window = Mock()
        self.mock_client.window.console = Mock()
        self.mock_client.window.location = Mock()
        
        # Ensure we clean up after each test
        self.addCleanup(self.cleanup_tk)
    
    def cleanup_tk(self):
        """Clean up Tkinter resources"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_render_string_element(self):
        """Test rendering string elements"""
        with patch('tkinter.Label') as mock_label:
            # render_element can handle both Element and str types
            render_element(self.parent_widget, "Hello World", self.mock_client)
            
            mock_label.assert_called_once()
            args, kwargs = mock_label.call_args
            self.assertEqual(args[0], self.parent_widget)
            self.assertEqual(kwargs["text"], "Hello World")
    
    def test_render_div_element(self):
        """Test rendering div elements"""
        div = Div({"id": "test-div"})
        
        with patch('tkinter.Frame') as mock_frame:
            render_element(self.parent_widget, div, self.mock_client)
            
            mock_frame.assert_called_once()
            args, kwargs = mock_frame.call_args
            self.assertEqual(args[0], self.parent_widget)
    
    def test_render_p_element(self):
        """Test rendering paragraph elements"""
        p = P()
        p.append_child("Test paragraph")
        
        with patch('tkinter.Label') as mock_label:
            render_element(self.parent_widget, p, self.mock_client)
            
            mock_label.assert_called_once()
            args, kwargs = mock_label.call_args
            self.assertEqual(args[0], self.parent_widget)
            self.assertEqual(kwargs["text"], "Test paragraph")
    
    def test_render_header_elements(self):
        """Test rendering header elements with different font sizes"""
        headers = [
            (H1(), "h1", 22),
            (H2(), "h2", 18),
            (H3(), "h3", 16)
        ]
        
        for header, tag, expected_size in headers:
            header.append_child(f"Header {tag}")
            
            with patch('tkinter.Label') as mock_label:
                render_element(self.parent_widget, header, self.mock_client)
                
                mock_label.assert_called_once()
                args, kwargs = mock_label.call_args
                self.assertEqual(kwargs["text"], f"Header {tag}")
                self.assertEqual(kwargs["font"], ("Arial", expected_size, "bold"))
    
    def test_render_button_element(self):
        """Test rendering button elements"""
        button = Button({"value": "Click Me"})
        
        with patch('tkinter.Button') as mock_button:
            render_element(self.parent_widget, button, self.mock_client)
            
            mock_button.assert_called_once()
            args, kwargs = mock_button.call_args
            self.assertEqual(args[0], self.parent_widget)
            self.assertEqual(kwargs["text"], "Click Me")
            self.assertIn("command", kwargs)
    
    def test_render_link_element(self):
        """Test rendering link elements"""
        link = A({"href": "https://example.com"})
        link.append_child("Click here")
        
        with patch('tkinter.Label') as mock_label:
            render_element(self.parent_widget, link, self.mock_client)
            
            mock_label.assert_called_once()
            args, kwargs = mock_label.call_args
            self.assertEqual(kwargs["text"], "Click here")
            self.assertEqual(kwargs["fg"], "blue")
            self.assertEqual(kwargs["font"], ("Arial", 12, "underline"))
            self.assertEqual(kwargs["cursor"], "hand2")
    
    def test_render_unknown_element(self):
        """Test rendering unknown elements"""
        unknown = Element("unknown-tag")
        
        with patch('tkinter.Frame') as mock_frame:
            render_element(self.parent_widget, unknown, self.mock_client)
            
            # Should log unknown tag
            self.mock_client.window.console.log.assert_called_with("UNKNOWN EL TAG: unknown-tag")
            
            # Should create a frame as fallback
            mock_frame.assert_called_once()
    
    def test_render_nested_elements(self):
        """Test rendering nested elements"""
        div = Div()
        p = P()
        p.append_child("Nested content")
        div.append_child(p)
        
        with patch('tkinter.Frame') as mock_frame, \
             patch('tkinter.Label') as mock_label:
            
            # Mock the pack method to avoid actual Tkinter operations
            mock_frame_instance = Mock()
            mock_frame.return_value = mock_frame_instance
            mock_label_instance = Mock()
            mock_label.return_value = mock_label_instance
            
            render_element(self.parent_widget, div, self.mock_client)
            
            # Should create frame for div
            mock_frame.assert_called_once()
            
            # Should create label for p
            mock_label.assert_called_once()
            args, kwargs = mock_label.call_args
            self.assertEqual(args[0], mock_frame_instance)  # p should be child of div
            self.assertEqual(kwargs["text"], "Nested content")
    
    def test_render_script_tags_ignored(self):
        """Test that script tags are ignored"""
        script = Element("script")
        script.append_child("console.log('test');")
        
        with patch('tkinter.Frame') as mock_frame:
            render_element(self.parent_widget, script, self.mock_client)
            
            # Should log and return early
            self.mock_client.window.console.log.assert_called_with("Unknown tag: ", "script")
            
            # Should not create any widgets
            mock_frame.assert_not_called()
    
    def test_render_ul_element(self):
        """Test rendering unordered list"""
        ul = Element("ul")
        li1 = Element("li")
        li1.append_child("Item 1")
        li2 = Element("li")
        li2.append_child("Item 2")
        ul.append_child(li1)
        ul.append_child(li2)
        
        with patch('tkinter.Frame') as mock_frame, \
             patch('tkinter.Label') as mock_label:
            
            mock_frame_instance = Mock()
            mock_frame.return_value = mock_frame_instance
            
            render_element(self.parent_widget, ul, self.mock_client)
            
            # Should create frame for ul
            mock_frame.assert_called_once()
            
            # Should create labels for li items with bullet points
            self.assertEqual(mock_label.call_count, 2)
            
            # Check first li
            first_call = mock_label.call_args_list[0]
            self.assertEqual(first_call[1]["text"], "• Item 1")
            
            # Check second li
            second_call = mock_label.call_args_list[1]
            self.assertEqual(second_call[1]["text"], "• Item 2")


if __name__ == '__main__':
    # Run tests without actually showing Tkinter windows
    unittest.main() 