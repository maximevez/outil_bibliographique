import os
import subprocess
import sys
from pathlib import Path

class Launcher:
    @staticmethod
    def open_article(pdf_path: str, md_path: str):
        """Ouvre le PDF avec le lecteur par défaut et le MD avec l'éditeur par défaut/IDE."""
        
        # Ouvre le PDF (généralement dans Edge/Mozilla selon la configuration de l'OS)
        Launcher._open_file_default(pdf_path)
        
        # Ouvre le Markdown. 
        # Astuce : Si tu veux forcer VS Code, tu peux remplacer la ligne du dessous par :
        # subprocess.Popen(["code", md_path], shell=True)
        Launcher._open_file_default(md_path)

    @staticmethod
    def _open_file_default(filepath: str):
        """Utilise la commande native de l'OS pour ouvrir un fichier."""
        path = Path(filepath)
        if not path.exists():
            print(f"Fichier introuvable : {filepath}")
            return

        # Détection de l'OS pour utiliser la commande appropriée
        if sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin": # macOS
            subprocess.call(["open", filepath])
        else: # Linux
            subprocess.call(["xdg-open", filepath])