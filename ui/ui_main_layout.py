# ui_layout.py
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt
import os
from PyQt5.QtGui import QIcon


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self,):

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "resources", "app_icon.ico")

        self.setWindowTitle("AppExrToPSB — Photoshop Automation Tool")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setGeometry(200, 200, 400, 300)

        # --- Label + Input ---
        self.folder_label_in = QLabel("Folder input:", self)
        self.folder_label_in.setGeometry(10, 30, 80, 20)

        self.folder_path_in = QLineEdit(self)
        self.folder_path_in.setGeometry(100, 30, 190, 20)

        self.select_folder_button_in = QPushButton("Select Folder", self)
        self.select_folder_button_in.setGeometry(300, 30, 90, 20)

        # --- Combo + Checkbox ---
        self.selected_option = QComboBox(self)
        self.selected_option.setGeometry(10, 60, 380, 20)
        self.selected_option.addItems(["8 Bits/Channel", "16 Bits/Channel", "32 Bits/Channel"])
        self.selected_option.setCurrentText("16 Bits/Channel")

        self.checkbox_processes = QCheckBox("Processes", self)
        self.checkbox_processes.setGeometry(10, 90, 100, 20)

        self.checkbox_prepost = QCheckBox("Prepost", self)
        self.checkbox_prepost.setGeometry(120, 90, 100, 20)

        self.folder_label_delay = QLabel("Delay (min):", self)
        self.folder_label_delay.setGeometry(10, 120, 80, 20)
        self.txt_delay = QLineEdit(self)
        self.txt_delay.setGeometry(100, 120, 80, 20)

        self.txt_label_computer_name = QLabel("Computer:", self)
        self.txt_label_computer_name.setGeometry(200, 120, 80, 20)
        self.txt_computer_name = QLineEdit(self)
        self.txt_computer_name.setGeometry(280, 120, 100, 20)

        # --- Button Row (1 line) ---
        self.button_container = QWidget(self)
        self.button_container.setGeometry(10, 180, 380, 40)
        self.button_layout = QHBoxLayout(self.button_container)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.close_button = QPushButton("Close")
        self.log_button = QPushButton("Show Log")

        for btn in [self.start_button, self.stop_button, self.close_button, self.log_button]:
            self.button_layout.addWidget(btn)

        # --- Info Labels ---
        self.info_label = QLabel("", self)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setGeometry(10, 230, 380, 20)

        self.info_label_process = QLabel("", self)
        self.info_label_process.setAlignment(Qt.AlignCenter)
        self.info_label_process.setGeometry(10, 260, 380, 20)

        # ===================== Hiển thị version =====================
        version = os.getenv("APP_VERSION", "v1.0.0")  # giá trị mặc định nếu chưa có .env
        self.version_label = QLabel(f"ExrToPSB {version}", self)
        self.version_label.setAlignment(Qt.AlignRight)
        self.version_label.setStyleSheet("color: #888; font-size: 12px; font-style: italic;")
        self.version_label.setGeometry(250, 280, 140, 20)  # vị trí góc dưới bên phải
