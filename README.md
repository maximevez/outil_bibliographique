# outil_bibliographique

## But : 
Logiciel desktop permettant la gestion de sa bibliographie et un partage communautaire

## Fonctionnalités :
- Sauvegarde des pdf en local (dossier outil_bibliographique crée sur l'ordinateur en local)
- Pour chaque ouverture d'un article : ouverture simultanée de l'article pdf sur modzilla ou edge et d'un fichier markdown sur un IDE
- Le plan du mardown sera déja pré écrit
- ta bibliotheque est un dossier git permettant le partage facilement avec un gitignore .pdf pour exporter seulement les markdowns (plus léger)
- ouverture de l'application : j'ai deja une bibliothèque => exporte ta propre biblio avec git. Si premiere utilisation creer un dossier ma bibliothèque 

## Architecture du projet : 

outil_bibliographique/

├── main.py                  # Le point d'entrée qui lance l'application
├── requirements.txt         # Les dépendances (ex: GitPython, PyQt)
├── assets/                  # Tes icônes et logos
├── src/
│   ├── ui/                  # L'interface graphique
│   │   ├── fenetre_principale.py
│   │   └── composants.py    # (boutons, listes, barres de recherche)
│   ├── core/                # Le "cerveau" de l'application
│   │   ├── git_manager.py   # Gère les git init, pull, commit, push
│   │   ├── file_manager.py  # Copie les PDF, crée les dossiers, génère les MD
│   │   └── launcher.py      # Utilise le module 'subprocess' pour ouvrir l'IDE et le Navigateur
│   └── templates/           # Modèles de base
│       └── template_note.md # Ton plan pré-écrit (Méthodologie, Résultats, Formules...)*
