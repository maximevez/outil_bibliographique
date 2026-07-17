import subprocess
import os
import platform

class Launcher:
    @staticmethod
    def open_article(chemin_pdf, chemin_md, navigateur="Système (Défaut)"):
        # 1. Ouvrir la note Markdown (dans VS Code par exemple)
        if os.path.exists(chemin_md):
            try:
                if platform.system() == 'Windows':
                    # On ajoute des guillemets autour du chemin pour protéger les espaces
                    subprocess.Popen(f'code "{chemin_md}"', shell=True)
                else:
                    subprocess.Popen(['code', chemin_md])
            except Exception:
                pass # Si VS Code n'est pas installé, on ignore silencieusement

        # 2. Ouvrir le PDF selon le navigateur choisi
        if platform.system() == 'Windows':
            try:
                if navigateur == "Firefox":
                    subprocess.Popen(f'start "" firefox "{chemin_pdf}"', shell=True)
                elif navigateur == "Edge":
                    subprocess.Popen(f'start "" msedge "{chemin_pdf}"', shell=True)
                elif navigateur == "Chrome":
                    subprocess.Popen(f'start "" chrome "{chemin_pdf}"', shell=True)
                else:
                    # Le choix "Système (Défaut)" ouvre avec l'outil par défaut
                    os.startfile(chemin_pdf) 
            except Exception:
                # Fallback de sécurité
                os.startfile(chemin_pdf)