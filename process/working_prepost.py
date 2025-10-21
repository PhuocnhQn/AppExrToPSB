# ============================================================
# working_prepost.py — version 7.2.1
# Workflow handler for "Prepost" stage in AppExrToPSB
# ============================================================

import os
import sys
import time
import shutil
from .utils_functions import create_folders, run_jsx, check_png_files_in_directory, compare_file_modification_time
from .workflow_helpers import update_ui_label

class WorkingPrepost:
    """Quy trình xử lý cho thư mục 'Prepost'"""

    def __init__(self, config, ui):
        self.config = config
        self.ui = ui

    # ============================================================
    # MAIN WORKFLOW
    # ============================================================

    def working_prepost(self, working_folder, complete_folder, computer_name):
        """Theo dõi và xử lý file PNG trong workflow Prepost"""

        create_folders(working_folder)
        create_folders(complete_folder)

        while True:
            # ========== DỪNG ==========
            status = self.config.get("Processing", "status")
            if status == "false":
                update_ui_label(self.ui,"🛑 Stopping Prepost workflow...")
                print("🛑 Processing stopped (Prepost workflow).")
                return

            # ========== KIỂM TRA PNG vs PSB ==========
            png_files = [
                os.path.splitext(f)[0]
                for f in os.listdir(working_folder)
                if f.lower().endswith(".png")
            ]
            psb_files = [
                os.path.splitext(f)[0]
                for f in os.listdir(working_folder)
                if f.lower().endswith(".psb")
            ]

            different_names = [png for png in png_files if png not in psb_files]
            if not different_names:
                print("✅ All PNGs have matching PSB files.")
                time.sleep(5)
                continue

            # ========== XỬ LÝ CÁC FILE PNG CHƯA CÓ PSB ==========
            if different_names:
                for name_file in different_names:
                    # ========== DỪNG ==========
                    status = self.config.get("Processing", "status")
                    if status == "false":
                        update_ui_label(self.ui,"🛑 Stopping Prepost workflow...")
                        print("🛑 Processing stopped (Prepost workflow).")
                        return
                    print(f"🔎 Found unprocessed PNG: {name_file}.png")

                    # ========== KIỂM TRA TRẠNG THÁI FILE ==========
                    script_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
                    data_folder = os.path.join(script_folder, "data")
                    create_folders(data_folder)

                    processed_folder = os.path.join(
                        os.path.dirname(working_folder), "processed"
                    )


                    name_filePNG_prepost = os.path.join(working_folder, name_file + ".png")
                    name_filePNG_processed = os.path.join(processed_folder, name_file + ".png")
                    name_filePSD_processed = os.path.join(processed_folder, name_file + ".psb")
                    # print("Checking files:", name_filePNG_prepost, name_filePNG_processed, name_filePSD_processed)

                    if os.path.exists(name_filePNG_processed) and os.path.exists(name_filePSD_processed):
                        check_time = compare_file_modification_time(
                            name_filePNG_prepost, name_filePNG_processed
                        )

                        if not check_time:
                            print("⚠️ PNG in processed folder is newer or prepost not ready, skipping...")
                            time.sleep(5)
                            continue
                    else:
                        print("⚠️ Missing PNG/PSB in processed folder.")
                        time.sleep(5)
                        continue

                    # ========== COPY PNG QUA FOLDER USER ==========
                    user_temp_dir = os.path.join(complete_folder, "Temp", computer_name)
                    create_folders(user_temp_dir)
                    png_user_path = os.path.join(user_temp_dir, f"{name_file}.png")

                    try:
                        shutil.move(name_filePNG_prepost, png_user_path)
                        print(f"✅ Moved PNG to user folder: {png_user_path}")
                    except Exception as e:
                        print(f"⚠️ Cannot move PNG: {e}")
                        time.sleep(5)
                        continue

                    # ========== KIỂM TRA & CHẠY JSX ==========
                    has_png_files = check_png_files_in_directory(user_temp_dir)
                    if not has_png_files:
                        print("⚠️ No PNG in user Temp folder, retrying...")
                        time.sleep(5)
                        continue
                    # ========== CHẠY JSX PREPOST ==========
                    update_ui_label(self.ui,"Starting Prepost workflow...")
                    time.sleep(2)
                    # Ghi tên file PNG hiện tại vào data/pngFile.txt
                    png_file_txt = os.path.join(data_folder, "pngFile.txt")
                    with open(png_file_txt, "w", encoding="utf-8") as f:
                        f.write(os.path.join(user_temp_dir, name_file + ".png"))
                    print(f"📝 Wrote current PNG to {png_file_txt}")
                    time.sleep(1)
                    try:
                        update_ui_label(self.ui,"▶ Running JSX: prepost.jsx")
                        print("▶ Running JSX: prepost.jsx")
                        run_jsx("prepost.jsx")

                        # move file trở lại
                        shutil.move(png_user_path, name_filePNG_prepost)
                        print("✅ PNG returned to main folder.")
                    except FileNotFoundError:
                        print("❌ JSX file not found: prepost.jsx")
                    except Exception as e:
                        print(f"⚠️ Error during prepost.jsx run: {e}")
                        
                    update_ui_label(self.ui,"🏁 Complete prepost process."  )
                    print("🏁 Complete prepost process.")
                    time.sleep(5)
                # End for different_names
                time.sleep(5)
