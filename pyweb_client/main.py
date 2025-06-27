import tkinter as tk
from tkinter import filedialog, scrolledtext

from pyweb_api.DOM import Div, P, Button
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

        self.history = []
        self.current_history_index = -1

        # Maximize window and focus
        self.root.state('zoomed')  # For Windows/Linux
        self.root.focus_force()

        self.render_layout()
        self.build_menu()

    def render(self):
        self.root.mainloop()

    def render_layout(self):
        self.root.title("PyWeb Client v0")
        self.root.configure(bg="#f0f0f0")

        # Top bar frame
        top_bar = tk.Frame(self.root, pady=5, relief="groove")
        top_bar.pack(fill="x", padx=10, pady=(10, 0))

        back_btn = tk.Button(top_bar, text="<", command=self.go_back, bg="#4285F4", relief="raised")
        back_btn.pack(side="left", pady=5, padx=(0, 5))  # מרווח קטן מימין

        forward_btn = tk.Button(top_bar, text=">", command=self.go_forward, bg="#4285F4", relief="raised")
        forward_btn.pack(side="left", pady=5, padx=(0, 10))  # מרווח קטן מימין
        #
        self.address_input = tk.Entry(top_bar, width=60, relief="sunken", bd=2, bg="white")
        self.address_input.insert(0, "app://home")
        self.address_input.pack(side="left", pady=5, fill="y")
        #
        go_btn = tk.Button(top_bar, text="Go", command=lambda: self.navigate_to(self.address_input.get()), bg="#4285F4",
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

        self.render_area.bind("<Configure>", self.onFrameConfigure)
        # Bind mouse wheel scrolling
        # שים לב לתיקון כאן: הפניה ל-self._on_mouse_wheel
        self.root.bind_all("<MouseWheel>", self._on_mouse_wheel)  # For Windows and MacOS
        self.root.bind_all("<Button-4>", self._on_mouse_wheel)  # For Linux (scroll up)
        self.root.bind_all("<Button-5>", self._on_mouse_wheel)  # For Linux (scroll down)

        # Log to console after it's created
        self.console_log("Console initialized.")

    def clear_render_area(self):
        for widget in self.render_area.winfo_children():
            widget.destroy()

    def onFrameConfigure(self, event):
        self.render_area_canvas.configure(scrollregion=self.render_area_canvas.bbox("all"))

    def _on_mouse_wheel(self, event):
        # הדפסה זו טובה לבדיקה, השאר אותה
        self.console_log(f"Mouse Wheel Event: {event}")
        """Handle mouse wheel scrolling for cross-platform compatibility."""

        scroll_val = 0
        if event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):  # Scroll Down
            scroll_val = 1
        elif event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):  # Scroll Up
            scroll_val = -1

        if scroll_val != 0:
            self.render_area_canvas.yview_scroll(scroll_val, "units")

    def build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.on_open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy")
        edit_menu.add_command(label="Paste")
        menubar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: self.console_log("PyWeb Client v0"))
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def on_go(self):
        url = self.address_input.get()
        self.console_log(f"Routing to {url}")
        self.clear_render_area()

        file_html = fetch_html(url)
        parser = PyHTMLParser()
        parser.feed(file_html)

        render_element(self.render_area, parser.root, self)

    def on_open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("HTML files", "*.html")])
        if file_path:
            # שינוי: במקום לטעון ישירות, נקרא ל-navigate_to עם נתיב הקובץ כ-URL
            self.navigate_to(f"file://{file_path}")

    def console_log(self, message):
        print(f"[console] {message}")  # For debug in terminal
        if self.console_output:
            self.console_output.insert(tk.END, f"{message}\n")
            self.console_output.see(tk.END)

    def navigate_to(self, url, add_to_history=True):
        """
        Navigates to a given URL, updates the address bar, and manages history.
        """
        self.console_log(f"Navigating to: {url}")
        self.clear_render_area()

        self.address_input.delete(0, tk.END)
        self.address_input.insert(0, url)

        if add_to_history:
            if self.current_history_index < len(self.history) - 1:
                self.history = self.history[:self.current_history_index + 1]

            self.history.append(url)
            self.current_history_index = len(self.history) - 1
            self.console_log(f"History updated: {self.history}, current index: {self.current_history_index}")

        if url == "app://home":
            root_dom_element = Div()
            root_dom_element.append_child(P())
            root_dom_element.children[-1].append_child("ברוך הבא ל-PyWeb Client!")
            root_dom_element.append_child(P())

            btn = Button(attrs={"value": "עבור לדף לדוגמה", "pyweb_onclick": "app://example_page"})
            root_dom_element.append_child(btn)

            render_element(self.render_area, root_dom_element, self)
            self.console_log("Home page rendered.")

        elif url == "app://example_page":
            root_dom_element = Div()
            root_dom_element.append_child(P())
            root_dom_element.children[-1].append_child("זהו דף לדוגמה.")
            btn = Button(attrs={"value": "חזור לדף הבית", "pyweb_onclick": "app://home"})
            root_dom_element.append_child(btn)
            render_element(self.render_area, root_dom_element, self)
            self.console_log("Example page rendered.")

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
            self.console_log(f"ERROR: Unknown URL scheme or page: {url}")
            root_dom_element = Div()
            root_dom_element.append_child(P())
            root_dom_element.children[-1].append_child(f"שגיאה: לא ניתן לטעון את הכתובת: {url}")
            render_element(self.render_area, root_dom_element, self)

    def go_back(self):
        if self.current_history_index > 0:
            self.current_history_index -= 1
            url_to_load = self.history[self.current_history_index]
            self.navigate_to(url_to_load, add_to_history=False)
        else:
            self.console_log("Cannot go back - already at the beginning of history.")

    def go_forward(self):
        if self.current_history_index < len(self.history) - 1:
            self.current_history_index += 1
            url_to_load = self.history[self.current_history_index]
            self.navigate_to(url_to_load, add_to_history=False)
        else:
            self.console_log("Cannot go forward - already at the end of history.")

    def _load_html_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                self.console_log(f"Selected file: {file_path}")
                parser = PyHTMLParser()
                parser.feed(f.read())
                render_element(self.render_area, parser.root, self)
                self.console_log(f'file {file_path} rendered!')
        except Exception as e:
            self.console_log(f"ERROR: {e}")


def run():
    root = tk.Tk()
    client = PyWebClient(root=root)
    client.render()


if __name__ == "__main__":
    run()
