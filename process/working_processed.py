# ============================================================
# working_processed.py — version 7.2.1
# Workflow handler for "Processed" stage in AppExrToPSB
# ============================================================

import os, sys
import time
from .utils_functions import (
    create_folders,
    check_exr_files_in_directory,
    move1_files,
    run_jsx,
)
from .photoshop_thread import PhotoshopThread
from .workflow_helpers import update_ui_label

class WorkingProcessed:
    """Quy trình xử lý cho thư mục 'Processed'"""

    def __init__(self, config, ui):
        self.config = config
        self.ui = ui
        self.ps_thread = PhotoshopThread(config)

    # ============================================================
    # MAIN WORKFLOW
    # ============================================================
    def working_processed(
        self, working_folder, complete_folder, working1_folder, complete1_folder, minutes
    ):
        """Xử lý file EXR trong workflow Processed"""

        create_folders(working_folder)
        create_folders(complete_folder)

        while True:
            # ========== DỪNG KHI TẮT ==========
            status = self.config.get("Processing", "status")
            if status == "false":
                update_ui_label(self.ui,"🛑 Stopping Processed workflow...")
                print("🛑 Processing stopped (Processed workflow).")
                return

            # ========== KIỂM TRA FILE EXR TRONG FOLDER ==========
            exr_files = [
                file
                for file in os.listdir(complete_folder)
                if file.lower().endswith(".exr")
            ]

            if len(exr_files) > 1:
                print(f"⚠️ There are {len(exr_files)} .exr files in the folder.")
                time.sleep(5)
                continue
            elif len(exr_files) == 1:
                print("📄 There is 1 .exr file in the folder.")
            else:
                print("📂 No .exr files found in the folder.")

                exr_files_get = [
                    f
                    for f in os.listdir(working_folder)
                    if f.lower().endswith(".exr")
                ]
                if exr_files_get:
                    first_file = exr_files_get[0]
                    source_path = os.path.join(working_folder, first_file)
                    print("source_path:", source_path)

                    update_ui_label(self.ui,"Starting Processed workflow...")
                    time.sleep(2)
                    delay_sec = int(minutes) * 60
                    update_ui_label(self.ui,f"⏳ Waiting {minutes} minute(s)...")   
                    print(f"⏳ Waiting {minutes} minute(s)...")

                    for i in range(delay_sec, 0, -1):
                        time.sleep(1)
                        update_ui_label(self.ui,f"  Delay countdown: {i}s remaining")   
                        print(f"  Delay countdown: {i}s remaining")
                        # cho phép dừng giữa chừng
                        status = self.config.get("Processing", "status")
                        if status == "false":
                            return

                    move1_files(working_folder, complete_folder)
                    print("✅ Moved 1 EXR file from 'output' to 'working'.")

            # ========== SAU KHI CÓ FILE TRONG COMPLETE ==========
            has_exr_files = check_exr_files_in_directory(complete_folder)
            if not has_exr_files:
                print("❌ No .exr file found in complete folder, retrying...")
                time.sleep(5)
                continue

            print("🧩 Handle PSB Processed...")
            try:
                print("▶ Start Script Processed...")
                # mở file EXR trong Photoshop
                # ✅ Nếu đang chạy EXE (PyInstaller)
                if getattr(sys, 'frozen', False):
                    base_dir = os.path.dirname(sys.executable)  # thư mục chứa file .exe
                else:
                    # ✅ Nếu chạy trong môi trường dev (từ mã nguồn)
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                # ✅ Luôn đảm bảo thư mục data tồn tại
                data_dir = os.path.join(base_dir, "data")
                os.makedirs(data_dir, exist_ok=True)
                # ✅ Đường dẫn tuyệt đối đến config.ini
                default_config_path = os.path.join(data_dir, "config.ini")
                config_file_path = self.config["Paths"].get("config_file_path", default_config_path)
                print("config_file_path:", config_file_path)
                update_ui_label(self.ui,"▶ Opening EXR in Photoshop...")
                self.ps_thread.start_processing_open_exr(config_file_path, complete_folder)

                # đợi mở EXR xong
                while self.ps_thread.running_open_exr:
                    time.sleep(5)
                    status = self.config.get("Processing", "status")
                    if status == "false":
                        update_ui_label(self.ui,"🛑 Stopping Processed workflow...")
                        print("🛑 Processing stopped (Processed workflow).")
                        return
                    update_ui_label(self.ui,"⌛ Waiting for EXR to open in Photoshop...")   
                    print("⌛ Waiting for EXR to open in Photoshop...")

                print("✅ EXR opened successfully.")

                # chạy JSX Processed.jsx
                update_ui_label(self.ui,"▶ Running JSX: Processed.jsx")
                print("▶ Running JSX: Processed.jsx")
                jsx_file_name = "Processed.jsx"
                run_jsx(jsx_file_name)

            except FileNotFoundError:
                print("❌ JSX file not found: Processed.jsx")
            except Exception as e:
                print("⚠️ Error during Processed run:", e)
                
            update_ui_label(self.ui,"🏁 Complete PSB Processed workflow.")
            print("🏁 Complete PSB Processed workflow.")
            move1_files(working1_folder, complete1_folder)
            print("📦 Moved result from 'working' to 'complete' (Processed).")

            # reset trạng thái
            self.ps_thread.running_open_exr = True
            time.sleep(5)
