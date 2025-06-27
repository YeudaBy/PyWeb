import tkinter as tk
from tkinter import filedialog, scrolledtext

from pyweb_api.DOM import Div, P, Button
from pyweb_api.Window import Location, Console
from pyweb_client.html_parser import PyHTMLParser
from pyweb_client.network import fetch_html
from pyweb_client.render import render_element


class PyWebClient:
    def __init__(self, root):
        self.render_area_canvas = None
        self.root = root
        self.address_input = None
        self.render_area = None
        self.console_output = None

        self.location = Location(self._on_location_change)
        self.console = Console(self._render_log)

        # Maximize window and focus
        self.root.state('zoomed')  # For Windows/Linux
        self.root.focus_force()

        self.render_layout()
        self.build_menu()

    def render(self):
        self.root.mainloop()

    def on_open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("HTML files", "*.html")])
        if file_path:
            self.location.navigate(f"file://{file_path}")

    def _render_log(self, level, message):
        if self.console_output:
            self.console_output.insert(tk.END, f"<{level}>: {message}\n")
            self.console_output.see(tk.END)

    def _on_location_change(self, url):
        self.console.log(f"Navigating to: {url}")
        self.clear_render_area()
        self.address_input.delete(0, tk.END)
        self.address_input.insert(0, url)

        if url == "app://home":
            root_dom_element = Div()
            p = P()
            p.append_child("ברוך הבא ל-PyWeb Client!")
            root_dom_element.append_child(p)


            btn = Button(attrs={"value": "Click"})

            def click_test(event):
                self.console.log(event)
                btn.set_text("Clicked!")

            root_dom_element.append_child(btn)
            btn.add_event_listener("click", click_test)


            render_element(self.render_area, root_dom_element, self)
            self.console.log("Home page rendered.")

        elif url == "app://example_page":
            root_dom_element = Div()
            root_dom_element.append_child(P())
            root_dom_element.children[-1].append_child("זהו דף לדוגמה.")
            btn = Button(attrs={"value": "חזור לדף הבית"})
            root_dom_element.append_child(btn)
            render_element(self.render_area, root_dom_element, self)
            self.console.log("Example page rendered.")

        elif url.startswith("file://"):
            file_path = url[len("file://"):]
            self._load_html_file(file_path)

        elif url.startswith("http"):
            try:
                content = fetch_html(url)
                parser = PyHTMLParser()
                parser.feed(content)
                render_element(self.render_area, parser.root, self)
            except Exception as e:
                content = P()
                content.children.append(f"ERROR: {e}")
                render_element(self.render_area, content, self)

        elif url.startswith("/"):
            try:
                content = fetch_html(self.address_input.get() + url)
                parser = PyHTMLParser()
                parser.feed(content)
                render_element(self.render_area, parser.root, self)
            except Exception as e:
                content = P()
                content.children.append(f"ERROR: {e}")
                render_element(self.render_area, content, self)

        else:
            self.console.error(f"Unknown URL scheme or page: {url}")
            root_dom_element = Div()
            root_dom_element.append_child(P())
            root_dom_element.children[-1].append_child(f"שגיאה: לא ניתן לטעון את הכתובת: {url}")
            render_element(self.render_area, root_dom_element, self)

    def _load_html_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                self.console.log(f"Selected file: {file_path}")
                parser = PyHTMLParser()
                parser.feed(f.read())
                render_element(self.render_area, parser.root, self)
                self.console.log(f'file {file_path} rendered!')
        except Exception as e:
            self.console.error(e)

    def clear_render_area(self):
        for widget in self.render_area.winfo_children():
            widget.destroy()

    def _on_render_area_conf(self, event):
        self.render_area_canvas.configure(scrollregion=self.render_area_canvas.bbox("all"))

    def _on_mouse_wheel(self, event):
        self.console.log(f"Mouse Wheel Event: {event}")

        scroll_val = 0
        if event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):  # Scroll Down
            scroll_val = 1
        elif event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):  # Scroll Up
            scroll_val = -1

        if scroll_val != 0:
            self.render_area_canvas.yview_scroll(scroll_val, "units")

    def render_layout(self):
        self.root.title("PyWeb Client v0")
        self.root.configure(bg="#f0f0f0")

        # Top bar frame
        top_bar = tk.Frame(self.root, pady=5, relief="groove")
        top_bar.pack(fill="x", padx=10, pady=(10, 0))

        back_btn = tk.Button(top_bar, text="<", command=self.location.back, bg="#4285F4", relief="raised")
        back_btn.pack(side="left", pady=5, padx=(0, 5))

        forward_btn = tk.Button(top_bar, text=">", command=self.location.forward, bg="#4285F4", relief="raised")
        forward_btn.pack(side="left", pady=5, padx=(0, 10))
        #
        self.address_input = tk.Entry(top_bar, width=60, relief="sunken", bd=2, bg="white")
        self.address_input.insert(0, "app://home")
        self.address_input.pack(side="left", pady=5, fill="y")
        #
        go_btn = tk.Button(top_bar, text="Go", command=lambda: self.location.navigate(self.address_input.get()),
                           bg="#4285F4",
                           relief="raised")
        go_btn.pack(side="left", pady=5)

        file_btn = tk.Button(top_bar, text="Open HTML", command=self.on_open_file, bg="#34A853", relief="raised")
        file_btn.pack(side="left", padx=(10, 0), pady=5)

        # Console area - We pack it FIRST with side=bottom
        self.console_output = scrolledtext.ScrolledText(self.root, height=8, bg="black", fg="lime",
                                                        insertbackground="black")
        self.console_output.pack(side="bottom", fill="x", padx=10, pady=(5, 10))

        # Render area - This will now fill the remaining space
        self.render_area_canvas = tk.Canvas(self.root, borderwidth=0)
        self.render_area = tk.Frame(self.render_area_canvas)
        self.vsb = tk.Scrollbar(self.root, orient="vertical", command=self.render_area_canvas.yview)
        self.render_area_canvas.configure(yscrollcommand=self.vsb.set)
        #
        self.vsb.pack(side="right", fill="y", pady=(10, 0))
        self.render_area_canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(10, 0))

        self.render_area_canvas.create_window((0, 0), window=self.render_area, anchor="nw")

        self.render_area.bind("<Configure>", self._on_render_area_conf)

        # Bind mouse wheel scrolling
        self.root.bind_all("<MouseWheel>", self._on_mouse_wheel)  # For Windows and MacOS
        self.root.bind_all("<Button-4>", self._on_mouse_wheel)  # For Linux (scroll up)
        self.root.bind_all("<Button-5>", self._on_mouse_wheel)  # For Linux (scroll down)

        # Log to console after it's created
        self.console.log("Console initialized.")

    def build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.on_open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        history_menu = tk.Menu(menubar, tearoff=0)
        history_menu.add_command(label="Print History", command=lambda: self.console.log(";-".join(self.location.history)))
        menubar.add_cascade(label="History", menu=history_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: self.console.log("PyWeb Client v0"))
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)


def run():
    root = tk.Tk()
    client = PyWebClient(root=root)
    client.render()


if __name__ == "__main__":
    run()
