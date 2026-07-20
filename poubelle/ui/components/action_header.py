import customtkinter as ctk
from CTkToolTip import CTkToolTip

class ActionHeader(ctk.CTkFrame):
    def __init__(self, master, cmd_new_folder, cmd_add_pdf, cmd_rename, cmd_move, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Le titre
        titre = ctk.CTkLabel(self, text="Ma Bibliothèque", font=("Arial", 20, "bold"))
        titre.pack(side="left", padx=(0, 10))
        
        # Les boutons icônes
        btn_add_dir = ctk.CTkButton(self, text="📁", width=30, command=cmd_new_folder)
        btn_add_dir.pack(side="left", padx=2)
        
        btn_add_pdf = ctk.CTkButton(self, text="➕", width=30, command=cmd_add_pdf)
        btn_add_pdf.pack(side="left", padx=2)
        
        btn_rename = ctk.CTkButton(self, text="✏️", width=30, command=cmd_rename)
        btn_rename.pack(side="left", padx=2)
        
        btn_move = ctk.CTkButton(self, text="➡️", width=30, command=cmd_move)
        btn_move.pack(side="left", padx=2)
        
        # Les infobulles
        CTkToolTip(btn_add_dir, message="Nouveau dossier")
        CTkToolTip(btn_add_pdf, message="Ajouter un article PDF")
        CTkToolTip(btn_rename, message="Renommer l'élément")
        CTkToolTip(btn_move, message="Déplacer l'élément")