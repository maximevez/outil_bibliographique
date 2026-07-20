from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QLabel, QComboBox,  QPushButton
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView  # <-- NOUVEL IMPORT
from PyQt6.QtCore import Qt
from src.ui2.components.action_header import ActionHeader
from src.ui2.components.library_view import LibraryView
from src.ui2.components.import_export import ImportExportPanel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings # <-- Indispensable pour lire les PDF

class MainWindow(QMainWindow):
    def __init__(self, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.setWindowTitle("Outil Bibliographique")
        self.resize(1200, 750)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Le séparateur redimensionnable
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # --- PANNEAU GAUCHE ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.header = ActionHeader(self.ctrl.creer_dossier, self.ctrl.ajouter_article, self.ctrl.renommer_element, self.ctrl.deplacer_element,self.ctrl.supprimer_element)
        left_layout.addWidget(self.header)

        self.lib_view = LibraryView(self.ctrl.lancer_recherche_via_ui, self.ctrl.annuler_recherche, self.ctrl.afficher_apercu, self.ctrl.ouvrir_article)
        left_layout.addWidget(self.lib_view)

        self.panel_import_export = ImportExportPanel(self.ctrl.handle_import, self.ctrl.handle_export)
        left_layout.addWidget(self.panel_import_export)

        # --- PANNEAU DROIT ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        header_droit = QHBoxLayout()
        self.lbl_titre_apercu = QLabel("Aucun article sélectionné")
        self.lbl_titre_apercu.setStyleSheet("font-weight: bold; font-size: 18px;")
        header_droit.addWidget(self.lbl_titre_apercu)

        header_droit.addStretch()

        self.btn_creer_note = QPushButton("📝 Créer Note")
        self.btn_creer_note.setStyleSheet("background-color: #2fa572; font-weight: bold;")
        self.btn_creer_note.clicked.connect(self.ctrl.creer_note_manquante)
        self.btn_creer_note.hide()
        header_droit.addWidget(self.btn_creer_note)

        self.btn_ouvrir = QPushButton("📖 Ouvrir")
        self.btn_ouvrir.clicked.connect(self.ctrl.ouvrir_article)
        self.btn_ouvrir.setEnabled(False)
        header_droit.addWidget(self.btn_ouvrir)

        self.menu_nav = QComboBox()
        self.menu_nav.addItems(["Système (Défaut)", "Firefox", "Edge", "Chrome"])
        header_droit.addWidget(self.menu_nav)

        right_layout.addLayout(header_droit)

        # Le widget natif QTextBrowser remplace tkinterweb
        # Le puissant moteur basé sur Chromium
        # Création du séparateur (coulissant de gauche à droite)
        self.split_droit = QSplitter(Qt.Orientation.Horizontal)
        
        # 1er écran : Le lecteur PDF
        self.pdf_viewer = QWebEngineView()
        settings = self.pdf_viewer.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True) # <-- Indispensable !
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True) # Autorise la lecture sur ton disque dur
        
        # 2ème écran : Ton lecteur Markdown actuel
        self.html_frame = QWebEngineView()

        # On ajoute les deux écrans au séparateur
        self.split_droit.addWidget(self.pdf_viewer)
        self.split_droit.addWidget(self.html_frame)
        
        # On donne plus de place au PDF par défaut (ex: 60% PDF, 40% Notes)
        self.split_droit.setSizes([600, 400])

        # On ajoute le tout au layout de droite
        right_layout.addWidget(self.split_droit)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([350, 850]) # Proportions de départ

    def set_titre_apercu(self, texte): self.lbl_titre_apercu.setText(texte)
    def set_etat_bouton_ouvrir(self, etat): self.btn_ouvrir.setEnabled(etat)
    def afficher_bouton_note(self, afficher): self.btn_creer_note.setVisible(afficher)
    def charger_html(self, html_content): self.html_frame.setHtml(html_content)
    def get_navigateur(self): return self.menu_nav.currentText()