# ============================================================
# photoshop_thread.py — version 7.2.1
# Thread-based Photoshop control for AppExrToPSB
# ============================================================

import os
import time
import pythoncom
import pyautogui
import pygetwindow as gw
import photoshop.api as ps
from threading import Thread


class PhotoshopThread:
    """
    Quản lý các thao tác với Photoshop (mở EXR, auto nhấn Enter, bring to front)
    """

    def __init__(self, config):
        self.config = config
        self.running_open_exr = True
        self.running = False

    # ============================================================
    # 📂 BẮT ĐẦU QUY TRÌNH MỞ FILE EXR
    # ============================================================

    def start_processing_open_exr(self, config_file_path, file_path):
        """Khởi chạy 2 thread song song: mở file EXR & auto nhấn Enter"""
        t1 = Thread(target=self.open_EXR_file, args=(config_file_path, file_path))
        t1.start()

    def open_EXR_file(self, config_file_path, file_path):
        """Mở EXR file trong Photoshop"""
        try:
            # Bật trạng thái xử lý EXR
            self.config["Processing_exr"] = {"openEXR": "true"}
            with open(config_file_path, "w") as cfg:
                self.config.write(cfg)

            # Sau khi gọi mở EXR, khởi động thread auto Enter
            self.running = True
            t2 = Thread(target=self.auto_press_enter, args=(2, file_path))
            t2.start()
            # Mở file EXR trong Photoshop
            print("🟢 Opening EXR file in Photoshop...")
            self.open_file_in_photoshop(file_path)

            # Chờ một chút để đảm bảo Enter xử lý xong hộp thoại
            time.sleep(5)

        except Exception as e:
            print("❌ open_EXR_file error:", e)

        finally:
            # Reset trạng thái
            self.config["Processing_exr"] = {"openEXR": "false"}
            with open(config_file_path, "w") as cfg:
                self.config.write(cfg)

            self.running = False
            print("✅ open_EXR_file completed.")


    def open_file_in_photoshop(self, file_path):
        """Thực hiện lệnh mở file EXR"""
        try:
            exr_files = self.get_exr_file_paths_in_directory(file_path)
            if not exr_files:
                print("⚠️ No EXR file found to open.")
                return

            path_exr = os.path.normpath(exr_files[0])
            self.bring_photoshop_to_front("Adobe Photoshop")
            time.sleep(1)  # chờ 1 giây để đảm bảo focus xong
            pythoncom.CoInitialize()
            try:
                app = ps.Application()
                app.DoJavaScript("app.displayDialogs = DialogModes.NO;")
                if os.path.exists(path_exr):
                    print(f"🟢 Opening file: {path_exr}")
                    app.Open(path_exr)
                    print("✅ File opened successfully in Photoshop.")
                else:
                    print(f"❌ File not found: {path_exr}")
            except Exception as e:
                print("❌ Photoshop error while opening file:", e)
            finally:
                pythoncom.CoUninitialize()
        except Exception as e:
            print("❌ open_file_in_photoshop() error:", e)


    # ============================================================
    # 🖱️ AUTO ENTER & WINDOW CONTROL
    # ============================================================

    def auto_press_enter(self, delay, folder_exr):
        """Tự động nhấn Enter khi Photoshop đang mở EXR"""
        print("[THREAD] auto_press_enter started.")
        try:
            while self.running:
                status = self.config.get("Processing_exr", "openEXR", fallback="false")
                current_doc = self.get_current_document_name()
                self.bring_photoshop_to_front(current_doc)

                if status == "true":
                    time.sleep(delay)
                    pyautogui.press('enter')
                    print("[AUTO] Pressed ENTER (Photoshop active).")

                time.sleep(1)
        except Exception as e:
            print("[FATAL] auto_press_enter crashed:", e)
        finally:
            self.running_open_exr = False
            print("[END] auto_press_enter ended cleanly.")

    def bring_photoshop_to_front(self, current_document_name=None):
        """Đưa cửa sổ Photoshop ra trước màn hình (ngay cả khi chưa có tài liệu mở)."""
        try:
            if not current_document_name or current_document_name.strip() == "":
                current_document_name = "Adobe Photoshop"

            windows = gw.getWindowsWithTitle(current_document_name)
            if not windows:
                # Nếu chưa có file mở, tìm cửa sổ chính
                windows = gw.getWindowsWithTitle("Adobe Photoshop")

            if windows:
                windows[0].activate()
                print(f"🪟 Photoshop focused: {windows[0].title}")
            else:
                print("⚠️ Photoshop window not found.")
        except Exception as e:
            print(f"⚠️ bring_photoshop_to_front failed: {e}")

    def get_current_document_name(self):
        """Lấy tên file hiện tại đang mở trong Photoshop"""
        pythoncom.CoInitialize()
        try:
            app = ps.Application()
            active_doc = app.ActiveDocument
            return active_doc.Name if active_doc else "Adobe Photoshop"
        except Exception:
            return "Adobe Photoshop"
        finally:
            pythoncom.CoUninitialize()

    def get_exr_file_paths_in_directory(self, directory):
        """Trả về danh sách đầy đủ đường dẫn file EXR trong thư mục"""
        exr_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(".exr"):
                    exr_files.append(os.path.join(root, file))
        return exr_files
