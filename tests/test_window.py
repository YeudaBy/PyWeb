import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyweb_api.Window.main import Window
from pyweb_api.Window.Console import Console
from pyweb_api.Window.Document import Document
from pyweb_api.Window.Location import Location


class TestConsole(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.mock_client._render_log = Mock()
        self.console = Console(self.mock_client)
    
    def test_console_initialization(self):
        """Test console initialization"""
        self.assertEqual(self.console.client, self.mock_client)
    
    def test_console_log(self):
        """Test console.log functionality"""
        self.console.log("Test message")
        self.mock_client._render_log.assert_called_once_with("log", "Test message")
    
    def test_console_error(self):
        """Test console.error functionality"""
        self.console.error("Error message")
        self.mock_client._render_log.assert_called_once_with("error", "Error message")
    
    def test_console_warn(self):
        """Test console.warn functionality"""
        self.console.warn("Warning message")
        self.mock_client._render_log.assert_called_once_with("warn", "Warning message")
    
    def test_console_info(self):
        """Test console.info functionality"""
        self.console.info("Info message")
        self.mock_client._render_log.assert_called_once_with("info", "Info message")
    
    def test_console_multiple_args(self):
        """Test console methods with multiple arguments"""
        self.console.log("Multiple", "arguments", 123)
        self.mock_client._render_log.assert_called_once_with("log", "Multiple arguments 123")
    
    def test_console_objects(self):
        """Test console methods with objects"""
        test_obj = {"key": "value", "number": 42}
        self.console.log("Object:", test_obj)
        self.mock_client._render_log.assert_called_once_with("log", "Object: {'key': 'value', 'number': 42}")


class TestDocument(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.document = Document(self.mock_client)
    
    def test_document_initialization(self):
        """Test document initialization"""
        self.assertEqual(self.document.client, self.mock_client)
        self.assertEqual(len(self.document.elements), 0)
    
    def test_get_element_by_id_existing(self):
        """Test getting existing element by ID"""
        from pyweb_api.DOM import Div
        
        # Create mock element with ID
        element = Div({"id": "test-element"})
        element.id = "test-element"
        self.document.elements = [element]
        
        result = self.document.get_element_by_id("test-element")
        self.assertEqual(result, element)
    
    def test_get_element_by_id_nonexistent(self):
        """Test getting non-existent element by ID"""
        result = self.document.get_element_by_id("nonexistent")
        self.assertIsNone(result)
    
    def test_get_elements_by_tag_name(self):
        """Test getting elements by tag name"""
        from pyweb_api.DOM import Div, P
        
        div1 = Div()
        div2 = Div()
        p1 = P()
        
        self.document.elements = [div1, div2, p1]
        
        divs = self.document.get_elements_by_tag_name("div")
        self.assertEqual(len(divs), 2)
        self.assertIn(div1, divs)
        self.assertIn(div2, divs)
        self.assertNotIn(p1, divs)
    
    def test_get_elements_by_class_name(self):
        """Test getting elements by class name"""
        from pyweb_api.DOM import Div, P
        
        div1 = Div({"class": "container"})
        div2 = Div({"class": "container sidebar"})
        p1 = P({"class": "text"})
        
        self.document.elements = [div1, div2, p1]
        
        containers = self.document.get_elements_by_class_name("container")
        self.assertEqual(len(containers), 2)
        self.assertIn(div1, containers)
        self.assertIn(div2, containers)
        self.assertNotIn(p1, containers)
    
    def test_create_element(self):
        """Test creating new elements"""
        element = self.document.create_element("div")
        
        self.assertEqual(element.tag, "div")
        self.assertIn(element, self.document.elements)
    
    def test_create_element_with_tag_map(self):
        """Test creating elements that exist in TAG_MAP"""
        from pyweb_api.DOM import P
        
        element = self.document.create_element("p")
        
        self.assertIsInstance(element, P)
        self.assertEqual(element.tag, "p")
        self.assertIn(element, self.document.elements)


class TestLocation(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.mock_client._on_location_change = Mock()
        self.location = Location(self.mock_client)
    
    def test_location_initialization(self):
        """Test location initialization"""
        self.assertEqual(self.location.client, self.mock_client)
        self.assertEqual(self.location.current_url, "app://home")
        self.assertEqual(self.location.history, ["app://home"])
        self.assertEqual(self.location.history_index, 0)
    
    def test_navigate_new_url(self):
        """Test navigating to a new URL"""
        new_url = "https://example.com"
        self.location.navigate(new_url)
        
        self.assertEqual(self.location.current_url, new_url)
        self.assertEqual(len(self.location.history), 2)
        self.assertEqual(self.location.history[1], new_url)
        self.assertEqual(self.location.history_index, 1)
        
        self.mock_client._on_location_change.assert_called_once_with(new_url)
    
    def test_navigate_same_url(self):
        """Test navigating to the same URL (should not add to history)"""
        current_url = self.location.current_url
        self.location.navigate(current_url)
        
        # Should still call _on_location_change but not add to history
        self.assertEqual(len(self.location.history), 1)
        self.mock_client._on_location_change.assert_called_once_with(current_url)
    
    def test_back_navigation(self):
        """Test back navigation"""
        # Navigate to a few pages
        self.location.navigate("page1")
        self.location.navigate("page2")
        self.location.navigate("page3")
        
        # Now go back
        self.location.back()
        
        self.assertEqual(self.location.current_url, "page2")
        self.assertEqual(self.location.history_index, 2)
    
    def test_back_navigation_at_beginning(self):
        """Test back navigation when at the beginning of history"""
        # Reset to initial state
        self.location.history_index = 0
        
        self.location.back()
        
        # Should stay at the same position
        self.assertEqual(self.location.history_index, 0)
        self.assertEqual(self.location.current_url, "app://home")
    
    def test_forward_navigation(self):
        """Test forward navigation"""
        # Navigate and then go back
        self.location.navigate("page1")
        self.location.navigate("page2")
        self.location.back()
        
        # Now go forward
        self.location.forward()
        
        self.assertEqual(self.location.current_url, "page2")
        self.assertEqual(self.location.history_index, 2)
    
    def test_forward_navigation_at_end(self):
        """Test forward navigation when at the end of history"""
        self.location.navigate("page1")
        
        # Try to go forward when already at the end
        self.location.forward()
        
        # Should stay at the same position
        self.assertEqual(self.location.current_url, "page1")
        self.assertEqual(self.location.history_index, 1)
    
    def test_reload(self):
        """Test page reload"""
        self.location.navigate("test-page")
        
        # Reset the mock to clear previous calls
        self.mock_client._on_location_change.reset_mock()
        
        self.location.reload()
        
        # Should call _on_location_change with current URL
        self.mock_client._on_location_change.assert_called_once_with("test-page")
        
        # History should remain unchanged
        self.assertEqual(len(self.location.history), 2)
        self.assertEqual(self.location.history_index, 1)
    
    def test_clear_history(self):
        """Test clearing history"""
        # Add some history
        self.location.navigate("page1")
        self.location.navigate("page2")
        self.location.navigate("page3")
        
        self.location.clear_history()
        
        # Should reset to initial state
        self.assertEqual(self.location.history, ["app://home"])
        self.assertEqual(self.location.history_index, 0)
        self.assertEqual(self.location.current_url, "app://home")
    
    def test_navigate_after_back(self):
        """Test navigating to new page after going back (should truncate forward history)"""
        # Build history
        self.location.navigate("page1")
        self.location.navigate("page2")
        self.location.navigate("page3")
        
        # Go back twice
        self.location.back()
        self.location.back()
        
        # Navigate to new page
        self.location.navigate("new-page")
        
        # Forward history should be truncated
        expected_history = ["app://home", "page1", "new-page"]
        self.assertEqual(self.location.history, expected_history)
        self.assertEqual(self.location.history_index, 2)
        self.assertEqual(self.location.current_url, "new-page")


class TestWindow(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.window = Window(self.mock_client)
    
    def test_window_initialization(self):
        """Test window initialization"""
        self.assertEqual(self.window.client, self.mock_client)
        self.assertIsInstance(self.window.console, Console)
        self.assertIsInstance(self.window.document, Document)
        self.assertIsInstance(self.window.location, Location)
    
    def test_alert_method(self):
        """Test window.alert method"""
        with patch('tkinter.messagebox.showinfo') as mock_showinfo:
            self.window.alert("Test alert message")
            mock_showinfo.assert_called_once_with("Alert", "Test alert message")
    
    def test_confirm_method(self):
        """Test window.confirm method"""
        with patch('tkinter.messagebox.askyesno') as mock_askyesno:
            mock_askyesno.return_value = True
            
            result = self.window.confirm("Are you sure?")
            
            self.assertTrue(result)
            mock_askyesno.assert_called_once_with("Confirm", "Are you sure?")
    
    def test_prompt_method(self):
        """Test window.prompt method"""
        with patch('tkinter.simpledialog.askstring') as mock_askstring:
            mock_askstring.return_value = "User input"
            
            result = self.window.prompt("Enter your name:")
            
            self.assertEqual(result, "User input")
            mock_askstring.assert_called_once_with("Prompt", "Enter your name:")
    
    def test_component_integration(self):
        """Test that window components are properly integrated"""
        # Test that console can be accessed through window
        with patch.object(self.window.console, 'log') as mock_log:
            self.window.console.log("Test message")
            mock_log.assert_called_once_with("Test message")
        
        # Test that location can be accessed through window
        with patch.object(self.window.location, 'navigate') as mock_navigate:
            self.window.location.navigate("test-url")
            mock_navigate.assert_called_once_with("test-url")
        
        # Test that document can be accessed through window
        with patch.object(self.window.document, 'create_element') as mock_create:
            self.window.document.create_element("div")
            mock_create.assert_called_once_with("div")


if __name__ == '__main__':
    unittest.main() 