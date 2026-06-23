from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyweb_client.main import PyWebClient


class RenderArea:
    def __init__(self, root, cl: 'PyWebClient'):
        self.root = root
        self.cl = cl
        self.scroll_area = None
        self.widget = None

    def render_init(self):
        self.scroll_area = QScrollArea(self.root)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #f3f4f6; }")

        self.widget = QWidget()
        self.widget.setObjectName("RenderAreaWidget")
        self.widget.setStyleSheet("#RenderAreaWidget { background-color: white; border-radius: 8px; }")
        
        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.widget)

    def clear(self):
        if self.widget and self.widget.layout():
            layout = self.widget.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
