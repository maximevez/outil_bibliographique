# 📚 Outil Bibliographique

## 🎯 Objectif du projet
Ce projet consiste en un logiciel desktop permettant la gestion de sa bibliographie et un partage communautaire[cite: 1]. Il a été pensé pour optimiser le flux de travail des chercheurs et étudiants lors de la revue de littérature, en liant étroitement la lecture de l'article scientifique à une prise de notes structurée et standardisée.

## ✨ Fonctionnalités
* **Archivage automatisé :** Le logiciel gère la sauvegarde des PDF en local dans un dossier dédié (`outil_bibliographique`) créé directement sur l'ordinateur de l'utilisateur[cite: 1].
* **Double ouverture intelligente :** Pour chaque ouverture d'un article depuis l'interface, le logiciel déclenche l'ouverture simultanée de l'article PDF sur un navigateur (Mozilla Firefox ou Microsoft Edge) et d'un fichier Markdown sur un IDE[cite: 1].
* **Prise de notes standardisée :** Le plan du fichier Markdown généré est déjà pré-écrit pour faire gagner du temps[cite: 1].
* **Partage et versioning léger :** La bibliothèque est gérée comme un dossier Git, ce qui permet de la partager facilement[cite: 1]. Un fichier `.gitignore` masque les fichiers `.pdf` pour n'exporter que les fichiers Markdown (beaucoup plus légers) sur les dépôts distants[cite: 1].
* **Démarrage adaptatif :** À l'ouverture de l'application : si l'utilisateur possède déjà une bibliothèque, le logiciel permet d'exporter sa propre bibliothèque avec Git[cite: 1]. S'il s'agit d'une première utilisation, l'outil propose de créer le dossier de départ "Ma Bibliothèque"[cite: 1].

---

## 🏗️ Architecture logicielle

Le projet est divisé en plusieurs modules afin de séparer la logique de l'interface graphique :

```text
outil_bibliographique/
├── main.py                  # Le point d'entrée qui lance l'application[cite: 1]
├── requirements.txt         # Les dépendances (ex: GitPython, PyQt, CustomTkinter)[cite: 1]
├── assets/                  # Tes icônes et logos[cite: 1]
├── src/
│   ├── ui/                  # L'interface graphique[cite: 1]
│   │   ├── fenetre_principale.py[cite: 1]
│   │   └── composants.py    # (boutons, listes, barres de recherche)[cite: 1]
│   ├── core/                # Le "cerveau" de l'application[cite: 1]
│   │   ├── git_manager.py   # Gère les git init, pull, commit, push[cite: 1]
│   │   ├── file_manager.py  # Copie les PDF, crée les dossiers, génère les MD[cite: 1]
│   │   └── launcher.py      # Utilise le module 'subprocess' pour ouvrir l'IDE et le Navigateur[cite: 1]
│   └── templates/           # Modèles de base[cite: 1]
│       └── template_note.md # Ton plan pré-écrit (Méthodologie, Résultats, Formules...)[cite: 1]
```

---

## ⚙️ Explication de la méthode (Workflow)

L'application repose sur le principe de la séparation totale entre le **code de l'outil** et les **données de l'utilisateur**.

1. **Initialisation :** Lors de la première exécution, le fichier `main.py` demande à l'utilisateur où il souhaite générer sa bibliothèque. Ce chemin est sauvegardé dans un fichier dynamique `config.json`.
2. **Ajout d'un article :** L'utilisateur importe un PDF via l'interface. Le `file_manager.py` prend le relais, copie le document proprement, nettoie le nom du fichier, et génère un `.md` jumeau à partir du `template_note.md`.
3. **Exploitation :** L'utilisateur navigue dans une arborescence (gérée via Tkinter/CustomTkinter). Il peut prévisualiser ses notes grâce à un moteur de rendu Markdown vers HTML intégré à la fenêtre. S'il clique sur "Ouvrir", le `launcher.py` ouvre simultanément les outils de lecture et d'édition.
4. **Collaboration :** L'utilisateur peut importer ou exporter des archives `.zip` de bibliothèques tierces (ou utiliser les fonctionnalités Git sous-jacentes) pour croiser ses recherches avec celles de ses collègues. Un système de "fichiers marqueurs" empêche la ré-exportation accidentelle des dossiers importés par autrui.

---

## 📦 Compilation : Créer l'exécutable (.exe)

Pour distribuer le logiciel à d'autres chercheurs sans nécessiter l'installation de Python, le projet est empaqueté avec **PyInstaller**.

**1. Installation du compilateur :**
Assurez-vous que l'environnement virtuel est activé, puis lancez :
```bash
pip install pyinstaller
```

**2. Compilation :**
À la racine du projet, exécutez la commande suivante :
```bash
pyinstaller --noconsole --onefile --name "Outil_Bibliographique" --icon="assets/logo.ico" main.py
```

**3. Déploiement :**
Récupérez le fichier généré dans le dossier `dist/` et partagez-le. L'exécutable est 100% autonome.

---

## 🚀 Installation pour le développement

Si vous souhaitez contribuer au code ou modifier l'application :

1. Cloner le dépôt Git :
   ```bash
   git clone <URL_DU_DEPOT>
   cd outil_bibliographique
   ```
2. Créer un environnement virtuel :
   ```bash
   python -m venv .venv
   ```
3. Activer l'environnement virtuel :
   * **Windows :** `.venv\Scripts\activate`
   * **Mac/Linux :** `source .venv/bin/activate`
4. Installer les dépendances listées dans le `requirements.txt` :
   ```bash
   pip install -r requirements.txt
   ```
5. Lancer l'application :
   ```bash
   python main.py
   ```