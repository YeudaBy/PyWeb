from pyweb_api.Window.Console import Console
from pyweb_api.Window.Document import Document
from pyweb_api.Window.Location import Location
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyweb_client.main import PyWebClient


class Window:
    def __init__(self, client: 'PyWebClient'):
        self.console = Console(client._render_log)
        self.location = Location(client._on_location_change)
        self.document = Document()
