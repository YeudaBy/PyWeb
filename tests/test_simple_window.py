import unittest
import sys
import os
from unittest.mock import Mock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyweb_api.Window.Console import Console
from pyweb_api.Window.Document import Document
from pyweb_api.Window.Location import Location
from pyweb_api.Window.main import Window


class TestConsole(unittest.TestCase):
    def test_console_creation(self):
        """Test console creation"""
        mock_writer = Mock()
        console = Console(mock_writer)
        
        self.assertEqual(console.write_to_console, mock_writer)
    
    def test_console_log(self):
        """Test console log method"""
        mock_writer = Mock()
        console = Console(mock_writer)
        
        console.log("test message")
        
        mock_writer.assert_called_with("log", "test message")


class TestDocument(unittest.TestCase):
    def test_document_creation(self):
        """Test document creation"""
        doc = Document()
        
        self.assertEqual(len(doc.children), 1)
        self.assertIsNotNone(doc.children[0])
    
    def test_create_element(self):
        """Test creating elements"""
        doc = Document()
        
        element = doc.create_element("div")
        
        self.assertEqual(element.tag, "div")


class TestLocation(unittest.TestCase):
    def test_location_creation(self):
        """Test location creation"""
        mock_callback = Mock()
        location = Location(mock_callback)
        
        self.assertEqual(location.on_location_change, mock_callback)
        self.assertEqual(len(location.history), 0)
        self.assertEqual(location.current_index, -1)
    
    def test_navigate(self):
        """Test navigation"""
        mock_callback = Mock()
        location = Location(mock_callback)
        
        location.navigate("test-url")
        
        self.assertEqual(len(location.history), 1)
        self.assertEqual(location.history[0], "test-url")
        self.assertEqual(location.current_index, 0)
        mock_callback.assert_called_with("test-url")


class TestWindow(unittest.TestCase):
    def test_window_creation(self):
        """Test window creation"""
        mock_client = Mock()
        mock_client._render_log = Mock()
        mock_client._on_location_change = Mock()
        
        window = Window(mock_client)
        
        self.assertIsInstance(window.console, Console)
        self.assertIsInstance(window.document, Document)
        self.assertIsInstance(window.location, Location)


if __name__ == '__main__':
    unittest.main() 