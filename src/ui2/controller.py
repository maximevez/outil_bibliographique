from PyQt6.QtWidgets import QMessageBox, QFileDialog, QInputDialog, QTreeWidgetItem
from pathlib import Path
import markdown
from src.core.launcher import Launcher
from src.core.archive_manager import ArchiveManager
from src.ui2.main_window import MainWindow
import shutil
import mdx_math  # Ajouté spécialement pour forcer PyInstaller à l'embarquer
import markdown.extensions.fenced_code
import markdown.extensions.nl2br
import markdown.extensions.extra
import markdown.extensions.tables

class AppController:
    def __init__(self, file_mgr, git_mgr, biblio_path):
        self.file_mgr = file_mgr
        self.git_mgr = git_mgr
        self.biblio_path = Path(biblio_path)
        self.archive_mgr = ArchiveManager(biblio_path)
        
        self.view = MainWindow(self)
        self.rafraichir_liste()
        self._maj_texte_apercu("Sélectionnez un article dans l'arborescence à gauche pour afficher vos notes.")

    def afficher_apercu(self):
        items = self.view.lib_view.tree.selectedItems()
        if not items: return
        item = items[0]
        chemin = Path(item.text(1)) # On lit la colonne cachée
        type_item = item.text(2)
        
        if type_item == "dossier":
            self.view.set_titre_apercu(f"📁 {chemin.name}")
            self._maj_texte_apercu("Ceci est un dossier.")
            self.view.set_etat_bouton_ouvrir(False)
            self.view.afficher_bouton_note(False)
            return

        self.view.set_titre_apercu(f"📄 {chemin.name}")
        self.view.set_etat_bouton_ouvrir(True)
        
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
            self._maj_texte_apercu("### ⚠️ Aucune note trouvée\n\nAucun fichier (`.md`) n'est associé à cet article.\n\nCliquez sur **Créer Note** pour en générer un.")
            self.view.afficher_bouton_note(True)

    def _maj_texte_apercu(self, texte_md):
        # 1. Ajout de 'mdx_math' pour empêcher le Markdown de casser le LaTeX
        html_content = markdown.markdown(texte_md, extensions=['extra', 'tables', 'mdx_math', 'fenced_code', 'nl2br'])
        
        # 2. Le CSS pour le mode sombre
        css_dark = """
        <style>
            body { background-color: #1e1e1e; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 14px; padding: 15px; }
            h1, h2, h3 { color: #5aa1e3; border-bottom: 1px solid #3a3a3a; padding-bottom: 5px; }
            code { background-color: #2b2b2b; padding: 2px 5px; border-radius: 4px; font-family: 'Consolas'; color: #ce9178; }
            pre { background-color: #2b2b2b; padding: 10px; border-radius: 5px; border: 1px solid #3a3a3a; }
            pre code { color: #d4d4d4; }
            blockquote { border-left: 4px solid #5aa1e3; padding-left: 15px; color: #a0a0a0; font-style: italic; }
            table { border-collapse: collapse; width: 100%; margin-top: 10px; }
            th, td { border: 1px solid #3a3a3a; padding: 8px; text-align: left; }
            th { background-color: #2b2b2b; }
        </style>
        """
        
        # 3. Le script MathJax (utilisation d'une chaîne brute 'r' pour gérer les antislashs)
        mathjax_script = r"""
        <script>
        MathJax = {
          tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [['$$', '$$'], ['\\[', '\\]']]
          }
        };
        </script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        """
        
        # 4. On assemble et on charge la page
        page_complete = f"<html><head>{css_dark}{mathjax_script}</head><body>{html_content}</body></html>"
        self.view.charger_html(page_complete)

    def rafraichir_liste(self):
        self.view.lib_view.tree.clear()
        articles_dir = self.biblio_path / "articles"
        if not articles_dir.exists(): return
        self._peupler_arbre(self.view.lib_view.tree.invisibleRootItem(), articles_dir)

    def _peupler_arbre(self, parent_item, chemin_dossier):
        chemins = sorted(chemin_dossier.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        for element in chemins:
            if element.is_dir():
                dossier_item = QTreeWidgetItem(parent_item, [f"📁 {element.name}", str(element), "dossier"])
                dossier_item.setExpanded(True)
                self._peupler_arbre(dossier_item, element)
            elif element.is_file() and element.suffix.lower() == '.pdf':
                QTreeWidgetItem(parent_item, [f"📄 {element.name}", str(element), "fichier"])

    def _obtenir_dossier_selectionne(self):
        items = self.view.lib_view.tree.selectedItems()
        if not items: return str(self.biblio_path / "articles")
        item = items[0]
        chemin = Path(item.text(1))
        return str(chemin) if item.text(2) == "dossier" else str(chemin.parent)

    def creer_dossier(self):
        nom_dossier, ok = QInputDialog.getText(self.view, "Nouveau dossier", "Nom du dossier :")
        if ok and nom_dossier and self.file_mgr.create_folder(nom_dossier, target_dir=self._obtenir_dossier_selectionne()):
            self.rafraichir_liste()

    def ajouter_article(self):
        # getOpenFileNames permet de sélectionner plusieurs fichiers (renvoie une liste)
        chemins_pdf, _ = QFileDialog.getOpenFileNames(self.view, "Sélectionner des articles PDF", "", "Fichiers PDF (*.pdf)")
        
        if chemins_pdf:
            dossier_cible = self._obtenir_dossier_selectionne()
            articles_ajoutes = 0
            
            for chemin in chemins_pdf:
                if self.file_mgr.add_article(chemin, target_dir=dossier_cible):
                    articles_ajoutes += 1
                    
            if articles_ajoutes > 0:
                self.git_mgr.commit_all(f"Ajout de {articles_ajoutes} article(s)")
                self.rafraichir_liste()
                QMessageBox.information(self.view, "Succès", f"{articles_ajoutes} article(s) ajouté(s) avec succès.")

    def renommer_element(self):
        items = self.view.lib_view.tree.selectedItems()
        if not items:
            QMessageBox.warning(self.view, "Attention", "Veuillez sélectionner un élément à renommer.")
            return
        item = items[0]
        chemin = Path(item.text(1))
        
        nom_actuel = chemin.name if item.text(2) == "dossier" else chemin.stem
        nouveau_nom, ok = QInputDialog.getText(self.view, "Renommer", "Nouveau nom :", text=nom_actuel)
        
        if ok and nouveau_nom and nouveau_nom != nom_actuel and self.file_mgr.rename_item(str(chemin), nouveau_nom):
            self.git_mgr.commit_all(f"Renommage de {nom_actuel} en {nouveau_nom}")
            self.rafraichir_liste()

    def deplacer_element(self):
        items = self.view.lib_view.tree.selectedItems()
        if not items:
            QMessageBox.warning(self.view, "Attention", "Veuillez sélectionner un élément à déplacer.")
            return
        item = items[0]
        chemin_source = Path(item.text(1))
        
        dossier_dest = QFileDialog.getExistingDirectory(self.view, "Dossier de destination", str(self.biblio_path / "articles"))
        if dossier_dest:
            try: Path(dossier_dest).relative_to(self.biblio_path / "articles")
            except ValueError:
                QMessageBox.critical(self.view, "Erreur", "Sélectionnez un dossier à l'intérieur de la bibliothèque.")
                return
            if chemin_source.is_dir() and str(chemin_source) in dossier_dest:
                QMessageBox.critical(self.view, "Erreur", "Impossible de déplacer un dossier dans lui-même.")
                return
            if self.file_mgr.move_item(str(chemin_source), dossier_dest):
                self.git_mgr.commit_all(f"Déplacement de {chemin_source.name}")
                self.rafraichir_liste()

    def ouvrir_article(self, item_ignored=None):
        items = self.view.lib_view.tree.selectedItems()
        if not items: return
        item = items[0]
        if item.text(2) == "dossier": return
            
        chemin_pdf = Path(item.text(1))
        chemin_md = chemin_pdf.parent / (chemin_pdf.stem + ".md")
        navigateur_choisi = self.view.get_navigateur()
        Launcher.open_article(str(chemin_pdf), str(chemin_md), navigateur_choisi)

    def creer_note_manquante(self):
        items = self.view.lib_view.tree.selectedItems()
        if not items: return
        item = items[0]
        chemin_pdf = Path(item.text(1))
        chemin_md = chemin_pdf.parent / (chemin_pdf.stem + ".md")
        
        chemin_template = Path(__file__).resolve().parent.parent / "templates" / "template_note.md"
        if chemin_template.exists():
            with open(chemin_template, "r", encoding="utf-8") as t:
                contenu_defaut = f"# {chemin_pdf.stem}\n\n" + t.read()
        else:
            contenu_defaut = f"# Notes sur {chemin_pdf.stem}\n\n## Méthodologie\n\n## Résultats\n"
        
        try:
            with open(chemin_md, "w", encoding="utf-8") as f:
                f.write(contenu_defaut)
            self.git_mgr.commit_all(f"Création note manquante pour {chemin_pdf.name}")
            self.afficher_apercu()
        except Exception as e: QMessageBox.critical(self.view, "Erreur", f"Impossible de créer la note : {e}")

    def lancer_recherche_via_ui(self, mot_cle):
        if not mot_cle.strip():
            self.rafraichir_liste()
            return
        resultats_pdf = self.file_mgr.search_by_keyword(mot_cle)
        tree = self.view.lib_view.tree
        tree.clear()
        if not resultats_pdf:
            QTreeWidgetItem(tree.invisibleRootItem(), ["Aucun article trouvé.", "", "info"])
            return
        for pdf_path in resultats_pdf:
            QTreeWidgetItem(tree.invisibleRootItem(), [f"📄 {pdf_path.name}  (Dossier : {pdf_path.parent.name})", str(pdf_path), "fichier"])

    def annuler_recherche(self):
        self.view.lib_view.clear_search()
        self.rafraichir_liste()

    def handle_export(self):
        chemin_zip, _ = QFileDialog.getSaveFileName(self.view, "Exporter", "Export.zip", "Fichiers ZIP (*.zip)")
        if chemin_zip:
            try:
                self.archive_mgr.exporter_zip(chemin_zip)
                QMessageBox.information(self.view, "Succès", "Bibliothèque exportée !")
            except Exception as e: QMessageBox.critical(self.view, "Erreur", str(e))

    def handle_import(self):
        chemin_zip, _ = QFileDialog.getOpenFileName(self.view, "Importer ZIP", "", "Fichiers ZIP (*.zip)")
        if not chemin_zip: return
        nom_dossier, ok = QInputDialog.getText(self.view, "Importation", "Nom du dossier :")
        if ok and nom_dossier:
            try:
                nom_nettoye = self.archive_mgr.importer_zip(chemin_zip, nom_dossier)
                self.rafraichir_liste()
                QMessageBox.information(self.view, "Succès", f"Importé dans '{nom_nettoye}'.")
            except Exception as e: QMessageBox.critical(self.view, "Erreur", str(e))
    
    def supprimer_element(self):
        items = self.view.lib_view.tree.selectedItems()
        if not items:
            QMessageBox.warning(self.view, "Attention", "Veuillez sélectionner un élément à supprimer.")
            return
            
        item = items[0]
        chemin = Path(item.text(1))
        type_item = item.text(2)

        # 1. Fenêtre de confirmation (sécurité indispensable)
        reponse = QMessageBox.question(
            self.view, 
            "Confirmation de suppression", 
            f"Voulez-vous vraiment supprimer '{chemin.name}' ?\nCette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reponse == QMessageBox.StandardButton.Yes:
            try:
                # 2A. Cas d'un dossier : on supprime tout son contenu
                if type_item == "dossier":
                    shutil.rmtree(chemin)
                
                # 2B. Cas d'un fichier : on supprime le PDF ET le fichier .md associé
                else:
                    chemin.unlink() # Supprime le PDF
                    chemin_md = chemin.parent / (chemin.stem + ".md")
                    if chemin_md.exists():
                        chemin_md.unlink() # Supprime la note
                
                # 3. On sauvegarde et on rafraîchit
                self.git_mgr.commit_all(f"Suppression de {chemin.name}")
                self.rafraichir_liste()
                
                # 4. On vide le panneau droit pour ne pas afficher le fichier supprimé
                self.view.set_titre_apercu("Aucun article sélectionné")
                self.view.charger_html("") 
                self.view.afficher_bouton_note(False)
                self.view.set_etat_bouton_ouvrir(False)
                
            except Exception as e:
                QMessageBox.critical(self.view, "Erreur", f"Impossible de supprimer l'élément : {e}")