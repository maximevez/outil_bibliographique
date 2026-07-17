from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton

class ImportExportPanel(QWidget):
    def __init__(self, cmd_import, cmd_export):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        btn_import = QPushButton("📥 Importer ZIP")
        btn_import.setStyleSheet("background-color: #2fa572; font-weight: bold;")
        btn_import.clicked.connect(cmd_import)
        layout.addWidget(btn_import)

        btn_export = QPushButton("📦 Exporter ZIP")
        btn_export.setStyleSheet("background-color: #a55a1f; font-weight: bold;")
        btn_export.clicked.connect(cmd_export)
        layout.addWidget(btn_export)