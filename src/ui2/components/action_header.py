from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont

class ActionHeader(QWidget):
    def __init__(self, cmd_new_folder, cmd_add_pdf, cmd_rename, cmd_move, cmd_delete):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Ma Bibliothèque")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        def make_btn(text, tooltip, cmd):
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.clicked.connect(cmd)
            btn.setFixedWidth(35)
            layout.addWidget(btn)

        make_btn("📁", "Nouveau dossier", cmd_new_folder)
        make_btn("➕", "Ajouter un article PDF", cmd_add_pdf)
        make_btn("✏️", "Renommer l'élément", cmd_rename)
        make_btn("➡️", "Déplacer l'élément", cmd_move)
        make_btn("🗑️", "Supprimer l'élément", cmd_delete)

        layout.addStretch() # Pousse tout vers la gauche