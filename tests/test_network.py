import unittest
import sys
import os
from unittest.mock import patch, Mock

# Add the project root to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyweb_client.network import fetch_html


class TestNetwork(unittest.TestCase):
    @patch('requests.get')
    def test_fetch_html_success(self, mock_get):
        """Test successful HTML fetching"""
        mock_response = Mock()
        mock_response.text = '<html><body>Test</body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_html('https://example.com')
        
        self.assertEqual(result, '<html><body>Test</body></html>')
        mock_get.assert_called_once_with('https://example.com')
    
    @patch('requests.get')
    def test_fetch_html_error(self, mock_get):
        """Test HTML fetching with error"""
        mock_get.side_effect = Exception("Network error")
        
        with self.assertRaises(Exception):
            fetch_html('https://invalid-url.com')


if __name__ == '__main__':
    unittest.main() 