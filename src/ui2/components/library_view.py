from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTreeWidget
from PyQt6.QtCore import QTimer

class LibraryView(QWidget):
    def __init__(self, cmd_search, cmd_cancel, on_select, on_double_click):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Barre de recherche
        search_layout = QHBoxLayout()
        self.search_var = QLineEdit()
        self.search_var.setPlaceholderText("Chercher un mot-clé...")
        self.timer_recherche = QTimer()
        self.timer_recherche.setSingleShot(True)
        self.timer_recherche.timeout.connect(lambda: cmd_search(self.search_var.text()))
        
        # Au lieu de chercher à chaque lettre, on relance le chrono de 300ms
        self.search_var.textChanged.connect(lambda: self.timer_recherche.start(300))
        # ------------------------------
        
        search_layout.addWidget(self.search_var)

        btn_search = QPushButton("🔍")
        btn_search.clicked.connect(lambda: cmd_search(self.search_var.text()))
        btn_search.setFixedWidth(40)
        search_layout.addWidget(btn_search)

        btn_cancel = QPushButton("❌")
        btn_cancel.setStyleSheet("background-color: #a83232;")
        btn_cancel.clicked.connect(cmd_cancel)
        btn_cancel.setFixedWidth(40)
        search_layout.addWidget(btn_cancel)

        layout.addLayout(search_layout)

        # Arborescence (QTreeWidget remplace le Treeview de Tkinter)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderHidden(True)
        self.tree.setColumnHidden(1, True) # Colonne cachée pour le chemin
        self.tree.setColumnHidden(2, True) # Colonne cachée pour le type
        self.tree.itemSelectionChanged.connect(on_select)
        self.tree.collapseAll()  #ferme tous les dossiers au démarrage
        self.tree.itemDoubleClicked.connect(self._toggle_dossier)
        layout.addWidget(self.tree)

    def clear_search(self):
        self.search_var.clear()
    
    def _toggle_dossier(self, item, column):
        # On vérifie si l'élément cliqué est bien un dossier (adapte l'index "2" selon ton code)
        if item.text(2) == "dossier": 
            item.setExpanded(not item.isExpanded())