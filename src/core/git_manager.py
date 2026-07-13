from git import Repo
from git.exc import InvalidGitRepositoryError
from pathlib import Path

class GitManager:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        # On initialise ou on charge le dépôt Git
        self.repo = self._init_or_load_repo()
        self._ensure_gitignore()

    def _init_or_load_repo(self) -> Repo:
        """Charge le dépôt existant ou lance un 'git init'."""
        try:
            return Repo(self.repo_path)
        except InvalidGitRepositoryError:
            return Repo.init(self.repo_path)

    def _ensure_gitignore(self):
        """Vérifie que le .gitignore existe bien pour exclure les PDF."""
        gitignore_path = self.repo_path / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write("*.pdf\n")
            
            # On commit immédiatement le .gitignore pour le sécuriser
            self.commit_all("Initialisation : Ajout du .gitignore")

    def commit_all(self, message: str = "Sauvegarde des notes Markdown"):
        """Équivalent de 'git add .' puis 'git commit -m'."""
        self.repo.git.add(all=True)
        
        # On vérifie s'il y a des modifications à sauvegarder
        if self.repo.is_dirty() or self.repo.untracked_files:
            self.repo.index.commit(message)
            print(f"Commit réussi : {message}")
        else:
            print("Aucune modification à sauvegarder.")
            
    def pull_remote(self, remote_name: str = "origin", branch: str = "main"):
        """Permet de récupérer les notes d'un autre chercheur."""
        try:
            remote = self.repo.remotes[remote_name]
            remote.pull(branch)
            print("Mise à jour réussie.")
        except Exception as e:
            print(f"Erreur lors de la synchronisation : {e}")