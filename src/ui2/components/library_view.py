from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTreeWidget

class LibraryView(QWidget):
    def __init__(self, cmd_search, cmd_cancel, on_select, on_double_click):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Barre de recherche
        search_layout = QHBoxLayout()
        self.search_var = QLineEdit()
        self.search_var.setPlaceholderText("Chercher un mot-clé...")
        self.search_var.returnPressed.connect(lambda: cmd_search(self.search_var.text()))
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
        self.tree.itemDoubleClicked.connect(on_double_click)
        layout.addWidget(self.tree)

    def clear_search(self):
        self.search_var.clear()