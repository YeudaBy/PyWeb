from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget, QTextEdit, QLabel)
from PyQt6.QtCore import Qt

from pyweb_api.network import network_inspector_log
from pyweb_api.DOM.HTMLElement import HTMLElement


class NetworkInspector(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle("PyWeb Developer Tools - Network Inspector")
        self.resize(800, 600)
        
        self.request_map = {}
        self.create_widgets()
        self.refresh_log()

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Top toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(5)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("QPushButton { background-color: #4285F4; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; } QPushButton:hover { background-color: #357ae8; }")
        refresh_btn.clicked.connect(self.refresh_log)
        toolbar_layout.addWidget(refresh_btn)

        clear_btn = QPushButton("Clear Log")
        clear_btn.setStyleSheet("QPushButton { background-color: #EA4335; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; } QPushButton:hover { background-color: #d62516; }")
        clear_btn.clicked.connect(self.clear_log)
        toolbar_layout.addWidget(clear_btn)

        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar)

        # Splitter pane
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter, stretch=1)

        # Left side: Request list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Method", "Status", "URL"])
        self.tree.itemSelectionChanged.connect(self.on_select_request)
        left_layout.addWidget(self.tree)
        splitter.addWidget(left_widget)

        # Right side: Detail tabs
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.notebook = QTabWidget()
        right_layout.addWidget(self.notebook)
        splitter.addWidget(right_widget)

        # Headers Tab
        self.headers_text = QTextEdit()
        self.headers_text.setReadOnly(True)
        self.notebook.addTab(self.headers_text, "Headers")

        # Body Tab
        self.body_text = QTextEdit()
        self.body_text.setReadOnly(True)
        self.notebook.addTab(self.body_text, "Response Info")

        # Summary Tab
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.notebook.addTab(self.summary_text, "Summary")

        splitter.setSizes([350, 450])

    def refresh_log(self):
        self.tree.clear()
        self.request_map = {}
        for idx, log in enumerate(network_inspector_log):
            item = QTreeWidgetItem([log["method"], str(log["status"]), log["url"]])
            self.tree.addTopLevelItem(item)
            self.request_map[id(item)] = log

    def clear_log(self):
        network_inspector_log.clear()
        self.refresh_log()
        self.headers_text.clear()
        self.body_text.clear()
        self.summary_text.clear()

    def on_select_request(self):
        selected = self.tree.selectedItems()
        if not selected:
            return
        
        log = self.request_map.get(id(selected[0]))
        if not log:
            return
            
        # Update Headers
        self.headers_text.clear()
        self.headers_text.append("=== REQUEST HEADERS ===")
        for k, v in log["request_headers"].items():
            self.headers_text.append(f"{k}: {v}")
            
        self.headers_text.append("\n=== RESPONSE HEADERS ===")
        for k, v in log["response_headers"].items():
            self.headers_text.append(f"{k}: {v}")
            
        # Update Body/Payload info
        self.body_text.clear()
        if log.get("request_body"):
            self.body_text.append("=== REQUEST BODY ===")
            self.body_text.append(f"{log['request_body']}\n")
        
        self.body_text.append(f"Response Body Size: {log.get('response_body_size', 0)} bytes")
        
        # Update Summary
        self.summary_text.clear()
        self.summary_text.append(f"URL: {log['url']}\n")
        self.summary_text.append(f"Method: {log['method']}")
        self.summary_text.append(f"Status Code: {log['status']}")
        self.summary_text.append(f"Response Size: {log.get('response_body_size', 0)} bytes")


class DOMInspector(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle("PyWeb Developer Tools - DOM Inspector")
        self.resize(800, 600)
        
        self.node_map = {}
        self.create_widgets()
        self.refresh_tree()

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Top toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(5)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("QPushButton { background-color: #4285F4; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; } QPushButton:hover { background-color: #357ae8; }")
        refresh_btn.clicked.connect(self.refresh_tree)
        toolbar_layout.addWidget(refresh_btn)

        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar)

        # Splitter pane
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter, stretch=1)

        # Left side: DOM Tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("DOM Elements")
        self.tree.itemSelectionChanged.connect(self.on_select_node)
        left_layout.addWidget(self.tree)
        splitter.addWidget(left_widget)

        # Right side: Detail notebook
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.notebook = QTabWidget()
        right_layout.addWidget(self.notebook)
        splitter.addWidget(right_widget)

        # Attributes Tab
        self.attrs_text = QTextEdit()
        self.attrs_text.setReadOnly(True)
        self.notebook.addTab(self.attrs_text, "Attributes")

        # Styles Tab
        self.styles_text = QTextEdit()
        self.styles_text.setReadOnly(True)
        self.notebook.addTab(self.styles_text, "Styles")

        # Text Tab
        self.value_text = QTextEdit()
        self.value_text.setReadOnly(True)
        self.notebook.addTab(self.value_text, "Text / Value")

        splitter.setSizes([350, 450])

    def refresh_tree(self):
        self.tree.clear()
        self.node_map = {}
        document = self.client.window.document
        if document and document.children:
            self.populate_tree(None, document.children[0])

    def populate_tree(self, parent_item, element):
        if isinstance(element, str):
            text_val = element.strip()
            if text_val:
                disp_text = f"Text: \"{text_val[:30]}\"" if len(text_val) > 30 else f"Text: \"{text_val}\""
                item = QTreeWidgetItem([disp_text])
                if parent_item:
                    parent_item.addChild(item)
                else:
                    self.tree.addTopLevelItem(item)
                self.node_map[id(item)] = element
        else:
            tag_name = element.tag
            disp_text = f"<{tag_name}>"
            if element.attrs:
                attrs_str = " ".join([f'{k}="{v}"' for k, v in element.attrs.items() if k != "style"])
                if attrs_str:
                    disp_text = f"<{tag_name} {attrs_str}>"
            item = QTreeWidgetItem([disp_text])
            if parent_item:
                parent_item.addChild(item)
            else:
                self.tree.addTopLevelItem(item)
            self.node_map[id(item)] = element
            
            for child in element.children:
                self.populate_tree(item, child)

    def on_select_node(self):
        selected = self.tree.selectedItems()
        if not selected:
            return
            
        node = self.node_map.get(id(selected[0]))
        self.attrs_text.clear()
        self.styles_text.clear()
        self.value_text.clear()
        
        if isinstance(node, str):
            self.attrs_text.append("Plain Text Node")
            self.value_text.append(node)
        elif isinstance(node, HTMLElement):
            self.attrs_text.append(f"Tag: {node.tag}\n")
            self.attrs_text.append("=== ATTRIBUTES ===")
            for k, v in node.attrs.items():
                if k != "style":
                    self.attrs_text.append(f"{k}: {v}")
            
            self.styles_text.append("=== INLINE STYLES ===")
            style_str = node.attrs.get("style", "")
            self.styles_text.append(f"Raw style: {style_str}\n")
            style_dict = node._get_style_dict()
            for k, v in style_dict.items():
                self.styles_text.append(f"{k}: {v}")
                
            self.value_text.append("=== TEXT CONTENT ===")
            text_content = "".join([c if isinstance(c, str) else "" for c in node.children])
            self.value_text.append(text_content)
