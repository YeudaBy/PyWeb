import unittest
import sys
import os

# Add the project root to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyweb_client.html_parser import PyHTMLParser
from pyweb_api.DOM import Div, P, H1


class TestIntegration(unittest.TestCase):
    def test_html_to_dom_integration(self):
        """Test full HTML parsing to DOM conversion"""
        html = '''
        <html>
            <body>
                <header>
                    <h1>PyWeb Test</h1>
                </header>
                <main>
                    <p>This is a test paragraph.</p>
                    <div class="container">
                        <p>Nested paragraph</p>
                    </div>
                </main>
            </body>
        </html>
        '''
        
        parser = PyHTMLParser()
        parser.feed(html)
        
        # Check structure
        self.assertEqual(len(parser.root.children), 1)
        html_element = parser.root.children[0]
        self.assertEqual(html_element.tag, "html")
        
        # Check that body exists
        body_element = html_element.children[0]
        self.assertEqual(body_element.tag, "body")
        
        # Check header
        header_element = body_element.children[0]
        self.assertEqual(header_element.tag, "header")
        
        # Check h1 in header
        h1_element = header_element.children[0]
        self.assertIsInstance(h1_element, H1)
        self.assertEqual(h1_element.children[0], "PyWeb Test")
    
    def test_pyweb_hub_parsing(self):
        """Test parsing the actual PyWeb hub HTML"""
        # Read and parse the hub HTML
        with open('pyweb_hub/index.html', 'r') as f:
            html_content = f.read()
        
        parser = PyHTMLParser()
        parser.feed(html_content)
        
        # Should successfully parse without errors
        self.assertIsNotNone(parser.root)
        self.assertGreater(len(parser.root.children), 0)
        
        # Check that it contains expected elements
        html_element = parser.root.children[0]
        self.assertEqual(html_element.tag, "html")


if __name__ == '__main__':
    unittest.main() 