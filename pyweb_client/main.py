import sys
import os
import threading
from typing import Optional

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QTextEdit, 
                             QFileDialog, QLabel, QMenu)
from PyQt6.QtCore import QObject, pyqtSignal, Qt, QEvent
from PyQt6.QtGui import QAction, QIcon

from pyweb_api.Window.main import Window
from pyweb_client.layout.RenderArea import RenderArea
from pyweb_client.render import render_element
from pyweb_client.router import ProtocolRouter, AppSchemeHandler, FileSchemeHandler, HttpSchemeHandler, RelativeSchemeHandler


class RenderSignaler(QObject):
    content_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str, object)


class ClickEventFilter(QObject):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            self.client.window.console.log(f"{obj} clicked")
        return super().eventFilter(obj, event)


class PyWebClient:
    def __init__(self, root: QMainWindow):
        self.root: QMainWindow = root

        # Set application logo/window icon
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "assests", "logo.png")
            if os.path.exists(logo_path):
                self.root.setWindowIcon(QIcon(logo_path))
        except Exception as e:
            print("Failed to load app logo:", e)

        self.render_area: RenderArea = RenderArea(self.root, self)
        self.address_input: Optional[QLineEdit] = None
        self.console_container: Optional[QWidget] = None
        self.console_output: Optional[QTextEdit] = None

        self.window: Window = Window(self)

        # Maximize window and focus
        self.root.showMaximized()

        # Initialize protocol scheme router
        self.router: ProtocolRouter = ProtocolRouter()
        self.router.register_handler("app", AppSchemeHandler(self))
        self.router.register_handler("file", FileSchemeHandler())
        self.router.register_handler("http", HttpSchemeHandler())
        self.router.register_handler("https", HttpSchemeHandler())
        self.router.register_handler("relative", RelativeSchemeHandler(self))

        # Thread signaler for safe GUI updates from background loop
        self.signaler = RenderSignaler()
        self.signaler.content_signal.connect(self._render_content)
        self.signaler.error_signal.connect(self._render_error)

        self.render_layout()
        self.build_menu()

        # Initialize background asyncio event loop
        import asyncio
        self.loop = asyncio.new_event_loop()
        def start_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        threading.Thread(target=start_loop, args=(self.loop,), daemon=True).start()

        # Start interactive REPL console asynchronously in background
        from pyweb_client.script_engine import PyWebInterpreter
        self.interpreter: PyWebInterpreter = PyWebInterpreter(self)
        threading.Thread(target=self.interpreter.open_console, daemon=True).start()

        # Install global click listener filter
        self.filter = ClickEventFilter(self)
        QApplication.instance().installEventFilter(self.filter)

    def render(self) -> None:
        pass  # PyQt6 loop is started via app.exec() in run()

    def on_open_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self.root, "Open HTML File", "", "HTML Files (*.html)")
        if file_path:
            self.window.location.navigate(f"file://{file_path}")

    def _render_log(self, level: str, message: str) -> None:
        if self.console_output:
            self.console_output.append(f"<{level}>: {message}")

    def _on_location_change(self, url: str) -> None:
        self.window.console.log(f"Navigating to: {url}")
        
        # Add to history menu dynamically
        hist_action = QAction(url, self.root)
        hist_action.triggered.connect(lambda: self.window.location.navigate(url))
        self.history_menu.addAction(hist_action)

        self.render_area.clear()
        
        if self.address_input:
            self.address_input.setText(url)

        # Asynchronously resolve url via scheme handlers
        import asyncio
        async def load_task():
            try:
                response = await self.router.resolve(url)
                self.signaler.content_signal.emit(response)
            except Exception as e:
                self.signaler.error_signal.emit(url, e)

        asyncio.run_coroutine_threadsafe(load_task(), self.loop)

    def _render_content(self, response) -> None:
        from pyweb_api.DOM import HTMLElement
        from pyweb_client.html_parser import PyHTMLParser
        
        try:
            if isinstance(response.content, HTMLElement):
                from pyweb_api.css_engine import resolve_styles
                resolve_styles(response.content, [])
                render_element(self.render_area.widget, response.content, self)
            else:
                parser = PyHTMLParser()
                parser.feed(response.content)
                from pyweb_api.css_engine import resolve_styles
                resolve_styles(parser.root, parser.stylesheets)
                render_element(self.render_area.widget, parser.root, self)
            self.window.console.log("Page rendered successfully.")
        except Exception as e:
            self._render_error(self.window.location.href or "Unknown", e)

    def _render_error(self, url: str, exception: Exception) -> None:
        self.window.console.error(f"Navigation error for {url}: {exception}")
        from pyweb_api.DOM import HTMLDivElement, HTMLPElementHTML
        root_dom_element = HTMLDivElement()
        p = HTMLPElementHTML()
        p.append_child(f"שגיאה: לא ניתן לטעון את הכתובת: {url}")
        p.append_child(f"\nשגיאה: {exception}")
        root_dom_element.append_child(p)
        render_element(self.render_area.widget, root_dom_element, self)

    def reload(self) -> None:
        self.render_area.clear()
        self.window.location.reload()

    def toggle_console(self) -> None:
        if self.console_container.isVisible():
            self.console_container.hide()
        else:
            self.console_container.show()

    def render_layout(self) -> None:
        self.root.setWindowTitle("PyWeb Client")
        
        central_widget = QWidget(self.root)
        self.root.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # Top bar toolbar
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)

        btn_style = "QPushButton { background-color: #e5e7eb; color: #374151; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; } QPushButton:hover { background-color: #d1d5db; }"
        
        self.back_btn = QPushButton("←")
        self.back_btn.setStyleSheet(btn_style)
        self.back_btn.clicked.connect(self.window.location.back)
        top_layout.addWidget(self.back_btn)

        self.reload_btn = QPushButton("↻")
        self.reload_btn.setStyleSheet(btn_style)
        self.reload_btn.clicked.connect(self.reload)
        top_layout.addWidget(self.reload_btn)

        self.forward_btn = QPushButton("→")
        self.forward_btn.setStyleSheet(btn_style)
        self.forward_btn.clicked.connect(self.window.location.forward)
        top_layout.addWidget(self.forward_btn)

        # Address input
        self.address_input = QLineEdit("app://home")
        self.address_input.setStyleSheet("QLineEdit { background-color: #f9fafb; color: #1f2937; border: 1px solid #e5e7eb; border-radius: 4px; padding: 6px; font-size: 11pt; } QLineEdit:focus { border: 1px solid #3b82f6; }")
        self.address_input.returnPressed.connect(lambda: self.window.location.navigate(self.address_input.text()))
        top_layout.addWidget(self.address_input)

        self.go_btn = QPushButton("Go")
        self.go_btn.setStyleSheet("QPushButton { background-color: #10b981; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; } QPushButton:hover { background-color: #059669; }")
        self.go_btn.clicked.connect(lambda: self.window.location.navigate(self.address_input.text()))
        top_layout.addWidget(self.go_btn)

        self.file_btn = QPushButton("Open HTML")
        self.file_btn.setStyleSheet("QPushButton { background-color: #3b82f6; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; } QPushButton:hover { background-color: #2563eb; }")
        self.file_btn.clicked.connect(self.on_open_file)
        top_layout.addWidget(self.file_btn)

        self.console_btn = QPushButton("Console")
        self.console_btn.setStyleSheet("QPushButton { background-color: #6b7280; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; } QPushButton:hover { background-color: #4b5563; }")
        self.console_btn.clicked.connect(self.toggle_console)
        top_layout.addWidget(self.console_btn)

        main_layout.addWidget(top_bar)

        # Render area Scroll Panel
        self.render_area.render_init()
        main_layout.addWidget(self.render_area.scroll_area, stretch=1)

        # COLLAPSIBLE DEV CONSOLE
        self.console_container = QWidget()
        console_layout = QVBoxLayout(self.console_container)
        console_layout.setContentsMargins(0, 5, 0, 0)
        console_layout.setSpacing(0)

        # Console Header
        console_header = QWidget()
        console_header.setStyleSheet("background-color: #111827; border-top-left-radius: 4px; border-top-right-radius: 4px;")
        header_layout = QHBoxLayout(console_header)
        header_layout.setContentsMargins(8, 4, 8, 4)

        console_title = QLabel("Developer Console")
        console_title.setStyleSheet("color: #9ca3af; font-weight: bold; font-size: 9pt;")
        header_layout.addWidget(console_title)
        
        header_layout.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("QPushButton { color: white; font-weight: bold; font-size: 8pt; background-color: #374151; padding: 2px 6px; border: none; border-radius: 2px; } QPushButton:hover { background-color: #4b5563; }")
        clear_btn.clicked.connect(lambda: self.console_output.clear())
        header_layout.addWidget(clear_btn)

        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("QPushButton { color: #9ca3af; font-weight: bold; font-size: 9pt; border: none; background: transparent; } QPushButton:hover { color: white; }")
        close_btn.clicked.connect(self.toggle_console)
        header_layout.addWidget(close_btn)

        console_layout.addWidget(console_header)

        # Console Output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("QTextEdit { background-color: #1f2937; color: #10b981; font-family: 'Courier'; font-size: 10pt; border: none; border-bottom-left-radius: 4px; border-bottom-right-radius: 4px; }")
        self.console_output.setFixedHeight(120)
        console_layout.addWidget(self.console_output)

        main_layout.addWidget(self.console_container)

        # Register shortcuts
        self.net_inspect_action = QAction(self.root)
        self.net_inspect_action.setShortcut("F12")
        self.net_inspect_action.triggered.connect(self.open_network_inspector)
        self.root.addAction(self.net_inspect_action)

        self.dom_inspect_action = QAction(self.root)
        self.dom_inspect_action.setShortcut("Ctrl+Shift+I")
        self.dom_inspect_action.triggered.connect(self.open_dom_inspector)
        self.root.addAction(self.dom_inspect_action)

        self.toggle_console_action = QAction(self.root)
        self.toggle_console_action.setShortcut("Ctrl+Backspace")
        self.toggle_console_action.triggered.connect(self.toggle_console)
        self.root.addAction(self.toggle_console_action)

    def open_network_inspector(self) -> None:
        from pyweb_client.debug_tools import NetworkInspector
        inspector = NetworkInspector(self)
        inspector.show()
        self.root.inspector = inspector # Prevent garbage collection

    def open_dom_inspector(self) -> None:
        from pyweb_client.debug_tools import DOMInspector
        inspector = DOMInspector(self)
        inspector.show()
        self.root.dom_inspector = inspector # Prevent garbage collection

    def build_menu(self) -> None:
        menubar = self.root.menuBar()

        file_menu = menubar.addMenu("File")
        open_action = QAction("Open", self.root)
        open_action.triggered.connect(self.on_open_file)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self.root)
        exit_action.triggered.connect(self.root.close)
        file_menu.addAction(exit_action)

        self.history_menu = menubar.addMenu("History")
        print_history_action = QAction("Print History", self.root)
        print_history_action.triggered.connect(lambda: self.window.console.log(";-".join(self.window.location.history)))
        self.history_menu.addAction(print_history_action)
        clear_history_action = QAction("Clear History", self.root)
        clear_history_action.triggered.connect(self.window.location.clear_history)
        self.history_menu.addAction(clear_history_action)
        self.history_menu.addSeparator()

        debug_menu = menubar.addMenu("Debug")
        net_action = QAction("Network Inspector", self.root)
        net_action.triggered.connect(self.open_network_inspector)
        debug_menu.addAction(net_action)
        dom_action = QAction("DOM Inspector", self.root)
        dom_action.triggered.connect(self.open_dom_inspector)
        debug_menu.addAction(dom_action)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self.root)
        about_action.triggered.connect(lambda: self.window.console.log("PyWeb Client v0"))
        help_menu.addAction(about_action)


def run() -> None:
    app = QApplication(sys.argv)
    main_win = QMainWindow()
    client = PyWebClient(root=main_win)
    main_win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
