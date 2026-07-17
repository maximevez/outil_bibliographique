import json
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path

from src.core.file_manager import FileManager
from src.core.git_manager import GitManager

import sys
from PyQt6.QtWidgets import QApplication
from src.ui2.controller import AppController

# Le fichier de configuration sera créé à côté de l'exécutable/script
FICHIER_CONFIG = Path("config.json")

def obtenir_chemin_biblio() -> Path:
    """Lit le fichier config, ou demande à l'utilisateur au premier lancement."""
    
    # Cas 1 : L'utilisateur a déjà configuré son dossier
    if FICHIER_CONFIG.exists():
        try:
            with open(FICHIER_CONFIG, "r", encoding="utf-8") as f:
                config = json.load(f)
                chemin = Path(config["biblio_path"])
                # Sécurité : on s'assure que le dossier n'a pas été supprimé ou déplacé
                if chemin.exists() or chemin.parent.exists():
                    return chemin
        except Exception as e:
            print(f"Erreur de lecture du config.json : {e}")
            # Si le fichier est corrompu, on l'ignore et on redemande le chemin
            
    # Cas 2 : Premier lancement (ou dossier introuvable)
    root = tk.Tk()
    root.withdraw() # Cache la petite fenêtre grise de base de Tkinter
    
    messagebox.showinfo(
        "Bienvenue !", 
        "C'est votre première utilisation (ou votre dossier a été déplacé).\n\n"
        "Veuillez choisir l'emplacement où sera créé le dossier de votre Bibliothèque."
    )
    
    # Ouvre l'explorateur pour choisir un dossier
    dossier_choisi = filedialog.askdirectory(title="Choisissez l'emplacement de la bibliothèque")
    
    if not dossier_choisi:
        messagebox.showerror("Erreur fatale", "L'application a besoin d'un dossier pour fonctionner. Fermeture.")
        sys.exit() # On coupe le programme proprement si l'utilisateur annule
        
    # On ajoute le nom de notre dossier au chemin choisi
    chemin_complet = Path(dossier_choisi) / "Ma_Bibliotheque"
    
    # On sauvegarde ce choix pour les prochains lancements
    with open(FICHIER_CONFIG, "w", encoding="utf-8") as f:
        json.dump({"biblio_path": str(chemin_complet)}, f, indent=4)
        
    root.destroy() # On détruit la fenêtre invisible
    return chemin_complet

def main():
    biblio_path = obtenir_chemin_biblio()
    if not biblio_path:
        print("Installation annulée.")
        return
        
    git_mgr = GitManager(biblio_path)
    file_mgr = FileManager(biblio_path)

    # Lancement du moteur PyQt6
    app = QApplication(sys.argv)
    
    # Injection d'un CSS global pour obtenir le style "CustomTkinter / Mode Sombre"
    app.setStyle("Fusion")
    dark_stylesheet = """
    QWidget { background-color: #2b2b2b; color: #e0e0e0; font-family: 'Segoe UI'; font-size: 11pt; }
    QTreeWidget { background-color: #1e1e1e; border: 1px solid #343638; border-radius: 5px; outline: none; }
    QTreeWidget::item { padding: 4px; }
    QTreeWidget::item:selected { background-color: #1f538d; color: white; }
    QPushButton { background-color: #343638; border: 1px solid #444648; border-radius: 5px; padding: 6px 12px; }
    QPushButton:hover { background-color: #444648; }
    QPushButton:disabled { background-color: #222222; color: #555555; border: none; }
    QLineEdit { background-color: #1e1e1e; border: 1px solid #343638; border-radius: 5px; padding: 6px; }
    QTextBrowser { background-color: #1e1e1e; border: 1px solid #343638; border-radius: 5px; }
    QComboBox { background-color: #343638; border: 1px solid #444648; border-radius: 5px; padding: 5px; }
    QSplitter::handle { background-color: #343638; width: 4px; }
    QMessageBox { background-color: #2b2b2b; }
    """
    app.setStyleSheet(dark_stylesheet)
    
    # On remarque que l'on ne passe plus "root" au controller !
    controller = AppController(file_mgr, git_mgr, biblio_path)
    controller.view.show()
    
    # Boucle principale d'application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()