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

        # Set application logo/window icon
        import os
        from PIL import Image, ImageTk
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "assests", "logo.png")
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, photo)
                self.root.logo_image = photo  # Keep a reference to prevent garbage collection
        except Exception as e:
            print("Failed to load app logo:", e)

        self.render_area: RenderArea = RenderArea(self.root, self)
        self.address_input: Optional[tk.Entry] = None
        self.console_container: Optional[tk.Frame] = None
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
        import asyncio
        async def load_task():
            try:
                response = await self.router.resolve(url)
                self.root.after(0, lambda: self._render_content(response))
            except Exception as e:
                self.root.after(0, lambda: self._render_error(url, e))

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

    def create_premium_button(self, parent, text, command, bg_color="#4f46e5", fg_color="white", hover_bg="#4338ca"):
        btn = tk.Label(
            parent,
            text=text,
            bg=bg_color,
            fg=fg_color,
            font=("Helvetica", 10, "bold"),
            padx=12,
            pady=6,
            cursor="hand2",
            relief="flat",
            bd=0
        )
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg_color))
        return btn

    def toggle_console(self) -> None:
        if self.console_container.winfo_ismapped():
            self.console_container.pack_forget()
        else:
            self.console_container.pack(side="bottom", fill="x", padx=10, pady=(5, 10))

    def render_layout(self) -> None:
        self.root.title("PyWeb Client")
        self.root.configure(bg="#f3f4f6")

        # Top bar frame (modern light background with bottom border highlight)
        top_bar = tk.Frame(self.root, bg="#ffffff", pady=8, bd=1, relief="flat")
        top_bar.pack(fill="x", padx=10, pady=(10, 0))

        # Premium styled navigation buttons
        back_btn = self.create_premium_button(top_bar, "←", self.window.location.back, bg_color="#e5e7eb", fg_color="#374151", hover_bg="#d1d5db")
        back_btn.pack(side="left", padx=(5, 4), pady=2)

        reload_btn = self.create_premium_button(top_bar, "↻", self.reload, bg_color="#e5e7eb", fg_color="#374151", hover_bg="#d1d5db")
        reload_btn.pack(side="left", padx=(0, 4), pady=2)

        forward_btn = self.create_premium_button(top_bar, "→", self.window.location.forward, bg_color="#e5e7eb", fg_color="#374151", hover_bg="#d1d5db")
        forward_btn.pack(side="left", padx=(0, 12), pady=2)

        # Address bar with high contrast border and large legibility
        self.address_input = tk.Entry(
            top_bar,
            font=("Helvetica", 11),
            bg="#f9fafb",
            fg="#1f2937",
            relief="solid",
            bd=1,
            insertbackground="#1f2937",
            highlightthickness=1,
            highlightbackground="#e5e7eb",
            highlightcolor="#3b82f6"
        )
        self.address_input.insert(0, "app://home")
        self.address_input.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=2)
        self.address_input.bind("<Return>", lambda e: self.window.location.navigate(self.address_input.get()))

        go_btn = self.create_premium_button(top_bar, "Go", lambda: self.window.location.navigate(self.address_input.get()), bg_color="#10b981", hover_bg="#059669")
        go_btn.pack(side="left", padx=(0, 8), pady=2)

        file_btn = self.create_premium_button(top_bar, "Open HTML", self.on_open_file, bg_color="#3b82f6", hover_bg="#2563eb")
        file_btn.pack(side="left", padx=(0, 8), pady=2)

        console_btn = self.create_premium_button(top_bar, "Console", self.toggle_console, bg_color="#6b7280", hover_bg="#4b5563")
        console_btn.pack(side="left", padx=(0, 5), pady=2)

        # Console container frame
        self.console_container = tk.Frame(self.root, bg="#1f2937")
        
        # Console header bar
        console_header = tk.Frame(self.console_container, bg="#111827", height=24)
        console_header.pack(fill="x", side="top")
        
        console_title = tk.Label(console_header, text="Developer Console", bg="#111827", fg="#9ca3af", font=("Helvetica", 9, "bold"))
        console_title.pack(side="left", padx=10, pady=2)
        
        clear_btn = tk.Label(console_header, text="Clear", bg="#374151", fg="white", font=("Helvetica", 8, "bold"), cursor="hand2", padx=6)
        clear_btn.bind("<Button-1>", lambda e: self.console_output.delete("1.0", tk.END))
        clear_btn.bind("<Enter>", lambda e: clear_btn.configure(bg="#4b5563"))
        clear_btn.bind("<Leave>", lambda e: clear_btn.configure(bg="#374151"))
        clear_btn.pack(side="right", padx=5, pady=2)
        
        close_btn = tk.Label(console_header, text="✕", bg="#111827", fg="#9ca3af", font=("Helvetica", 9, "bold"), cursor="hand2", padx=6)
        close_btn.bind("<Button-1>", lambda e: self.toggle_console())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(fg="white"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(fg="#9ca3af"))
        close_btn.pack(side="right", padx=5, pady=2)
        
        self.console_output = scrolledtext.ScrolledText(
            self.console_container, 
            height=7, 
            bg="#1f2937", 
            fg="#10b981", 
            insertbackground="white", 
            font=("Courier", 10),
            relief="flat",
            bd=0
        )
        self.console_output.pack(fill="both", expand=True)
        
        # Start with console shown
        self.console_container.pack(side="bottom", fill="x", padx=10, pady=(5, 10))

        self.render_area.render_init()
        # Log to console after it's created
        self.window.console.log("Console initialized.")
        self.root.bind("<Button-1>", self._on_click_root)
        self.root.bind("<F12>", lambda e: self.open_network_inspector())
        self.root.bind("<Control-Shift-Key-I>", lambda e: self.open_dom_inspector())
        # self.root.bind("<Control-Shift-key-i>", lambda e: self.open_dom_inspector())
        self.root.bind("<Control-BackSpace>", lambda e: self.toggle_console())
        # self.root.bind("<Control-quote>", lambda e: self.toggle_console())
        self.root.bind("<Control-dead_grave>", lambda e: self.toggle_console())
        self.root.bind("<Control-asciitilde>", lambda e: self.toggle_console())
        self.root.bind("<Control-grave>", lambda e: self.toggle_console())

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
