import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from src.core.launcher import Launcher

class ApplicationUI:
    def __init__(self, root, file_mgr, git_mgr, biblio_path):
        self.root = root
        self.file_mgr = file_mgr
        self.git_mgr = git_mgr
        self.biblio_path = Path(biblio_path)
        
        self.root.title("Outil Bibliographique")
        self.root.geometry("800x600")
        
        self._creer_widgets()
        self.rafraichir_liste()
        
    def _creer_widgets(self):
        # --- En-tête ---
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill=tk.X)
        # --- Barre de recherche ---
        search_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="🔍 Mot-clé :").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Permet de lancer la recherche en appuyant sur "Entrée" sur le clavier
        search_entry.bind('<Return>', lambda e: self.lancer_recherche())
        
        ttk.Button(search_frame, text="Rechercher", command=self.lancer_recherche).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="❌ Annuler", command=self.annuler_recherche).pack(side=tk.LEFT, padx=2)

        ttk.Label(header_frame, text="Ma Bibliothèque", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Synchroniser (Git)", command=self.sync_git).pack(side=tk.RIGHT)
        
        # --- Zone centrale : Arborescence des articles ---
        list_frame = ttk.Frame(self.root, padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # On remplace la Listbox par un Treeview
        self.tree = ttk.Treeview(list_frame, columns=("chemin", "type"), show="tree", selectmode="browse")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        # Double-clic pour ouvrir un article
        self.tree.bind('<Double-1>', lambda e: self.ouvrir_article())
        
        # --- Pied de page : Actions ---
        # --- Pied de page : Actions ---
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(action_frame, text="📁 Nouveau Dossier", command=self.creer_dossier).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="➕ Ajouter article", command=self.ajouter_article).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="✏️ Renommer", command=self.renommer_element).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="➡️ Déplacer", command=self.deplacer_element).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="📖 Ouvrir", command=self.ouvrir_article).pack(side=tk.RIGHT, padx=2)

    def rafraichir_liste(self):
        """Recharge l'arborescence depuis le dossier articles."""
        # On vide l'arbre existant
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        articles_dir = self.biblio_path / "articles"
        if not articles_dir.exists():
            return
            
        self._peupler_arbre("", articles_dir)

    def _peupler_arbre(self, parent_id, chemin_dossier):
        """Fonction récursive pour lire les dossiers et sous-dossiers."""
        # On trie pour afficher les dossiers en premier, puis les fichiers par ordre alphabétique
        chemins = sorted(chemin_dossier.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        
        for element in chemins:
            if element.is_dir():
                dossier_id = self.tree.insert(parent_id, "end", text=f"📁 {element.name}", values=(str(element), "dossier"), open=True)
                self._peupler_arbre(dossier_id, element)
            elif element.is_file() and element.suffix.lower() == '.pdf':
                self.tree.insert(parent_id, "end", text=f"📄 {element.name}", values=(str(element), "fichier"))

    def _obtenir_dossier_selectionne(self):
        """Détermine dans quel dossier l'utilisateur veut agir selon sa sélection."""
        selection = self.tree.selection()
        # Si rien n'est sélectionné, on retourne la racine "articles"
        if not selection:
            return str(self.biblio_path / "articles")
            
        item = self.tree.item(selection[0])
        chemin = Path(item["values"][0])
        type_item = item["values"][1]
        
        # Si c'est un dossier, on cible ce dossier. Si c'est un fichier, on cible le dossier parent du fichier.
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
        chemin_pdf = filedialog.askopenfilename(
            title="Sélectionner un article PDF",
            filetypes=[("Fichiers PDF", "*.pdf")]
        )
        
        if chemin_pdf:
            dossier_cible = self._obtenir_dossier_selectionne()
            
            if self.file_mgr.add_article(chemin_pdf, target_dir=dossier_cible):
                nom_fichier = Path(chemin_pdf).name
                self.git_mgr.commit_all(f"Ajout de l'article {nom_fichier}")
                self.rafraichir_liste()
                messagebox.showinfo("Succès", f"L'article {nom_fichier} a été ajouté dans {Path(dossier_cible).name}.")

    def ouvrir_article(self):
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        chemin = Path(item["values"][0])
        type_item = item["values"][1]
        
        # On empêche l'ouverture si c'est un dossier qui est sélectionné
        if type_item == "dossier":
            return
            
        chemin_pdf = chemin
        chemin_md = chemin.parent / (chemin.stem + ".md")
        
        Launcher.open_article(str(chemin_pdf), str(chemin_md))

    def sync_git(self):
        self.git_mgr.commit_all("Synchronisation manuelle")
        messagebox.showinfo("Git", "Bibliothèque sauvegardée localement (Commit effectué).")

    def renommer_element(self):
        """Demande un nouveau nom et renomme l'élément sélectionné."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un élément à renommer.")
            return
            
        item = self.tree.item(selection[0])
        chemin = Path(item["values"][0])
        type_item = item["values"][1]
        
        # On propose le nom actuel par défaut (sans le .pdf pour faire plus propre)
        nom_actuel = chemin.name if type_item == "dossier" else chemin.stem
            
        nouveau_nom = simpledialog.askstring("Renommer", "Nouveau nom :", initialvalue=nom_actuel)
        
        # Si l'utilisateur a entré un nom et qu'il est différent de l'ancien
        if nouveau_nom and nouveau_nom != nom_actuel:
            if self.file_mgr.rename_item(str(chemin), nouveau_nom):
                self.git_mgr.commit_all(f"Renommage de {nom_actuel} en {nouveau_nom}")
                self.rafraichir_liste()

    def deplacer_element(self):
        """Ouvre un explorateur pour choisir le dossier de destination."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un élément à déplacer.")
            return
            
        item = self.tree.item(selection[0])
        chemin_source = Path(item["values"][0])
        
        # Ouvre une fenêtre pour choisir le dossier cible (elle s'ouvre dans la biblio par défaut)
        dossier_dest = filedialog.askdirectory(
            initialdir=self.biblio_path / "articles",
            title="Sélectionnez le dossier de destination"
        )
        
        if dossier_dest:
            # SÉCURITÉ 1 : S'assurer qu'on reste bien dans le dossier de la bibliothèque
            try:
                Path(dossier_dest).relative_to(self.biblio_path / "articles")
            except ValueError:
                messagebox.showerror("Erreur", "Vous devez sélectionner un dossier situé à l'intérieur de votre bibliothèque.")
                return
            
            # SÉCURITÉ 2 : Empêcher de déplacer un dossier à l'intérieur de lui-même
            if chemin_source.is_dir() and str(chemin_source) in dossier_dest:
                messagebox.showerror("Erreur", "Impossible de déplacer un dossier à l'intérieur de lui-même.")
                return
                
            # On déplace l'élément
            if self.file_mgr.move_item(str(chemin_source), dossier_dest):
                self.git_mgr.commit_all(f"Déplacement de {chemin_source.name}")
                self.rafraichir_liste()
    
    def lancer_recherche(self):
        mot_cle = self.search_var.get().strip()
        
        # Si la barre est vide, on recharge l'arborescence normale
        if not mot_cle:
            self.rafraichir_liste()
            return
            
        resultats_pdf = self.file_mgr.search_by_keyword(mot_cle)
        
        # On vide l'affichage actuel
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not resultats_pdf:
            self.tree.insert("", "end", text="Aucun article trouvé avec ce mot-clé.", values=("", "info"))
            return
            
        # On affiche les résultats sous forme de liste plate
        for pdf_path in resultats_pdf:
            # On récupère le nom du dossier parent pour savoir où l'article est rangé
            dossier_parent = pdf_path.parent.name
            texte_affichage = f"📄 {pdf_path.name}  (Dossier : {dossier_parent})"
            
            self.tree.insert("", "end", text=texte_affichage, values=(str(pdf_path), "fichier"))

    def annuler_recherche(self):
        """Vide la barre de recherche et remet l'arborescence des dossiers par défaut."""
        self.search_var.set("")
        self.rafraichir_liste()