import customtkinter as ctk

class ImportExportPanel(ctk.CTkFrame):
    def __init__(self, master, cmd_import, cmd_export, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Configuration pour que les boutons prennent 50% de l'espace
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        # Bouton Import
        self.btn_import = ctk.CTkButton(
            self, 
            text="📥 Importer ZIP", 
            command=cmd_import, 
            fg_color="#2fa572", 
            hover_color="#25855a"
        )
        self.btn_import.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Bouton Export
        self.btn_export = ctk.CTkButton(
            self, 
            text="📦 Exporter ZIP", 
            command=cmd_export, 
            fg_color="#a55a1f", 
            hover_color="#874918"
        )
        self.btn_export.grid(row=0, column=1, padx=5, pady=5, sticky="ew")