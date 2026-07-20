import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import customtkinter as ctk
from pathlib import Path
from src.core.launcher import Launcher
import markdown
from tkinterweb import HtmlFrame
import os
import zipfile
from zipfile import ZipInfo
from src.core.archive_manager import ArchiveManager
from poubelle.ui.components.import_export import ImportExportPanel
from poubelle.ui.components.action_header import ActionHeader
from poubelle.ui.components.library_view import LibraryView

class ApplicationUI:
    def __init__(self, root, file_mgr, git_mgr, biblio_path):
        self.root = root
        self.file_mgr = file_mgr
        self.git_mgr = git_mgr
        self.biblio_path = Path(biblio_path)
        self.archive_mgr = ArchiveManager(biblio_path)
        
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

        # En-tête avec titre et boutons d'action
        # === EN-TÊTE D'ACTION (Titre + Icônes via composant externe) ===
        self.header = ActionHeader(
            master=left_frame,
            cmd_new_folder=self.creer_dossier,
            cmd_add_pdf=self.ajouter_article,
            cmd_rename=self.renommer_element,
            cmd_move=self.deplacer_element
        )
        self.header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # === ARBORESCENCE & RECHERCHE (via composant externe) ===
        self.lib_view = LibraryView(
            master=left_frame,
            cmd_search=self.lancer_recherche_via_ui,
            cmd_cancel=self.annuler_recherche,
            on_select=self.afficher_apercu,
            on_double_click=lambda e: self.ouvrir_article()
        )
        self.lib_view.grid(row=1, column=0, rowspan=2, padx=0, pady=0, sticky="nsew")
        
        # On redirige les références internes pour ne pas casser le reste du code
        self.tree = self.lib_view.tree

        # Boutons d'action
        # === NOUVEAU PANNEAU D'ACTION (Uniquement Import/Export) ===
        # === PANNEAU D'ACTION (Import/Export via composant externe) ===
        self.panel_import_export = ImportExportPanel(
            master=left_frame,
            cmd_import=self.handle_import,
            cmd_export=self.handle_export
        )
        self.panel_import_export.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    def _creer_panneau_droit(self):
        self.right_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        header_droit = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_droit.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        self.lbl_titre_apercu = ctk.CTkLabel(header_droit, text="Aucun article sélectionné", font=("Segoe UI", 16, "bold"))
        self.lbl_titre_apercu.pack(side=tk.LEFT)
        
        # --- NOUVEAUTÉS ICI ---
        # 1. Sélecteur de navigateur
        self.var_navigateur = tk.StringVar(value="Système (Défaut)")
        self.menu_nav = ctk.CTkOptionMenu(
            header_droit, 
            variable=self.var_navigateur,
            values=["Système (Défaut)", "Firefox", "Edge", "Chrome"],
            width=140
        )
        self.menu_nav.pack(side=tk.RIGHT, padx=5)

        # 2. Bouton Ouvrir (réduit)
        self.btn_ouvrir = ctk.CTkButton(header_droit, text="📖 Ouvrir", command=self.ouvrir_article, state="disabled", width=100)
        self.btn_ouvrir.pack(side=tk.RIGHT, padx=5)

        # 3. Bouton Créer Note (Caché par défaut)
        self.btn_creer_note = ctk.CTkButton(
            header_droit, 
            text="📝 Créer Note", 
            command=self.creer_note_manquante, 
            fg_color="#2fa572", 
            hover_color="#25855a", 
            width=100
        )
        # On ne fait pas pack() ici pour qu'il reste invisible au lancement
        # ----------------------

        self.html_frame = HtmlFrame(self.right_frame, messages_enabled=False)
        self.html_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        
        self._maj_texte_apercu("Sélectionnez un article dans l'arborescence à gauche pour afficher vos notes.")

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
    def lancer_recherche_via_ui(self, mot_cle):
        if not mot_cle.strip():
            self.rafraichir_liste()
            return
            
        resultats_pdf = self.file_mgr.search_by_keyword(mot_cle)
        # ... (le reste de ton code de recherche)
        # Note : utilise self.lib_view.tree au lieu de self.tree ici

    def annuler_recherche(self):
        self.lib_view.clear_search()
        self.rafraichir_liste()
    
    # === IMPORT / EXPORT ===
    # === CONTROLEURS IMPORT / EXPORT ===
    def handle_export(self):
        chemin_zip = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("Fichiers ZIP", "*.zip")],
            title="Exporter ma bibliothèque",
            initialfile="Ma_Bibliotheque_Export.zip"
        )
        if not chemin_zip:
            return

        try:
            # On demande au Core de faire le travail
            self.archive_mgr.exporter_zip(chemin_zip)
            messagebox.showinfo("Succès", "Votre bibliothèque a été exportée avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exportation : {e}")

    def handle_import(self):
        chemin_zip = filedialog.askopenfilename(
            title="Sélectionner une bibliothèque partagée (ZIP)",
            filetypes=[("Fichiers ZIP", "*.zip")]
        )
        if not chemin_zip:
            return

        nom_dossier = simpledialog.askstring("Importation", "Nom du dossier pour cette bibliothèque :\n(ex: Biblio de Sophie)")
        if not nom_dossier:
            return

        try:
            # On envoie le chemin et le nom au Core
            nom_nettoye = self.archive_mgr.importer_zip(chemin_zip, nom_dossier)
            
            # Si aucune erreur n'a été levée (raise) par le Core, on met à jour l'UI
            self.rafraichir_liste()
            messagebox.showinfo("Succès", f"La bibliothèque a été importée avec succès dans '{nom_nettoye}'.")
            
        except FileExistsError as e:
            messagebox.showerror("Erreur", str(e))
        except ValueError as e:
            messagebox.showwarning("Attention", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'importation : {e}")

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
            self.btn_creer_note.pack_forget() # Cache le bouton note
            return

        self.lbl_titre_apercu.configure(text=f"📄 {chemin.name}")
        self.btn_ouvrir.configure(state="normal")
        
        chemin_md = chemin.parent / (chemin.stem + ".md")
        if chemin_md.exists():
            self.btn_creer_note.pack_forget() # La note existe, on cache le bouton
            try:
                with open(chemin_md, "r", encoding="utf-8") as f:
                    contenu = f.read()
                self._maj_texte_apercu(contenu)
            except Exception as e:
                self._maj_texte_apercu(f"Erreur de lecture : {e}")
        else:
            self._maj_texte_apercu("### ⚠️ Aucune note trouvée\n\nAucun fichier de notes (`.md`) n'est associé à cet article.\n\nCliquez sur le bouton **Créer Note** en haut à droite pour en générer un automatiquement.")
            self.btn_creer_note.pack(side=tk.RIGHT, padx=5) # On affiche le bouton !
    
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
        navigateur_choisi = self.var_navigateur.get() # On récupère le choix !
        
        Launcher.open_article(str(chemin_pdf), str(chemin_md), navigateur_choisi)

    def creer_note_manquante(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        chemin_pdf = Path(item["values"][0])
        chemin_md = chemin_pdf.parent / (chemin_pdf.stem + ".md")
        
        # Ton template de base
        contenu_defaut = f"# Notes sur {chemin_pdf.stem}\n\n## Méthodologie\n\n## Résultats\n\n## Remarques\n"
        
        try:
            with open(chemin_md, "w", encoding="utf-8") as f:
                f.write(contenu_defaut)
                
            # On commit si Git est activé
            self.git_mgr.commit_all(f"Création de la note manquante pour {chemin_pdf.name}")
            
            # On rafraîchit l'aperçu pour afficher la note fraîchement créée
            self.afficher_apercu()
            messagebox.showinfo("Succès", "La note a été créée avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de créer la note : {e}")