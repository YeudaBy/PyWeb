import unittest
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock

# Add the project root to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyweb_client.network import fetch_text


class TestNetwork(unittest.IsolatedAsyncioTestCase):
    @patch('pyweb_client.network.fetch', new_callable=AsyncMock)
    async def test_fetch_html_success(self, mock_fetch):
        """Test successful HTML fetching"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text.return_value = '<html><body>Test</body></html>'
        mock_fetch.return_value = mock_response
        
        result = await fetch_text('https://example.com')
        
        self.assertEqual(result, '<html><body>Test</body></html>')
        mock_fetch.assert_called_once_with('https://example.com')
    
    @patch('pyweb_client.network.fetch', new_callable=AsyncMock)
    async def test_fetch_html_error(self, mock_fetch):
        """Test HTML fetching with error"""
        mock_fetch.side_effect = Exception("Network error")
        
        with self.assertRaises(Exception):
            await fetch_text('https://invalid-url.com')


if __name__ == '__main__':
    unittest.main() 