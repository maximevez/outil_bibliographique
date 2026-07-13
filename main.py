import tkinter as tk
from pathlib import Path
from src.core.file_manager import FileManager
from src.core.git_manager import GitManager
from src.ui.fenetre_principale import ApplicationUI

def main():
    # 1. On définit le chemin de la bibliothèque
    biblio_path = Path.home() / "Documents" / "Ma_Bibliotheque"
    
    # 2. Initialisation du moteur
    file_mgr = FileManager(biblio_path)
    file_mgr.setup_directories()
    git_mgr = GitManager(biblio_path)
    
    # 3. Création et lancement de l'interface graphique
    root = tk.Tk()
    
    # Application d'un thème natif un peu plus moderne (facultatif mais recommandé)
    style = tk.ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
        
    app = ApplicationUI(root, file_mgr, git_mgr, biblio_path)
    
    # Démarre la boucle de l'application (maintient la fenêtre ouverte)
    root.mainloop()

if __name__ == "__main__":
    main()