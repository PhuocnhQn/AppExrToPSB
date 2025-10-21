# ============================================================
# utils_functions.py — version 7.2.1
# Common utility functions for AppExrToPSB
# ============================================================

import os
import sys
import time
import shutil
import pythoncom
from datetime import datetime
import photoshop.api as ps

# ============================================================
# 📁 FOLDER / FILE UTILITIES
# ============================================================

def create_folders(folder_path):
    """Tạo thư mục nếu chưa tồn tại."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"📁 Created folder: {folder_path}")


def get_exr_files_in_directory(directory):
    """Trả về danh sách file .exr trong thư mục."""
    return [
        f for f in os.listdir(directory)
        if f.lower().endswith(".exr") and os.path.isfile(os.path.join(directory, f))
    ]


def check_exr_files_in_directory(directory):
    """Kiểm tra có ít nhất 1 file .exr không."""
    return any(file.lower().endswith(".exr") for file in os.listdir(directory))


def check_png_files_in_directory(directory):
    """Kiểm tra có ít nhất 1 file .png không."""
    return any(file.lower().endswith(".png") for file in os.listdir(directory))


def move1_files(source_folder, target_folder):
    """
    Di chuyển 1 file EXR đầu tiên từ source sang target.
    Tự động đổi tên nếu bị trùng.
    """
    exr_files = get_exr_files_in_directory(source_folder)
    if not exr_files:
        print("⚠️ No EXR files to move.")
        return False

    first_file = exr_files[0]
    src = os.path.join(source_folder, first_file)
    dst = os.path.join(target_folder, first_file)

    while os.path.exists(dst):
        name, ext = os.path.splitext(first_file)
        first_file = f"{name}_new{ext}"
        dst = os.path.join(target_folder, first_file)

    try:
        shutil.move(src, dst)
        print(f"✅ Moved file: {first_file} → {target_folder}")
        return True
    except Exception as e:
        print(f"❌ Cannot move file ({first_file}): {e}")
        return False


# ============================================================
# 🧠 FILE STATUS & TIMESTAMP UTILITIES
# ============================================================

def has_file_changed(file_path, delay=5):
    """
    Kiểm tra file có thay đổi kích thước sau delay giây hay không.
    Trả về True nếu file đang bị ghi / chưa ổn định.
    """
    try:
        size1 = os.path.getsize(file_path)
        if size1 == 0:
            return True
        time.sleep(delay)
        size2 = os.path.getsize(file_path)
        return size1 != size2
    except FileNotFoundError:
        return True
    except Exception as e:
        print("Error checking file:", e)
        return True


def get_file_modified_time(file_path):
    """Trả về thời gian sửa đổi cuối cùng của tệp (datetime)."""
    try:
        return datetime.fromtimestamp(os.path.getmtime(file_path))
    except FileNotFoundError:
        return None


def get_file_modified_time(file_path):
    """Lấy thời gian chỉnh sửa cuối cùng của file (datetime)."""
    if not os.path.exists(file_path):
        return None
    return datetime.fromtimestamp(os.path.getmtime(file_path))


def compare_file_modification_time(file_prepost, file_processed, threshold_seconds=30):
    """
    So sánh thời gian chỉnh sửa giữa file prepost và processed.

    Quy tắc:
    1️⃣ Nếu prepost CŨ HƠN processed  → Trả về True  (processed mới hơn → bỏ qua)
    2️⃣ Nếu prepost MỚI HƠN processed → 
        - Nếu chênh lệch >= threshold_seconds (30s) → True  (đã đủ ổn định để xử lý)
        - Nếu chênh lệch < threshold_seconds → False (mới cập nhật, chờ thêm)
    """

    t1 = get_file_modified_time(file_prepost)
    t2 = get_file_modified_time(file_processed)
    # print("Modification times:", t1, t2)
    if not t1 or not t2:
        return False

    diff = (t1 - t2).total_seconds()

    if diff < 0:
        # prepost cũ hơn processed → skip
        return True
    else:
        # prepost mới hơn processed → chỉ True nếu cách ≥ 30s
        return diff >= threshold_seconds
# ============================================================
# 🪄 JSX EXECUTION UTILITIES
# ============================================================

def run_jsx(filename):
    """Chạy file JSX trong Photoshop."""
    if getattr(sys, 'frozen', False):
        # Khi chương trình đã được đóng gói (.exe)
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    jsx_folder = os.path.join(base_dir, "jsx")
    jsx_path = os.path.join(jsx_folder, filename)

    if not os.path.exists(jsx_path):
        print(f"❌ JSX not found: {jsx_path}")
        return False

    print(f"▶ Running JSX: {jsx_path}")
    pythoncom.CoInitialize()
    try:
        app = ps.Application()
        app.DoJavaScriptFile(jsx_path)
        print(f"✅ JSX executed successfully: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error running JSX: {e}")
        return False
    finally:
        pythoncom.CoUninitialize()
