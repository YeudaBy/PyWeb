import unittest
import sys
import os

# Add the project root to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyweb_client.html_parser import PyHTMLParser
from pyweb_api.DOM import Element, Div, P, H1


class TestPyHTMLParser(unittest.TestCase):
    def setUp(self):
        self.parser = PyHTMLParser()
    
    def test_parser_initialization(self):
        """Test parser initialization"""
        self.assertIsNotNone(self.parser.root)
        self.assertEqual(self.parser.root.tag, "root")
        self.assertEqual(self.parser.current, self.parser.root)
        self.assertEqual(len(self.parser.root.children), 0)
    
    def test_simple_html_parsing(self):
        """Test parsing simple HTML"""
        html = "<p>Hello World</p>"
        self.parser.feed(html)
        
        # Should have one child (the p element)
        self.assertEqual(len(self.parser.root.children), 1)
        p_element = self.parser.root.children[0]
        
        self.assertIsInstance(p_element, P)
        self.assertEqual(p_element.tag, "p")
        self.assertEqual(len(p_element.children), 1)
        self.assertEqual(p_element.children[0], "Hello World")
    
    def test_nested_html_parsing(self):
        """Test parsing nested HTML"""
        html = "<div><p>Paragraph text</p><h1>Header text</h1></div>"
        self.parser.feed(html)
        
        # Should have one child (the div element)
        self.assertEqual(len(self.parser.root.children), 1)
        div_element = self.parser.root.children[0]
        
        self.assertIsInstance(div_element, Div)
        self.assertEqual(len(div_element.children), 2)
        
        # Check paragraph
        p_element = div_element.children[0]
        self.assertIsInstance(p_element, P)
        self.assertEqual(p_element.children[0], "Paragraph text")
        
        # Check header
        h1_element = div_element.children[1]
        self.assertIsInstance(h1_element, H1)
        self.assertEqual(h1_element.children[0], "Header text")
    
    def test_attributes_parsing(self):
        """Test parsing HTML attributes"""
        html = '<div id="container" class="main-div" style="color: red;"><p class="text">Content</p></div>'
        self.parser.feed(html)
        
        div_element = self.parser.root.children[0]
        self.assertEqual(div_element.attrs["id"], "container")
        self.assertEqual(div_element.attrs["class"], "main-div")
        self.assertEqual(div_element.attrs["style"], "color: red;")
        
        p_element = div_element.children[0]
        self.assertEqual(p_element.attrs["class"], "text")
    
    def test_self_closing_tags(self):
        """Test parsing self-closing tags"""
        html = '<div><br/><hr/></div>'
        self.parser.feed(html)
        
        div_element = self.parser.root.children[0]
        self.assertEqual(len(div_element.children), 2)
        
        # Both br and hr should be generic Elements since they're not in TAG_MAP
        br_element = div_element.children[0]
        hr_element = div_element.children[1]
        
        self.assertEqual(br_element.tag, "br")
        self.assertEqual(hr_element.tag, "hr")
    
    def test_complex_document_parsing(self):
        """Test parsing a complex HTML document"""
        html = '''
        <html>
            <head>
                <title>Test Document</title>
            </head>
            <body>
                <header>
                    <h1>Main Title</h1>
                </header>
                <main>
                    <section>
                        <p>First paragraph</p>
                        <p>Second paragraph</p>
                    </section>
                </main>
            </body>
        </html>
        '''
        
        self.parser.feed(html)
        
        # Should have one child (html element)
        self.assertEqual(len(self.parser.root.children), 1)
        html_element = self.parser.root.children[0]
        self.assertEqual(html_element.tag, "html")
        
        # HTML should have head and body
        self.assertEqual(len(html_element.children), 2)
        head_element = html_element.children[0]
        body_element = html_element.children[1]
        
        self.assertEqual(head_element.tag, "head")
        self.assertEqual(body_element.tag, "body")
        
        # Check that title is in head
        title_element = head_element.children[0]
        self.assertEqual(title_element.tag, "title")
        self.assertEqual(title_element.children[0], "Test Document")
    
    def test_whitespace_handling(self):
        """Test that whitespace is properly handled"""
        html = "<p>   Text with spaces   </p>"
        self.parser.feed(html)
        
        p_element = self.parser.root.children[0]
        # Should strip whitespace
        self.assertEqual(p_element.children[0], "Text with spaces")
    
    def test_empty_elements(self):
        """Test parsing empty elements"""
        html = "<div></div><p></p>"
        self.parser.feed(html)
        
        self.assertEqual(len(self.parser.root.children), 2)
        div_element = self.parser.root.children[0]
        p_element = self.parser.root.children[1]
        
        self.assertEqual(len(div_element.children), 0)
        self.assertEqual(len(p_element.children), 0)
    
    def test_unknown_tags(self):
        """Test parsing unknown tags"""
        html = "<unknown-tag>Content</unknown-tag>"
        self.parser.feed(html)
        
        unknown_element = self.parser.root.children[0]
        self.assertEqual(unknown_element.tag, "unknown-tag")
        self.assertIsInstance(unknown_element, Element)
        self.assertEqual(unknown_element.children[0], "Content")
    
    def test_parent_child_relationships(self):
        """Test that parent-child relationships are properly established"""
        html = "<div><p>Child content</p></div>"
        self.parser.feed(html)
        
        div_element = self.parser.root.children[0]
        p_element = div_element.children[0]
        
        # Check parent relationships
        self.assertEqual(p_element.parent, div_element)
        self.assertEqual(div_element.parent, self.parser.root)
        self.assertIsNone(self.parser.root.parent)
    
    def test_multiple_root_elements(self):
        """Test parsing multiple root elements"""
        html = "<div>First</div><p>Second</p><h1>Third</h1>"
        self.parser.feed(html)
        
        self.assertEqual(len(self.parser.root.children), 3)
        
        div_element = self.parser.root.children[0]
        p_element = self.parser.root.children[1]
        h1_element = self.parser.root.children[2]
        
        self.assertEqual(div_element.tag, "div")
        self.assertEqual(p_element.tag, "p")
        self.assertEqual(h1_element.tag, "h1")


if __name__ == '__main__':
    unittest.main() 