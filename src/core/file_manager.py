import shutil
from pathlib import Path
import re

class FileManager:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.articles_path = self.base_path / "articles"
        self.templates_path = Path("src/templates")
        
    def setup_directories(self):
        self.articles_path.mkdir(parents=True, exist_ok=True)
        self.templates_path.mkdir(parents=True, exist_ok=True)
        
    def add_article(self, pdf_source_path: str, target_dir: str = None) -> bool:
        """Copie un PDF et génère son Markdown dans le dossier cible sélectionné."""
        source = Path(pdf_source_path)
        if not source.exists() or source.suffix.lower() != '.pdf':
            print("Erreur : Le fichier n'existe pas ou n'est pas un PDF.")
            return False
        
        # Si aucun dossier cible n'est précisé, on le met à la racine de 'articles'
        dest_path = Path(target_dir) if target_dir else self.articles_path
        
        # 1. Copie du PDF
        destination_pdf = dest_path / source.name
        shutil.copy2(source, destination_pdf)
        
        # 2. Création du Markdown avec le même nom
        md_name = source.stem + ".md"
        destination_md = dest_path / md_name
        
        if not destination_md.exists():
            self._create_markdown_from_template(destination_md)
            
        return True

    def create_folder(self, folder_name: str, target_dir: str = None) -> bool:
        """Crée un sous-dossier dans le dossier cible sélectionné."""
        parent_path = Path(target_dir) if target_dir else self.articles_path
        new_folder = parent_path / folder_name
        new_folder.mkdir(parents=True, exist_ok=True)
        return True
        
    def _create_markdown_from_template(self, destination: Path):
        """Utilise le template s'il existe, sinon crée un Markdown structuré."""
        template_file = self.templates_path / "template_note.md"
        
        # Le nouveau plan pré-écrit avec bloc LaTeX
        contenu_par_defaut = f"""# {destination.stem}

        ## Mots-clés
        **FR :** 
        **EN :** 

        ## Résumé


        ## Informations importantes
        - 
        - 

        ## Citer l'article (BibTeX / LaTeX)
        ```latex
        @article{{cle_citation,
        title={{{destination.stem}}},
        author={{Nom_Auteur, Initiale.}},
        journal={{Nom_du_Journal}},
        year={{Année}}
        }}
        """

        if template_file.exists():
            shutil.copy2(template_file, destination)
        else:
            # Si le fichier physique template_note.md n'existe pas, on injecte ce contenu
            with open(destination, "w", encoding="utf-8") as f:
                f.write(contenu_par_defaut)

    def rename_item(self, target_path: str, new_name: str) -> bool:
        """Renomme un dossier ou un fichier (et son Markdown associé)."""
        path = Path(target_path)
        if not path.exists():
            return False
        
        if path.is_dir():
            # Renommage d'un dossier
            new_path = path.parent / new_name
            path.rename(new_path)
        else:
            # Renommage d'un article
            # On s'assure que le nouveau nom a bien l'extension .pdf
            if not new_name.lower().endswith('.pdf'):
                new_name += '.pdf'
            
            new_pdf_path = path.parent / new_name
            path.rename(new_pdf_path)
            
            # On cherche et on renomme le Markdown correspondant
            md_path = path.parent / (path.stem + ".md")
            if md_path.exists():
                new_md_name = new_pdf_path.stem + ".md"
                md_path.rename(path.parent / new_md_name)
                
        return True

    def move_item(self, source_path: str, dest_dir: str) -> bool:
        """Déplace un dossier ou un fichier (et son Markdown associé) vers un autre dossier."""
        src = Path(source_path)
        dest = Path(dest_dir)
        
        if not src.exists() or not dest.exists() or not dest.is_dir():
            return False
            
        if src.is_dir():
            # Déplacement d'un dossier entier
            shutil.move(str(src), str(dest / src.name))
        else:
            # Déplacement du PDF
            shutil.move(str(src), str(dest / src.name))
            
            # Déplacement du Markdown associé
            md_path = src.parent / (src.stem + ".md")
            if md_path.exists():
                shutil.move(str(md_path), str(dest / md_path.name))
                
        return True
    
    def search_by_keyword(self, keyword: str) -> list[Path]:
        """Cherche un mot-clé uniquement dans la section 'Mots-clés' des fichiers Markdown."""
        resultats = []
        keyword = keyword.lower()

        # On utilise rglob pour scanner les .md dans tous les sous-dossiers
        for md_file in self.articles_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # La magie de la Regex : on capture tout ce qui est entre "## Mots-clés" et le prochain "##" (ou la fin du fichier \Z)
                match = re.search(r'## Mots-clés(.*?)(?:##|\Z)', content, re.DOTALL | re.IGNORECASE)

                if match:
                    mots_cles_section = match.group(1).lower()
                    if keyword in mots_cles_section:
                        # Si on trouve le mot, on récupère le chemin du PDF correspondant
                        pdf_path = md_file.with_suffix('.pdf')
                        if pdf_path.exists():
                            resultats.append(pdf_path)
                            
            except Exception as e:
                print(f"Erreur de lecture pour {md_file}: {e}")

        return resultats