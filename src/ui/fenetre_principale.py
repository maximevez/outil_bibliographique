import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import customtkinter as ctk
from pathlib import Path
from src.core.launcher import Launcher
import markdown
from tkinterweb import HtmlFrame

class ApplicationUI:
    def __init__(self, root, file_mgr, git_mgr, biblio_path):
        self.root = root
        self.file_mgr = file_mgr
        self.git_mgr = git_mgr
        self.biblio_path = Path(biblio_path)
        
        self.root.title("Outil Bibliographique")
        self.root.geometry("1100x700")
        
        # Grille principale
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)

        self._styliser_treeview()
        self._creer_panneau_gauche()
        self._creer_panneau_droit()
        
        self.rafraichir_liste()
        self.root.config(cursor="arrow")
        
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
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # En-tête
        header_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(header_frame, text="Ma Bibliothèque", font=("Segoe UI", 18, "bold")).pack(side=tk.LEFT)
        ctk.CTkButton(header_frame, text="Sync Git", width=80, command=self.sync_git).pack(side=tk.RIGHT)

        # Barre de recherche intégrée
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="Chercher un mot-clé...")
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        search_entry.bind('<Return>', lambda e: self.lancer_recherche())
        ctk.CTkButton(search_frame, text="🔍", width=40, command=self.lancer_recherche).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(search_frame, text="❌", width=40, fg_color="#a83232", hover_color="#8a2727", command=self.annuler_recherche).pack(side=tk.LEFT)

        # Arborescence
        tree_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        tree_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        self.tree = ttk.Treeview(tree_frame, columns=("chemin", "type"), show="tree", selectmode="browse")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        self.tree.bind('<<TreeviewSelect>>', self.afficher_apercu)
        self.tree.bind('<Double-1>', lambda e: self.ouvrir_article())

        # Boutons d'action
        action_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        action_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(action_frame, text="📁 Nouveau Dossier", command=self.creer_dossier).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(action_frame, text="➕ Ajouter PDF", command=self.ajouter_article).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(action_frame, text="✏️ Renommer", command=self.renommer_element).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(action_frame, text="➡️ Déplacer", command=self.deplacer_element).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)

    def _creer_panneau_droit(self):
        self.right_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        header_droit = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_droit.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        self.lbl_titre_apercu = ctk.CTkLabel(header_droit, text="Aucun article sélectionné", font=("Segoe UI", 16, "bold"))
        self.lbl_titre_apercu.pack(side=tk.LEFT)
        
        self.btn_ouvrir = ctk.CTkButton(header_droit, text="📖 Ouvrir l'article", command=self.ouvrir_article, state="disabled")
        self.btn_ouvrir.pack(side=tk.RIGHT)

        self.html_frame = HtmlFrame(self.right_frame, messages_enabled=False)
        self.html_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        
        self._maj_texte_apercu("Sélectionnez un article dans l'arborescence à gauche pour afficher vos notes.")
        
        self._maj_texte_apercu("Sélectionnez un article dans l'arborescence à gauche pour afficher vos notes.")

    # === LOGIQUE D'AFFICHAGE ET APERÇU ===
    def afficher_apercu(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        chemin = Path(item["values"][0])
        type_item = item["values"][1]
        
        if type_item == "dossier":
            self.lbl_titre_apercu.configure(text=f"📁 {chemin.name}")
            self._maj_texte_apercu("Ceci est un dossier.")
            self.btn_ouvrir.configure(state="disabled")
            return

        self.lbl_titre_apercu.configure(text=f"📄 {chemin.name}")
        self.btn_ouvrir.configure(state="normal")
        
        chemin_md = chemin.parent / (chemin.stem + ".md")
        if chemin_md.exists():
            try:
                with open(chemin_md, "r", encoding="utf-8") as f:
                    contenu = f.read()
                self._maj_texte_apercu(contenu)
            except Exception as e:
                self._maj_texte_apercu(f"Erreur de lecture : {e}")
        else:
            self._maj_texte_apercu("Aucun fichier de notes (.md) trouvé pour cet article.")

    def _maj_texte_apercu(self, texte_md):
        # 1. On convertit le Markdown en HTML (avec l'extension 'extra' pour supporter les tableaux)
        html_content = markdown.markdown(texte_md, extensions=['extra'])
        
        # 2. On crée un style CSS pour que le rendu reste en "Mode Sombre" et soit joli
        css_dark = """
        <style>
            body { 
                background-color: #2b2b2b; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                padding: 10px; 
                line-height: 1.6;
            }
            h1, h2, h3 { color: #5aa1e3; border-bottom: 1px solid #3a3a3a; padding-bottom: 5px; }
            code { 
                background-color: #1e1e1e; 
                padding: 2px 5px; 
                border-radius: 4px; 
                font-family: 'Consolas', monospace; 
                color: #ce9178;
            }
            pre { 
                background-color: #1e1e1e; 
                padding: 10px; 
                border-radius: 5px; 
                border: 1px solid #3a3a3a;
            }
            pre code { color: #d4d4d4; }
            blockquote { 
                border-left: 4px solid #5aa1e3; 
                margin-left: 0; 
                padding-left: 15px; 
                color: #a0a0a0; 
                font-style: italic;
            }
            ul, ol { margin-top: 5px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #3a3a3a; padding: 8px; text-align: left; }
            th { background-color: #1e1e1e; }
        </style>
        """
        
        # 3. On assemble le tout et on l'envoie au composant
        page_complete = f"<html><head>{css_dark}</head><body>{html_content}</body></html>"
        self.html_frame.load_html(page_complete)

    # === LOGIQUE DES DOSSIERS ET ACTIONS ===
    def rafraichir_liste(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        articles_dir = self.biblio_path / "articles"
        if not articles_dir.exists():
            return
        self._peupler_arbre("", articles_dir)

    def _peupler_arbre(self, parent_id, chemin_dossier):
        chemins = sorted(chemin_dossier.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        for element in chemins:
            if element.is_dir():
                dossier_id = self.tree.insert(parent_id, "end", text=f"📁 {element.name}", values=(str(element), "dossier"), open=True)
                self._peupler_arbre(dossier_id, element)
            elif element.is_file() and element.suffix.lower() == '.pdf':
                self.tree.insert(parent_id, "end", text=f"📄 {element.name}", values=(str(element), "fichier"))

    def _obtenir_dossier_selectionne(self):
        selection = self.tree.selection()
        if not selection:
            return str(self.biblio_path / "articles")
            
        item = self.tree.item(selection[0])
        chemin = Path(item["values"][0])
        type_item = item["values"][1]
        
        if type_item == "dossier":
            return str(chemin)
        else:
            return str(chemin.parent)

    def creer_dossier(self):
        nom_dossier = simpledialog.askstring("Nouveau dossier", "Nom du dossier :")
        if not nom_dossier:
            return
        dossier_cible = self._obtenir_dossier_selectionne()
        if self.file_mgr.create_folder(nom_dossier, target_dir=dossier_cible):
            self.rafraichir_liste()

    def ajouter_article(self):
        chemin_pdf = filedialog.askopenfilename(title="Sélectionner un article PDF", filetypes=[("Fichiers PDF", "*.pdf")])
        if chemin_pdf:
            dossier_cible = self._obtenir_dossier_selectionne()
            if self.file_mgr.add_article(chemin_pdf, target_dir=dossier_cible):
                nom_fichier = Path(chemin_pdf).name
                self.git_mgr.commit_all(f"Ajout de l'article {nom_fichier}")
                self.rafraichir_liste()
                messagebox.showinfo("Succès", f"L'article {nom_fichier} a été ajouté.")

    def renommer_element(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un élément à renommer.")
            return
        item = self.tree.item(selection[0])
        chemin = Path(item["values"][0])
        type_item = item["values"][1]
        
        nom_actuel = chemin.name if type_item == "dossier" else chemin.stem
        nouveau_nom = simpledialog.askstring("Renommer", "Nouveau nom :", initialvalue=nom_actuel)
        
        if nouveau_nom and nouveau_nom != nom_actuel:
            if self.file_mgr.rename_item(str(chemin), nouveau_nom):
                self.git_mgr.commit_all(f"Renommage de {nom_actuel} en {nouveau_nom}")
                self.rafraichir_liste()

    def deplacer_element(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un élément à déplacer.")
            return
        item = self.tree.item(selection[0])
        chemin_source = Path(item["values"][0])
        
        dossier_dest = filedialog.askdirectory(initialdir=self.biblio_path / "articles", title="Dossier de destination")
        if dossier_dest:
            try:
                Path(dossier_dest).relative_to(self.biblio_path / "articles")
            except ValueError:
                messagebox.showerror("Erreur", "Sélectionnez un dossier à l'intérieur de la bibliothèque.")
                return
            
            if chemin_source.is_dir() and str(chemin_source) in dossier_dest:
                messagebox.showerror("Erreur", "Impossible de déplacer un dossier dans lui-même.")
                return
                
            if self.file_mgr.move_item(str(chemin_source), dossier_dest):
                self.git_mgr.commit_all(f"Déplacement de {chemin_source.name}")
                self.rafraichir_liste()

    def ouvrir_article(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        chemin = Path(item["values"][0])
        if item["values"][1] == "dossier":
            return
            
        chemin_pdf = chemin
        chemin_md = chemin.parent / (chemin.stem + ".md")
        Launcher.open_article(str(chemin_pdf), str(chemin_md))

    def sync_git(self):
        self.git_mgr.commit_all("Synchronisation manuelle")
        messagebox.showinfo("Git", "Bibliothèque sauvegardée localement (Commit effectué).")

    # === RECHERCHE ===
    def lancer_recherche(self):
        mot_cle = self.search_var.get().strip()
        if not mot_cle:
            self.rafraichir_liste()
            return
            
        resultats_pdf = self.file_mgr.search_by_keyword(mot_cle)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not resultats_pdf:
            self.tree.insert("", "end", text="Aucun article trouvé avec ce mot-clé.", values=("", "info"))
            return
            
        for pdf_path in resultats_pdf:
            dossier_parent = pdf_path.parent.name
            self.tree.insert("", "end", text=f"📄 {pdf_path.name}  (Dossier : {dossier_parent})", values=(str(pdf_path), "fichier"))

    def annuler_recherche(self):
        self.search_var.set("")
        self.rafraichir_liste()