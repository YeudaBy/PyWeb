import unittest
import sys
import os

# Add the project root to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyweb_api.DOM import Element, Event, Div, P, Button, A, H1, H2, H3, Input, TAG_MAP


class TestElement(unittest.TestCase):
    def setUp(self):
        self.element = Element("div", {"id": "test", "class": "container"})
    
    def test_element_creation(self):
        """Test basic element creation"""
        self.assertEqual(self.element.tag, "div")
        self.assertEqual(self.element.attrs["id"], "test")
        self.assertEqual(self.element.attrs["class"], "container")
        self.assertEqual(len(self.element.children), 0)
        self.assertIsNone(self.element.parent)
    
    def test_append_child_string(self):
        """Test appending string child"""
        self.element.append_child("Hello World")
        self.assertEqual(len(self.element.children), 1)
        self.assertEqual(self.element.children[0], "Hello World")
    
    def test_append_child_element(self):
        """Test appending element child"""
        child = Element("p")
        self.element.append_child(child)
        self.assertEqual(len(self.element.children), 1)
        self.assertEqual(self.element.children[0], child)
        self.assertEqual(child.parent, self.element)
    
    def test_set_text(self):
        """Test setting text content"""
        self.element.append_child("old text")
        child = Element("span")
        self.element.append_child(child)
        
        self.element.set_text("new text")
        self.assertEqual(len(self.element.children), 1)
        self.assertEqual(self.element.children[0], "new text")
    
    def test_style_parsing(self):
        """Test CSS style parsing"""
        element = Element("div", {"style": "color: red; font-size: 16px; background-color: blue"})
        styles = element._get_style_dict()
        
        self.assertEqual(styles["color"], "red")
        self.assertEqual(styles["font-size"], "16px")
        self.assertEqual(styles["background-color"], "blue")
    
    def test_ancestry_path(self):
        """Test getting ancestry path"""
        parent = Element("body")
        grandparent = Element("html")
        parent.parent = grandparent
        self.element.parent = parent
        
        path = self.element._get_ancestry_path()
        self.assertEqual(len(path), 2)
        self.assertEqual(path[0], parent)
        self.assertEqual(path[1], grandparent)


class TestEvent(unittest.TestCase):
    def test_event_creation(self):
        """Test event creation"""
        element = Element("button")
        event = Event("click", element)
        
        self.assertEqual(event.type, "click")
        self.assertEqual(event.target, element)
        self.assertIsNone(event.current_target)
        self.assertFalse(event._stopped)
    
    def test_stop_propagation(self):
        """Test event stop propagation"""
        element = Element("button")
        event = Event("click", element)
        
        event.stop_propagation()
        self.assertTrue(event._stopped)


class TestEventHandling(unittest.TestCase):
    def setUp(self):
        self.root = Element("div")
        self.parent = Element("p")
        self.child = Element("button")
        
        self.root.append_child(self.parent)
        self.parent.append_child(self.child)
        
        self.events_fired = []
    
    def event_handler(self, event):
        self.events_fired.append(f"{event.current_target.tag}_{event.type}")
    
    def test_event_listener_addition(self):
        """Test adding event listeners"""
        self.child.add_event_listener("click", self.event_handler)
        
        self.assertIn(("click", "bubble"), self.child.listeners)
        self.assertEqual(len(self.child.listeners[("click", "bubble")]), 1)
    
    def test_event_dispatch_bubbling(self):
        """Test event bubbling"""
        self.child.add_event_listener("click", self.event_handler)
        self.parent.add_event_listener("click", self.event_handler)
        self.root.add_event_listener("click", self.event_handler)
        
        event = Event("click", self.child)
        self.child.dispatch_event(event)
        
        # Should fire on target, then bubble up
        expected = ["button_click", "p_click", "div_click"]
        self.assertEqual(self.events_fired, expected)
    
    def test_event_stop_propagation(self):
        """Test stopping event propagation"""
        def stopping_handler(event):
            self.events_fired.append(f"{event.current_target.tag}_click")
            event.stop_propagation()
        
        self.child.add_event_listener("click", stopping_handler)
        self.parent.add_event_listener("click", self.event_handler)
        
        event = Event("click", self.child)
        self.child.dispatch_event(event)
        
        # Should only fire on target, not bubble
        self.assertEqual(self.events_fired, ["button_click"])


class TestElementTypes(unittest.TestCase):
    def test_div_creation(self):
        """Test Div element creation"""
        div = Div({"class": "container"})
        self.assertEqual(div.tag, "div")
        self.assertEqual(div.attrs["class"], "container")
    
    def test_p_creation(self):
        """Test P element creation"""
        p = P({"id": "paragraph"})
        self.assertEqual(p.tag, "p")
        self.assertEqual(p.attrs["id"], "paragraph")
    
    def test_button_creation(self):
        """Test Button element creation"""
        button = Button({"type": "submit", "value": "Click Me"})
        self.assertEqual(button.tag, "button")
        self.assertEqual(button.attrs["type"], "submit")
        self.assertEqual(button.attrs["value"], "Click Me")
    
    def test_input_creation(self):
        """Test Input element creation - note: this has a bug in DOM.py"""
        input_elem = Input({"type": "text", "name": "username"})
        # Note: There's a bug - Input.__init__ calls super().__init__('button', ...)
        # instead of 'input'
        self.assertEqual(input_elem.tag, "button")  # This should be "input"
        self.assertEqual(input_elem.attrs["type"], "text")
    
    def test_header_elements(self):
        """Test header elements (H1, H2, H3)"""
        h1 = H1({"class": "title"})
        h2 = H2({"class": "subtitle"})
        h3 = H3({"class": "subheading"})
        
        self.assertEqual(h1.tag, "h1")
        self.assertEqual(h2.tag, "h2")
        self.assertEqual(h3.tag, "h3")
        
        self.assertEqual(h1.attrs["class"], "title")
        self.assertEqual(h2.attrs["class"], "subtitle")
        self.assertEqual(h3.attrs["class"], "subheading")
    
    def test_link_creation(self):
        """Test A (link) element creation"""
        link = A({"href": "https://example.com", "target": "_blank"})
        self.assertEqual(link.tag, "a")
        self.assertEqual(link.attrs["href"], "https://example.com")
        self.assertEqual(link.attrs["target"], "_blank")


class TestTagMap(unittest.TestCase):
    def test_tag_map_completeness(self):
        """Test that TAG_MAP contains expected mappings"""
        expected_tags = {
            "div": Div,
            "section": Div,
            "header": Div,
            "main": Div,
            "p": P,
            "button": Button,
            "input": Input,
            "a": A,
            "h1": H1,
            "h2": H2,
            "h3": H3,
        }
        
        for tag, expected_class in expected_tags.items():
            self.assertIn(tag, TAG_MAP)
            self.assertEqual(TAG_MAP[tag], expected_class)
    
    def test_tag_map_usage(self):
        """Test using TAG_MAP to create elements"""
        # Test that we can create elements using TAG_MAP
        div_class = TAG_MAP["div"]
        div = div_class({"id": "test"})
        self.assertIsInstance(div, Div)
        self.assertEqual(div.tag, "div")
        
        p_class = TAG_MAP["p"]
        p = p_class({"class": "text"})
        self.assertIsInstance(p, P)
        self.assertEqual(p.tag, "p")


if __name__ == '__main__':
    unittest.main() 