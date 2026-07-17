import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QSize

class ActionHeader(QWidget):
    def __init__(self, cmd_new_folder, cmd_add_pdf, cmd_rename, cmd_move, cmd_delete):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Ma Bibliothèque")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # --- GESTION DU CHEMIN POUR LE .EXE ---
        if hasattr(sys, '_MEIPASS'):
            # Si on est dans le .exe, PyInstaller a mis les dossiers ici
            base_dir = Path(sys._MEIPASS)
        else:
            # Si on lance le script python normal
            base_dir = Path(__file__).resolve().parents[3]
            
        chemins_icones = base_dir / "assets"
        # ---------------------------------------

        def make_btn(nom_fichier_icone, tooltip, cmd):
            btn = QPushButton()
            chemin_complet = chemins_icones / nom_fichier_icone
            
            if not chemin_complet.exists():
                btn.setText("?")
                btn.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
            else:
                chemin_str = chemin_complet.as_posix()
                btn.setIcon(QIcon(chemin_str))
                btn.setIconSize(QSize(36, 36))
            
            btn.setToolTip(tooltip)
            btn.clicked.connect(cmd)
            btn.setFixedSize(40, 40)
            layout.addWidget(btn)

        make_btn("dossier.png", "Nouveau dossier", cmd_new_folder)
        make_btn("ajouter.png", "Ajouter un ou plusieurs PDF", cmd_add_pdf)
        make_btn("renommer.png", "Renommer l'élément", cmd_rename)
        make_btn("deplacer.png", "Déplacer l'élément", cmd_move)
        make_btn("supprimer.png", "Supprimer l'élément", cmd_delete)

        layout.addStretch()