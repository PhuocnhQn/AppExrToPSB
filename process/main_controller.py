# ============================================================
# main_controller.py — version 7.2.2 (finalized)
# Central controller for AppExrToPSB automation
# ============================================================

import os
import sys
import time
import configparser
from threading import Thread
from PyQt5.QtWidgets import QFileDialog

from log.ui.log_window import LogWindow
from ui.ui_main_layout import Ui_MainWindow
from .working_processed import WorkingProcessed
from .working_prepost import WorkingPrepost
from .utils_functions import create_folders
from log.process.gui_logger import QTextEditLogger
from .workflow_helpers import update_ui_label, check_processing_status


class MainController(Ui_MainWindow):
    """Điều khiển toàn bộ workflow Processed + Prepost"""

    def __init__(self):
        super().__init__()
        # -----------------------------
        # 🔧 Cấu hình & khởi tạo
        # -----------------------------
        self.setup_ui()
        self.config = configparser.ConfigParser()
        self.setup_logic()
        self.load_last_config()

        # -----------------------------
        # 🔗 Gán sự kiện cho nút UI
        # -----------------------------
        self.start_button.clicked.connect(self.start_processing)
        self.stop_button.clicked.connect(self.stop_processing)
        self.close_button.clicked.connect(self.close_application)
        self.log_button.clicked.connect(self.toggle_log_window)
        self.select_folder_button_in.clicked.connect(self.select_folder_in)
        print("✅ MainController initialized")

    # ============================================================
    # Show Log Window
    # ============================================================
    def toggle_log_window(self):
        """Bật/tắt log panel mà không đóng chương trình."""
        if self.log_window.isVisible():
            self.log_window.hide()
            self.log_button.setText("Show Log")
        else:
            print("🪶 Opening Processing Log window...")
            self.log_window.show()
            self.log_window.raise_()
            self.log_window.activateWindow()
            self.log_button.setText("Hide Log")

    # ============================================================
    # Select Folder In
    # ============================================================
    def select_folder_in(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path_in.setText(folder)

    # ============================================================
    # SETUP
    # ============================================================
    def setup_logic(self):
        """Khởi tạo cấu trúc thư mục và đọc config"""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        # Thư mục data nằm cạnh file exe (hoặc cạnh thư mục source)
        data_folder = os.path.join(base_dir, "data")
        create_folders(data_folder)

        self.config_file_path = os.path.join(data_folder, "config.ini")
        if not os.path.exists(self.config_file_path):
            with open(self.config_file_path, "w") as f:
                f.write("[Processing]\nstatus=false\n")

        self.config.read(self.config_file_path)

        # log window
        self.log_window = LogWindow(self)
        self.log_window.hide()
        sys.stdout = QTextEditLogger(self.log_window)
        sys.stderr = QTextEditLogger(self.log_window)
        print("📁 setup_logic completed")
    # ============================================================
    # LOAD LAST CONFIG
    # ============================================================    
    def load_last_config(self):
        """Đọc lại dữ liệu đã lưu từ config.ini và hiển thị lên giao diện"""
        try:
            if not os.path.exists(self.config_file_path):
                print("⚠️ No config file found, skip loading previous data.")
                return

            self.config.read(self.config_file_path)

            # --- Lấy dữ liệu đã lưu ---
            folder_in = self.config.get("Paths", "source_folder", fallback="")
            chk_processes = self.config.get("Paths", "chk_processes", fallback="0")
            chk_prepost = self.config.get("Paths", "chk_preposr", fallback="0")
            delay_min = self.config.get("Paths", "delay_min", fallback="")
            computer_name = self.config.get("Paths", "conputer_name", fallback="")

            # --- Cập nhật giao diện ---
            self.folder_path_in.setText(folder_in)
            self.checkbox_processes.setChecked(chk_processes == "1")
            self.checkbox_prepost.setChecked(chk_prepost == "1")
            self.txt_delay.setText(delay_min)
            self.txt_computer_name.setText(computer_name)

            print("✅ UI restored from last saved config.ini")

        except Exception as e:
            print(f"⚠️ Failed to load previous config: {e}")

    # ============================================================
    # START PROCESS
    # ============================================================
    def start_processing(self):
        update_ui_label(self, "🚀 Processing started...")
        """Khởi động toàn bộ workflow Processed & Prepost"""
        folder_in = self.folder_path_in.text().strip()
        if not folder_in:
            self.info_label_process.setText("⚠️ Please select input folder first.")
            print("Error: Input folder not selected.")
            return

        delay_text = self.txt_delay.text().strip()
        if not delay_text.isdigit():
            self.info_label_process.setText("⚠️ Delay must be a positive integer (minutes).")
            print("Error: Invalid delay value.")
            return

        minutes = int(delay_text)
        chk_processes = str(int(self.checkbox_processes.isChecked()))
        chk_prepost = str(int(self.checkbox_prepost.isChecked()))
        computer_name = self.txt_computer_name.text().strip() or "Default_PC"

        script_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        data_folder = os.path.join(script_folder, "data")
        create_folders(data_folder)

        self.config["Paths"] = {
            "source_folder": folder_in,
            "chk_processes": chk_processes,
            "chk_preposr": chk_prepost,
            "delay_min": str(minutes),
            "conputer_name": computer_name,
        }
        self.config["Processing"] = {"status": "true"}
        self.config["Processing_exr"] = {"openEXR": "false"}

        with open(os.path.join(data_folder, "config.ini"), "w") as cfg:
            self.config.write(cfg)

        folder_processed = os.path.join(folder_in, "processed")
        folder_prepost = os.path.join(folder_in, "prepost")
        folder_temp_user = os.path.join(folder_processed, "Temp", computer_name)

        for folder in [folder_processed, folder_prepost, folder_temp_user]:
            create_folders(folder)

        # Ghi file phụ
        txt_data = {
            "inputFolder.txt": folder_in,
            "mode.txt": self.selected_option.currentText(),
            "computer_name.txt": computer_name,
            "processes.txt": chk_processes,
            "preposr.txt": chk_prepost,
        }
        for name, content in txt_data.items():
            with open(os.path.join(data_folder, name), "w", encoding="utf-8") as f:
                f.write(content)
        # đem status check vào thread
        self.thread_check_status = Thread(target=check_processing_status, args=(self.config, self))
        self.thread_check_status.start()

        processed = WorkingProcessed(self.config, self)
        prepost = WorkingPrepost(self.config, self)

        if chk_processes == "1":
            Thread(
                target=processed.working_processed,
                args=(folder_in, folder_temp_user, folder_temp_user, folder_processed, minutes),
                daemon=True
            ).start()
        if chk_prepost == "1":
            Thread(
                target=prepost.working_prepost,
                args=(folder_prepost, folder_prepost, computer_name),
                daemon=True
            ).start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.info_label_process.setText("🚀 Processing started...")
        print("✅ All workflows started successfully.")

    # ============================================================
    # STOP PROCESS
    # ============================================================
    def stop_processing(self):
        print("🛑 Stop requested...")
        self.config["Processing"] = {"status": "false"}
        with open(self.config_file_path, "w") as cfg:
            self.config.write(cfg)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        print("✅ All workflows stopped.")

    # ============================================================
    # CLOSE APP
    # ============================================================
    def close_application(self):
        script_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        data_folder = os.path.join(script_folder, "data")
        create_folders(data_folder)
        cfg_file = os.path.join(data_folder, "config.ini")
        self.config["Processing"] = {"status": "false"}
        with open(cfg_file, "w") as f:
            self.config.write(f)
        self.close()
