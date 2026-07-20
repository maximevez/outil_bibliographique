import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
import markdown
from src.core.launcher import Launcher
from src.core.archive_manager import ArchiveManager
from src.ui.main_window import MainWindow

class AppController:
    def __init__(self, root, file_mgr, git_mgr, biblio_path):
        self.file_mgr = file_mgr
        self.git_mgr = git_mgr
        self.biblio_path = Path(biblio_path)
        self.archive_mgr = ArchiveManager(biblio_path)
        
        # Le Contrôleur crée la Vue et s'injecte lui-même à l'intérieur (self)
        self.view = MainWindow(root, self)
        
        self.rafraichir_liste()
        self._maj_texte_apercu("Sélectionnez un article dans l'arborescence à gauche pour afficher vos notes.")
        root.config(cursor="arrow")

    # === LOGIQUE D'AFFICHAGE ET APERÇU ===
    def afficher_apercu(self, event=None):
        tree = self.view.lib_view.tree
        selection = tree.selection()
        if not selection: return
            
        item = tree.item(selection[0])
        chemin = Path(item["values"][0])
        type_item = item["values"][1]
        
        if type_item == "dossier":
            self.view.set_titre_apercu(f"📁 {chemin.name}")
            self._maj_texte_apercu("Ceci est un dossier.")
            self.view.set_etat_bouton_ouvrir("disabled")
            self.view.afficher_bouton_note(False)
            return

        self.view.set_titre_apercu(f"📄 {chemin.name}")
        self.view.set_etat_bouton_ouvrir("normal")
        
        chemin_md = chemin.parent / (chemin.stem + ".md")
        if chemin_md.exists():
            self.view.afficher_bouton_note(False)
            try:
                with open(chemin_md, "r", encoding="utf-8") as f:
                    contenu = f.read()
                self._maj_texte_apercu(contenu)
            except Exception as e:
                self._maj_texte_apercu(f"Erreur de lecture : {e}")
        else:
            self._maj_texte_apercu("### ⚠️ Aucune note trouvée\n\nAucun fichier de notes (`.md`) n'est associé à cet article.\n\nCliquez sur le bouton **Créer Note** en haut à droite pour en générer un automatiquement.")
            self.view.afficher_bouton_note(True)

    def _maj_texte_apercu(self, texte_md):
        html_content = markdown.markdown(texte_md, extensions=['extra'])
        css_dark = """
        <style>
            body { background-color: #2b2b2b; color: #e0e0e0; font-family: 'Segoe UI', Arial, sans-serif; padding: 10px; line-height: 1.6; }
            h1, h2, h3 { color: #5aa1e3; border-bottom: 1px solid #3a3a3a; padding-bottom: 5px; }
            code { background-color: #1e1e1e; padding: 2px 5px; border-radius: 4px; font-family: 'Consolas', monospace; color: #ce9178; }
            pre { background-color: #1e1e1e; padding: 10px; border-radius: 5px; border: 1px solid #3a3a3a; }
            pre code { color: #d4d4d4; }
            blockquote { border-left: 4px solid #5aa1e3; margin-left: 0; padding-left: 15px; color: #a0a0a0; font-style: italic; }
            ul, ol { margin-top: 5px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #3a3a3a; padding: 8px; text-align: left; }
            th { background-color: #1e1e1e; }
        </style>
        """
        page_complete = f"<html><head>{css_dark}</head><body>{html_content}</body></html>"
        self.view.charger_html(page_complete)

    # === LOGIQUE DES DOSSIERS ET ACTIONS ===
    def rafraichir_liste(self):
        tree = self.view.lib_view.tree
        for item in tree.get_children():
            tree.delete(item)
            
        articles_dir = self.biblio_path / "articles"
        if not articles_dir.exists(): return
        self._peupler_arbre("", articles_dir)

    def _peupler_arbre(self, parent_id, chemin_dossier):
        tree = self.view.lib_view.tree
        chemins = sorted(chemin_dossier.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        for element in chemins:
            if element.is_dir():
                dossier_id = tree.insert(parent_id, "end", text=f"📁 {element.name}", values=(str(element), "dossier"), open=True)
                self._peupler_arbre(dossier_id, element)
            elif element.is_file() and element.suffix.lower() == '.pdf':
                tree.insert(parent_id, "end", text=f"📄 {element.name}", values=(str(element), "fichier"))

    def _obtenir_dossier_selectionne(self):
        tree = self.view.lib_view.tree
        selection = tree.selection()
        if not selection:
            return str(self.biblio_path / "articles")
            
        item = tree.item(selection[0])
        chemin = Path(item["values"][0])
        return str(chemin) if item["values"][1] == "dossier" else str(chemin.parent)

    def creer_dossier(self):
        nom_dossier = simpledialog.askstring("Nouveau dossier", "Nom du dossier :")
        if nom_dossier and self.file_mgr.create_folder(nom_dossier, target_dir=self._obtenir_dossier_selectionne()):
            self.rafraichir_liste()

    def ajouter_article(self):
        chemin_pdf = filedialog.askopenfilename(title="Sélectionner un article PDF", filetypes=[("Fichiers PDF", "*.pdf")])
        if chemin_pdf and self.file_mgr.add_article(chemin_pdf, target_dir=self._obtenir_dossier_selectionne()):
            nom_fichier = Path(chemin_pdf).name
            self.git_mgr.commit_all(f"Ajout de l'article {nom_fichier}")
            self.rafraichir_liste()
            messagebox.showinfo("Succès", f"L'article {nom_fichier} a été ajouté.")

    def renommer_element(self):
        tree = self.view.lib_view.tree
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un élément à renommer.")
            return
        item = tree.item(selection[0])
        chemin = Path(item["values"][0])
        
        nom_actuel = chemin.name if item["values"][1] == "dossier" else chemin.stem
        nouveau_nom = simpledialog.askstring("Renommer", "Nouveau nom :", initialvalue=nom_actuel)
        
        if nouveau_nom and nouveau_nom != nom_actuel and self.file_mgr.rename_item(str(chemin), nouveau_nom):
            self.git_mgr.commit_all(f"Renommage de {nom_actuel} en {nouveau_nom}")
            self.rafraichir_liste()

    def deplacer_element(self):
        tree = self.view.lib_view.tree
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un élément à déplacer.")
            return
        item = tree.item(selection[0])
        chemin_source = Path(item["values"][0])
        
        dossier_dest = filedialog.askdirectory(initialdir=self.biblio_path / "articles", title="Dossier de destination")
        if dossier_dest:
            try: Path(dossier_dest).relative_to(self.biblio_path / "articles")
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
        tree = self.view.lib_view.tree
        selection = tree.selection()
        if not selection: return
        item = tree.item(selection[0])
        if item["values"][1] == "dossier": return
            
        chemin_pdf = Path(item["values"][0])
        chemin_md = chemin_pdf.parent / (chemin_pdf.stem + ".md")
        navigateur_choisi = self.view.get_navigateur()
        
        Launcher.open_article(str(chemin_pdf), str(chemin_md), navigateur_choisi)

    def creer_note_manquante(self):
        tree = self.view.lib_view.tree
        selection = tree.selection()
        if not selection: return
        item = tree.item(selection[0])
        chemin_pdf = Path(item["values"][0])
        chemin_md = chemin_pdf.parent / (chemin_pdf.stem + ".md")
        
        # 1. On calcule le chemin vers le dossier src/templates/template_note.md
        # Path(__file__) est controller.py. parent.parent remonte à 'src/'
        chemin_template = Path(__file__).resolve().parent.parent/ "templates" / "template_note.md"
        
        # 2. On lit le fichier template s'il existe
        if chemin_template.exists():
            with open(chemin_template, "r", encoding="utf-8") as t:
                contenu_template = t.read()
            # On ajoute le nom de l'article tout en haut du template
            contenu_defaut = f"# {chemin_pdf.stem}\n\n" + contenu_template
        else:
            # Plan B (sécurité) si le fichier template a été supprimé ou déplacé
            contenu_defaut = f"# Notes sur {chemin_pdf.stem}\n\n## Méthodologie\n\n## Résultats\n\n## Remarques\n"
        
        try:
            with open(chemin_md, "w", encoding="utf-8") as f:
                f.write(contenu_defaut)
            self.git_mgr.commit_all(f"Création de la note manquante pour {chemin_pdf.name}")
            self.afficher_apercu()
            messagebox.showinfo("Succès", "La note a été créée avec succès à partir du modèle !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de créer la note : {e}")

    # === RECHERCHE ET ARCHIVES (Identique à avant) ===
    def lancer_recherche_via_ui(self, mot_cle):
        if not mot_cle.strip():
            self.rafraichir_liste()
            return
            
        resultats_pdf = self.file_mgr.search_by_keyword(mot_cle)
        tree = self.view.lib_view.tree
        
        for item in tree.get_children(): tree.delete(item)
            
        if not resultats_pdf:
            tree.insert("", "end", text="Aucun article trouvé.", values=("", "info"))
            return
            
        for pdf_path in resultats_pdf:
            dossier_parent = pdf_path.parent.name
            tree.insert("", "end", text=f"📄 {pdf_path.name}  (Dossier : {dossier_parent})", values=(str(pdf_path), "fichier"))

    def annuler_recherche(self):
        self.view.lib_view.clear_search()
        self.rafraichir_liste()

    def handle_export(self):
        chemin_zip = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Fichiers ZIP", "*.zip")], title="Exporter", initialfile="Export.zip")
        if chemin_zip:
            try:
                self.archive_mgr.exporter_zip(chemin_zip)
                messagebox.showinfo("Succès", "Bibliothèque exportée !")
            except Exception as e: messagebox.showerror("Erreur", str(e))

    def handle_import(self):
        chemin_zip = filedialog.askopenfilename(title="Importer ZIP", filetypes=[("Fichiers ZIP", "*.zip")])
        if not chemin_zip: return
        nom_dossier = simpledialog.askstring("Importation", "Nom du dossier :")
        if nom_dossier:
            try:
                nom_nettoye = self.archive_mgr.importer_zip(chemin_zip, nom_dossier)
                self.rafraichir_liste()
                messagebox.showinfo("Succès", f"Importé dans '{nom_nettoye}'.")
            except Exception as e: messagebox.showerror("Erreur", str(e))