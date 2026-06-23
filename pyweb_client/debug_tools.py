import tkinter as tk
from tkinter import ttk, scrolledtext
from pyweb_api.network import network_inspector_log
from pyweb_api.DOM.HTMLElement import HTMLElement


class NetworkInspector:
    def __init__(self, client):
        self.client = client
        self.window = tk.Toplevel(client.root)
        self.window.title("PyWeb Developer Tools - Network Inspector")
        self.window.geometry("800x600")
        
        self.create_widgets()
        self.refresh_log()

    def create_widgets(self):
        # Top toolbar
        toolbar = tk.Frame(self.window, pady=5, bg="#f0f0f0")
        toolbar.pack(fill="x")
        
        refresh_btn = tk.Button(toolbar, text="Refresh", command=self.refresh_log, bg="#4285F4", fg="black")
        refresh_btn.pack(side="left", padx=5)
        
        clear_btn = tk.Button(toolbar, text="Clear Log", command=self.clear_log, bg="#EA4335", fg="black")
        clear_btn.pack(side="left", padx=5)
        
        # Split pane
        paned = ttk.PanedWindow(self.window, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left side: Request list
        left_frame = tk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        self.tree = ttk.Treeview(left_frame, columns=("method", "status", "url"), show="headings")
        self.tree.heading("method", text="Method")
        self.tree.heading("status", text="Status")
        self.tree.heading("url", text="URL")
        
        self.tree.column("method", width=70, anchor="center")
        self.tree.column("status", width=60, anchor="center")
        self.tree.column("url", width=250, anchor="w")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_request)
        
        # Right side: Detail notebook
        right_frame = tk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Headers Tab
        self.headers_text = scrolledtext.ScrolledText(self.notebook, bg="white", fg="black")
        self.notebook.add(self.headers_text, text="Headers")
        
        # Body Tab
        self.body_text = scrolledtext.ScrolledText(self.notebook, bg="white", fg="black")
        self.notebook.add(self.body_text, text="Response Info")
        
        # Summary Tab
        self.summary_text = scrolledtext.ScrolledText(self.notebook, bg="white", fg="black")
        self.notebook.add(self.summary_text, text="Summary")

    def refresh_log(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.request_map = {}
        for idx, log in enumerate(network_inspector_log):
            item_id = self.tree.insert("", "end", values=(log["method"], log["status"], log["url"]))
            self.request_map[item_id] = log

    def clear_log(self):
        network_inspector_log.clear()
        self.refresh_log()
        self.headers_text.delete("1.0", tk.END)
        self.body_text.delete("1.0", tk.END)
        self.summary_text.delete("1.0", tk.END)

    def on_select_request(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        log = self.request_map.get(selected[0])
        if not log:
            return
            
        # Update Headers
        self.headers_text.delete("1.0", tk.END)
        self.headers_text.insert(tk.END, "=== REQUEST HEADERS ===\n")
        for k, v in log["request_headers"].items():
            self.headers_text.insert(tk.END, f"{k}: {v}\n")
            
        self.headers_text.insert(tk.END, "\n=== RESPONSE HEADERS ===\n")
        for k, v in log["response_headers"].items():
            self.headers_text.insert(tk.END, f"{k}: {v}\n")
            
        # Update Body/Payload info
        self.body_text.delete("1.0", tk.END)
        if log.get("request_body"):
            self.body_text.insert(tk.END, "=== REQUEST BODY ===\n")
            self.body_text.insert(tk.END, f"{log['request_body']}\n\n")
        
        self.body_text.insert(tk.END, f"Response Body Size: {log.get('response_body_size', 0)} bytes\n")
        
        # Update Summary
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert(tk.END, f"URL: {log['url']}\n\n")
        self.summary_text.insert(tk.END, f"Method: {log['method']}\n")
        self.summary_text.insert(tk.END, f"Status Code: {log['status']}\n")
        self.summary_text.insert(tk.END, f"Response Size: {log.get('response_body_size', 0)} bytes\n")


class DOMInspector:
    def __init__(self, client):
        self.client = client
        self.window = tk.Toplevel(client.root)
        self.window.title("PyWeb Developer Tools - DOM Inspector")
        self.window.geometry("800x600")
        
        self.node_map = {}
        self.create_widgets()
        self.refresh_tree()

    def create_widgets(self):
        # Top toolbar
        toolbar = tk.Frame(self.window, pady=5, bg="#f0f0f0")
        toolbar.pack(fill="x")
        
        refresh_btn = tk.Button(toolbar, text="Refresh", command=self.refresh_tree, bg="#4285F4", fg="black")
        refresh_btn.pack(side="left", padx=5)
        
        # Split pane
        paned = ttk.PanedWindow(self.window, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left side: DOM Tree
        left_frame = tk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        self.tree = ttk.Treeview(left_frame, show="tree")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_node)
        
        # Right side: Detail notebook
        right_frame = tk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Attributes Tab
        self.attrs_text = scrolledtext.ScrolledText(self.notebook, bg="white", fg="black")
        self.notebook.add(self.attrs_text, text="Attributes")
        
        # Styles Tab
        self.styles_text = scrolledtext.ScrolledText(self.notebook, bg="white", fg="black")
        self.notebook.add(self.styles_text, text="Styles")
        
        # Text Tab
        self.value_text = scrolledtext.ScrolledText(self.notebook, bg="white", fg="black")
        self.notebook.add(self.value_text, text="Text / Value")

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.node_map = {}
        document = self.client.window.document
        if document:
            self.populate_tree("", document)

    def populate_tree(self, parent_item, element):
        if isinstance(element, str):
            text_val = element.strip()
            if text_val:
                disp_text = f"Text: \"{text_val[:30]}\"" if len(text_val) > 30 else f"Text: \"{text_val}\""
                item_id = self.tree.insert(parent_item, "end", text=disp_text)
                self.node_map[item_id] = element
        else:
            tag_name = element.tag
            disp_text = f"<{tag_name}>"
            if element.attrs:
                attrs_str = " ".join([f'{k}="{v}"' for k, v in element.attrs.items() if k != "style"])
                if attrs_str:
                    disp_text = f"<{tag_name} {attrs_str}>"
            item_id = self.tree.insert(parent_item, "end", text=disp_text)
            self.node_map[item_id] = element
            
            for child in element.children:
                self.populate_tree(item_id, child)

    def on_select_node(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        node = self.node_map.get(selected[0])
        self.attrs_text.delete("1.0", tk.END)
        self.styles_text.delete("1.0", tk.END)
        self.value_text.delete("1.0", tk.END)
        
        if isinstance(node, str):
            self.attrs_text.insert(tk.END, "Plain Text Node\n")
            self.value_text.insert(tk.END, node)
        elif isinstance(node, HTMLElement):
            self.attrs_text.insert(tk.END, f"Tag: {node.tag}\n\n")
            self.attrs_text.insert(tk.END, "=== ATTRIBUTES ===\n")
            for k, v in node.attrs.items():
                if k != "style":
                    self.attrs_text.insert(tk.END, f"{k}: {v}\n")
            
            self.styles_text.insert(tk.END, "=== INLINE STYLES ===\n")
            style_str = node.attrs.get("style", "")
            self.styles_text.insert(tk.END, f"Raw style: {style_str}\n\n")
            style_dict = node._get_style_dict()
            for k, v in style_dict.items():
                self.styles_text.insert(tk.END, f"{k}: {v}\n")
                
            self.value_text.insert(tk.END, "=== TEXT CONTENT ===\n")
            text_content = "".join([c if isinstance(c, str) else "" for c in node.children])
            self.value_text.insert(tk.END, text_content)
