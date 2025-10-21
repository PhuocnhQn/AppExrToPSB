from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
import os


class LogEmitter(QObject):
    log_signal = pyqtSignal(str)


class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ========= WINDOW =========
        self.setWindowTitle("Processing Log")
        self.resize(700, 400)
        self.setWindowFlags(Qt.Tool)
        self.setParent(parent)

        self.setAttribute(Qt.WA_DeleteOnClose, True)  # không bị destroy khi ẩn

        # ========= ICON =========
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "resources", "app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # ========= UI =========
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            background-color: #0e1018;
            color: #d5e2ff;
            font-family: Consolas;
            font-size: 13px;
            border: 1px solid #2a3350;
        """)
        layout.addWidget(self.text_edit)

        # 🔹 Button Hide
        self.hide_btn = QPushButton("Hide Log", self)
        self.hide_btn.setStyleSheet("""
            QPushButton {
                background-color: #171b2e;
                color: #e8eefc;
                border: 1px solid #2a3350;
                border-radius: 6px;
                padding: 5px;
            }
            QPushButton:hover { background-color: #232a46; }
            QPushButton:pressed { background-color: #2d3658; }
        """)
        self.hide_btn.clicked.connect(self.hide)
        layout.addWidget(self.hide_btn)
        self.setLayout(layout)

        # ========= SIGNAL =========
        self.emitter = LogEmitter()
        self.emitter.log_signal.connect(self.add_log, Qt.QueuedConnection)
        self.log_history = []

    # ========== Ghi log ==========
    def add_log(self, message: str):
        text = str(message).strip()
        if not text:
            return
        self.log_history.append(text)
        self.text_edit.append(text)
        self.text_edit.verticalScrollBar().setValue(
            self.text_edit.verticalScrollBar().maximum()
        )

    # ========== Ẩn thay vì đóng ==========
    def closeEvent(self, event):
        event.ignore()
        self.hide()
