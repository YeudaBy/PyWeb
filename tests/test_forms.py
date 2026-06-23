import unittest
import sys
import os
from unittest.mock import Mock

# Add the project root to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QTextEdit, QPushButton
from PyQt6.QtCore import Qt

from pyweb_client.render import render_element
from pyweb_api.DOM import HTMLFormElement, HTMLInputElement, HTMLTextAreaElement, HTMLButtonElement, HTMLEvent
from pyweb_api.network import Request


class TestForms(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with QApplication"""
        self.app = QApplication.instance() or QApplication([])
        self.parent_widget = QWidget()
        
        # Mock client and window
        self.mock_client = Mock()
        self.mock_window = Mock()
        self.mock_client.window = self.mock_window
        self.mock_window.location = Mock()
        self.mock_window.console = Mock()
        
        self.addCleanup(self.cleanup_qt)

    def cleanup_qt(self):
        """Clean up Qt resources"""
        try:
            self.parent_widget.deleteLater()
        except:
            pass

    def test_form_finding_controls(self):
        """Test that form correctly discovers inputs, textareas, and buttons in its subtree"""
        form = HTMLFormElement()
        
        # Text input
        input_text = HTMLInputElement(attrs={"name": "username", "value": "alice"})
        form.append_child(input_text)
        
        # Textarea
        textarea = HTMLTextAreaElement(attrs={"name": "bio"})
        textarea.append_child("hello bio")
        form.append_child(textarea)
        
        # Button inside a div container
        from pyweb_api.DOM import HTMLDivElement
        div = HTMLDivElement()
        btn = HTMLButtonElement(attrs={"name": "action", "value": "save"})
        div.append_child(btn)
        form.append_child(div)
        
        # Test finding controls
        from pyweb_api.DOM.HTMLInteractiveElement import find_form_controls
        controls = find_form_controls(form)
        self.assertEqual(len(controls), 3)
        self.assertIn(input_text, controls)
        self.assertIn(textarea, controls)
        self.assertIn(btn, controls)

    def test_input_value_qt_binding(self):
        """Test that HTMLInputElement.value binds dynamically to QLineEdit text"""
        input_el = HTMLInputElement(attrs={"name": "test_input", "value": "initial"})
        
        # Before rendering
        self.assertEqual(input_el.value, "initial")
        
        # Render and edit Qt widget
        render_element(self.parent_widget, input_el, self.mock_client)
        widget = input_el._qt_widget
        self.assertIsInstance(widget, QLineEdit)
        self.assertEqual(widget.text(), "initial")
        
        widget.setText("changed")
        self.assertEqual(input_el.value, "changed")
        
        # Set value programmatically
        input_el.value = "new_val"
        self.assertEqual(widget.text(), "new_val")

    def test_textarea_value_qt_binding(self):
        """Test that HTMLTextAreaElement.value binds dynamically to QTextEdit plain text"""
        textarea = HTMLTextAreaElement(attrs={"name": "test_text"})
        textarea.append_child("initial text")
        
        # Before rendering
        self.assertEqual(textarea.value, "initial text")
        
        # Render and edit Qt widget
        render_element(self.parent_widget, textarea, self.mock_client)
        widget = textarea._qt_widget
        self.assertIsInstance(widget, QTextEdit)
        self.assertEqual(widget.toPlainText(), "initial text")
        
        widget.setPlainText("new text")
        self.assertEqual(textarea.value, "new text")
        
        # Set value programmatically
        textarea.value = "programmatic text"
        self.assertEqual(widget.toPlainText(), "programmatic text")

    def test_form_submission_get(self):
        """Test GET form submission query string formatting and navigation"""
        form = HTMLFormElement(attrs={"action": "http://example.com/search", "method": "GET"})
        input_q = HTMLInputElement(attrs={"name": "q", "value": "python"})
        input_lang = HTMLInputElement(attrs={"name": "lang", "value": "he"})
        form.append_child(input_q)
        form.append_child(input_lang)
        
        # Submit form
        form.submit(self.mock_client)
        
        # Verify get navigation URL
        self.mock_window.location.navigate.assert_called_once()
        nav_arg = self.mock_window.location.navigate.call_args[0][0]
        self.assertIsInstance(nav_arg, str)
        self.assertTrue(nav_arg.startswith("http://example.com/search?"))
        self.assertIn("q=python", nav_arg)
        self.assertIn("lang=he", nav_arg)

    def test_form_submission_post(self):
        """Test POST form submission request routing and body payload"""
        form = HTMLFormElement(attrs={"action": "http://example.com/submit", "method": "POST"})
        input_user = HTMLInputElement(attrs={"name": "user", "value": "john_doe"})
        form.append_child(input_user)
        
        # Submit form
        form.submit(self.mock_client)
        
        # Verify POST request creation
        self.mock_window.location.navigate.assert_called_once()
        req = self.mock_window.location.navigate.call_args[0][0]
        self.assertIsInstance(req, Request)
        self.assertEqual(req.url, "http://example.com/submit")
        self.assertEqual(req.method, "POST")
        self.assertEqual(req.headers.get("Content-Type"), "application/x-www-form-urlencoded")
        self.assertEqual(req.body, "user=john_doe")

    def test_submit_button_triggers_submit(self):
        """Test that HTMLButtonElement (type=submit) triggers form submission on click"""
        form = HTMLFormElement(attrs={"action": "http://test.com/action"})
        input_field = HTMLInputElement(attrs={"name": "field", "value": "data"})
        btn = HTMLButtonElement(attrs={"type": "submit"})
        
        form.append_child(input_field)
        form.append_child(btn)
        
        # Render them
        render_element(self.parent_widget, form, self.mock_client)
        
        # Verify the button clicked signal triggers navigation
        self.mock_window.location.navigate.assert_not_called()
        
        # Trigger PyQt6 button click
        btn_widget = btn._qt_widget
        self.assertIsInstance(btn_widget, QPushButton)
        btn_widget.click()
        
        self.mock_window.location.navigate.assert_called_once_with("http://test.com/action?field=data")

    def test_input_type_submit_triggers_submit(self):
        """Test that HTMLInputElement (type=submit) renders as QPushButton and triggers form submission"""
        form = HTMLFormElement(attrs={"action": "http://test.com/input-action"})
        input_submit = HTMLInputElement(attrs={"type": "submit", "value": "Go!"})
        form.append_child(input_submit)
        
        # Render
        render_element(self.parent_widget, form, self.mock_client)
        
        submit_widget = input_submit._qt_widget
        self.assertIsInstance(submit_widget, QPushButton)
        self.assertEqual(submit_widget.text(), "Go!")
        
        # Trigger click
        submit_widget.click()
        
        self.mock_window.location.navigate.assert_called_once_with("http://test.com/input-action")

    def test_submit_event_prevent_default(self):
        """Test that calling preventDefault() on submit event cancels form submission"""
        form = HTMLFormElement(attrs={"action": "http://test.com/should-not-go"})
        
        def on_submit(event):
            event.preventDefault()
            
        form.add_event_listener("submit", on_submit)
        
        # Trigger submit
        form.submit(self.mock_client)
        
        # Verify navigation was NOT called
        self.mock_window.location.navigate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
