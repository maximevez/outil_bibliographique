import json
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path

from src.core.file_manager import FileManager
from src.core.git_manager import GitManager
#from src.ui.fenetre_principale import ApplicationUI
from src.ui.controller import AppController

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
    # 1. On récupère le chemin dynamiquement (via config ou dialogue)
    biblio_path = obtenir_chemin_biblio()
    
    # 2. Initialisation du moteur
    file_mgr = FileManager(biblio_path)
    file_mgr.setup_directories()
    git_mgr = GitManager(biblio_path)
    
    # 3. Configuration du design moderne
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    # 4. Lancement de l'interface principale
    root = ctk.CTk()
    # On lance l'application via le Contrôleur
    app = AppController(root, file_mgr, git_mgr, biblio_path)
    
    root.mainloop()

if __name__ == "__main__":
    main()