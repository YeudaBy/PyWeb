import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
from typing import Optional

from pyweb_api.Window.main import Window
from pyweb_client.layout.RenderArea import RenderArea
from pyweb_client.render import render_element
from pyweb_client.router import ProtocolRouter, AppSchemeHandler, FileSchemeHandler, HttpSchemeHandler, RelativeSchemeHandler


class PyWebClient:
    def __init__(self, root: tk.Tk):
        self.root: tk.Tk = root

        self.render_area: RenderArea = RenderArea(self.root, self)
        self.address_input: Optional[tk.Entry] = None
        self.console_output: Optional[scrolledtext.ScrolledText] = None

        self.window: Window = Window(self)

        # Maximize window and focus
        self.root.state('zoomed')
        self.root.focus_force()

        # Initialize protocol scheme router
        self.router: ProtocolRouter = ProtocolRouter()
        self.router.register_handler("app", AppSchemeHandler(self))
        self.router.register_handler("file", FileSchemeHandler())
        self.router.register_handler("http", HttpSchemeHandler())
        self.router.register_handler("https", HttpSchemeHandler())
        self.router.register_handler("relative", RelativeSchemeHandler(self))

        self.render_layout()
        self.build_menu()

        # Start interactive REPL console asynchronously in background
        from pyweb_client.script_engine import PyWebInterpreter
        self.interpreter: PyWebInterpreter = PyWebInterpreter(self)
        threading.Thread(target=self.interpreter.open_console, daemon=True).start()

    def render(self) -> None:
        self.root.mainloop()

    def on_open_file(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("HTML files", "*.html")])
        if file_path:
            self.window.location.navigate(f"file://{file_path}")

    def _render_log(self, level: str, message: str) -> None:
        if self.console_output:
            self.console_output.insert(tk.END, f"<{level}>: {message}\n")
            self.console_output.see(tk.END)

    def _on_click_root(self, event: tk.Event) -> None:
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        self.window.console.log(widget, "clicked")

    def _on_location_change(self, url: str) -> None:
        self.window.console.log(f"Navigating to: {url}")
        self.history_menu.add_command(label=url, command=lambda: self.window.location.navigate(url))
        self.render_area.clear()
        
        if self.address_input:
            self.address_input.delete(0, tk.END)
            self.address_input.insert(0, url)

        # Asynchronously resolve url via scheme handlers
        def load_thread() -> None:
            try:
                response = self.router.resolve(url)
                self.root.after(0, lambda: self._render_content(response))
            except Exception as e:
                self.root.after(0, lambda: self._render_error(url, e))

        threading.Thread(target=load_thread, daemon=True).start()

    def _render_content(self, response) -> None:
        from pyweb_api.DOM import HTMLElement
        from pyweb_client.html_parser import PyHTMLParser
        
        try:
            if isinstance(response.content, HTMLElement):
                render_element(self.render_area.widget, response.content, self)
            else:
                parser = PyHTMLParser()
                parser.feed(response.content)
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

    def render_layout(self) -> None:
        self.root.title("PyWeb Client v0")
        self.root.configure(bg="#f0f0f0")

        # Top bar frame
        top_bar = tk.Frame(self.root, pady=5, relief="groove")
        top_bar.pack(fill="x", padx=10, pady=(10, 0))

        back_btn = tk.Button(top_bar, text="<", command=self.window.location.back, bg="#4285F4", relief="raised")
        back_btn.pack(side="left", pady=5, padx=(0, 5))

        reload_btn = tk.Button(top_bar, text="reload", command=self.reload, bg="#4285F4", relief="raised")
        reload_btn.pack(side="left", pady=5, padx=(0, 10))

        forward_btn = tk.Button(top_bar, text=">", command=self.window.location.forward, bg="#4285F4", relief="raised")
        forward_btn.pack(side="left", pady=5, padx=(0, 15))

        self.address_input = tk.Entry(top_bar, width=60, relief="sunken", bd=2, bg="white")
        self.address_input.insert(0, "app://home")
        self.address_input.pack(side="left", pady=5, fill="y")

        go_btn = tk.Button(top_bar, text="Go", command=lambda: self.window.location.navigate(self.address_input.get()),
                           bg="#4285F4",
                           relief="raised")
        go_btn.pack(side="left", pady=5)

        file_btn = tk.Button(top_bar, text="Open HTML", command=self.on_open_file, bg="#34A853", relief="raised")
        file_btn.pack(side="left", padx=(10, 0), pady=5)

        # Console area - We pack it FIRST with side=bottom
        self.console_output = scrolledtext.ScrolledText(self.root, height=8, bg="black", fg="lime",
                                                        insertbackground="black")
        self.console_output.pack(side="bottom", fill="x", padx=10, pady=(5, 10))

        self.render_area.render_init()
        # Log to console after it's created
        self.window.console.log("Console initialized.")
        self.root.bind("<Button-1>", self._on_click_root)
        self.root.bind("<F12>", lambda e: self.open_network_inspector())
        self.root.bind("<Control-Shift-Key-I>", lambda e: self.open_dom_inspector())
        # self.root.bind("<Control-Shift-key-i>", lambda e: self.open_dom_inspector())

    def open_network_inspector(self) -> None:
        from pyweb_client.debug_tools import NetworkInspector
        NetworkInspector(self)

    def open_dom_inspector(self) -> None:
        from pyweb_client.debug_tools import DOMInspector
        DOMInspector(self)

    def build_menu(self) -> None:
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.on_open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        history_menu = tk.Menu(menubar, tearoff=0)
        history_menu.add_command(label="Print History",
                                 command=lambda: self.window.console.log(";-".join(self.window.location.history)))
        history_menu.add_command(label="Clear History",
                                 command=self.window.location.clear_history)
        history_menu.add_separator()
        menubar.add_cascade(label="History", menu=history_menu)
        self.history_menu = history_menu

        debug_menu = tk.Menu(menubar, tearoff=0)
        debug_menu.add_command(label="Network Inspector", command=self.open_network_inspector)
        debug_menu.add_command(label="DOM Inspector", command=self.open_dom_inspector)
        menubar.add_cascade(label="Debug", menu=debug_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: self.window.console.log("PyWeb Client v0"))
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)


def run() -> None:
    root = tk.Tk()
    client = PyWebClient(root=root)
    client.render()


if __name__ == "__main__":
    run()
