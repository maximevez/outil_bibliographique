import os
import zipfile
import time
from pathlib import Path
from zipfile import ZipInfo

class ArchiveManager:
    def __init__(self, biblio_path):
        self.biblio_path = Path(biblio_path)

    def exporter_zip(self, chemin_zip):
        """Exporte la bibliothèque locale en ignorant les dossiers importés."""
        articles_dir = self.biblio_path / "articles"
        
        with zipfile.ZipFile(chemin_zip, 'w') as zipf:
            for root, dirs, files in os.walk(articles_dir):
                if ".ignore_export" in files:
                    dirs[:] = []  # Ignore ce dossier
                    continue
                    
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(articles_dir)
                    
                    # 1. On force les slashs (Standard ZIP)
                    nom_zip = arcname.as_posix()
                    
                    # 2. On crée la carte d'identité (évite le bug de 1980)
                    info = ZipInfo(nom_zip, date_time=time.localtime()[:6])
                    info.compress_type = zipfile.ZIP_DEFLATED
                    
                    # 3. Écriture
                    contenu = file_path.read_bytes()
                    zipf.writestr(info, contenu)

    def importer_zip(self, chemin_zip, nom_dossier):
        """Importe une archive et ajoute le marqueur de protection."""
        # Nettoyage du nom
        nom_dossier_clean = "".join([c for c in nom_dossier if c.isalpha() or c.isdigit() or c in ' -_']).strip()
        if not nom_dossier_clean:
            raise ValueError("Le nom du dossier est invalide ou vide.")
            
        dossier_import = self.biblio_path / "articles" / nom_dossier_clean
        
        if dossier_import.exists():
            raise FileExistsError(f"Le dossier '{nom_dossier_clean}' existe déjà.")
            
        dossier_import.mkdir(parents=True)
        
        # Extraction (Mode 'r' pour Read)
        with zipfile.ZipFile(chemin_zip, 'r') as zipf:
            zipf.extractall(dossier_import)
            
        # Création du fichier marqueur caché
        with open(dossier_import / ".ignore_export", "w", encoding="utf-8") as f:
            f.write("Dossier importé. Ne pas ré-exporter.")
            
        return nom_dossier_clean