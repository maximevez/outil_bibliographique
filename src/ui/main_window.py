import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from tkinterweb import HtmlFrame
from src.ui.components.action_header import ActionHeader
from src.ui.components.library_view import LibraryView
from src.ui.components.import_export import ImportExportPanel

class MainWindow:
    def __init__(self, root, ctrl):
        self.root = root
        self.ctrl = ctrl # Le "Chef d'orchestre" (Contrôleur)

        self.root.title("Outil Bibliographique")
        self.root.geometry("1100x700")
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)

        self._styliser_treeview()
        self._creer_panneau_gauche()
        self._creer_panneau_droit()

    def _styliser_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=30,
                        fieldbackground="#2b2b2b",
                        bordercolor="#343638",
                        borderwidth=0,
                        font=("Segoe UI", 11))
        style.map('Treeview', background=[('selected', '#1f538d')])

    def _creer_panneau_gauche(self):
        left_frame = ctk.CTkFrame(self.root, corner_radius=10)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        self.header = ActionHeader(
            master=left_frame,
            cmd_new_folder=self.ctrl.creer_dossier,
            cmd_add_pdf=self.ctrl.ajouter_article,
            cmd_rename=self.ctrl.renommer_element,
            cmd_move=self.ctrl.deplacer_element
        )
        self.header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.lib_view = LibraryView(
            master=left_frame,
            cmd_search=self.ctrl.lancer_recherche_via_ui,
            cmd_cancel=self.ctrl.annuler_recherche,
            on_select=self.ctrl.afficher_apercu,
            on_double_click=lambda e: self.ctrl.ouvrir_article()
        )
        self.lib_view.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        self.panel_import_export = ImportExportPanel(
            master=left_frame,
            cmd_import=self.ctrl.handle_import,
            cmd_export=self.ctrl.handle_export
        )
        self.panel_import_export.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    def _creer_panneau_droit(self):
        self.right_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        header_droit = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_droit.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        self.lbl_titre_apercu = ctk.CTkLabel(header_droit, text="Aucun article sélectionné", font=("Segoe UI", 16, "bold"))
        self.lbl_titre_apercu.pack(side=tk.LEFT)
        
        self.var_navigateur = tk.StringVar(value="Système (Défaut)")
        self.menu_nav = ctk.CTkOptionMenu(
            header_droit, variable=self.var_navigateur,
            values=["Système (Défaut)", "Firefox", "Edge", "Chrome"], width=140
        )
        self.menu_nav.pack(side=tk.RIGHT, padx=5)

        self.btn_ouvrir = ctk.CTkButton(header_droit, text="📖 Ouvrir", command=self.ctrl.ouvrir_article, state="disabled", width=100)
        self.btn_ouvrir.pack(side=tk.RIGHT, padx=5)

        self.btn_creer_note = ctk.CTkButton(
            header_droit, text="📝 Créer Note", command=self.ctrl.creer_note_manquante, 
            fg_color="#2fa572", hover_color="#25855a", width=100
        )

        self.html_frame = HtmlFrame(self.right_frame, messages_enabled=False)
        self.html_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

    # === MÉTHODES POUR PERMETTRE AU CONTRÔLEUR DE MODIFIER L'INTERFACE ===
    def set_titre_apercu(self, texte):
        self.lbl_titre_apercu.configure(text=texte)

    def set_etat_bouton_ouvrir(self, etat):
        self.btn_ouvrir.configure(state=etat)

    def afficher_bouton_note(self, afficher):
        if afficher:
            self.btn_creer_note.pack(side=tk.RIGHT, padx=5)
        else:
            self.btn_creer_note.pack_forget()

    def charger_html(self, html_content):
        self.html_frame.load_html(html_content)

    def get_navigateur(self):
        return self.var_navigateur.get()