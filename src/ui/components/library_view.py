import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

class LibraryView(ctk.CTkFrame):
    def __init__(self, master, cmd_search, cmd_cancel, on_select, on_double_click, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Barre de recherche
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="Chercher un mot-clé...")
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        search_entry.bind('<Return>', lambda e: cmd_search(self.search_var.get()))
        
        ctk.CTkButton(search_frame, text="🔍", width=40, command=lambda: cmd_search(self.search_var.get())).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(search_frame, text="❌", width=40, fg_color="#a83232", hover_color="#872727", command=cmd_cancel).pack(side=tk.LEFT)

        # Arborescence
        tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        tree_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        self.tree = ttk.Treeview(tree_frame, columns=("chemin", "type"), show="tree", selectmode="browse")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        self.tree.bind('<<TreeviewSelect>>', on_select)
        self.tree.bind('<Double-1>', on_double_click)

    def get_search_text(self):
        return self.search_var.get()

    def clear_search(self):
        self.search_var.set("")