# ============================================================
# ui_helpers.py — tiện ích cập nhật giao diện an toàn từ thread
# ============================================================

from PyQt5.QtCore import QMetaObject, Qt, Q_ARG

# ============================================================
# ui_helpers.py — tiện ích cập nhật giao diện an toàn từ thread
# ============================================================

from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
import time

def check_processing_status(config, ui):
    """Theo dõi trạng thái Processing trong config.ini và cập nhật UI."""
    a = 0
    while True:
        a += 1
        status = config.get("Processing", "status", fallback="false")

        if status == "false":
            ui.info_label.setText("🛑 Processing stopped.")
            print("Processing stopped (check_processing_status).")
            return

        ui.info_label.setText(f"⚙️ Processing... {a} sec")
        print(f"Processing... {a} sec")

        time.sleep(1)

def update_ui_label(ui, text, target="info_label_process"):
    """
    Cập nhật text của label giao diện an toàn từ thread phụ.
    
    Parameters:
        ui: Đối tượng giao diện (MainController hoặc QWidget)
        text: Nội dung cần hiển thị
        target: tên thuộc tính label cần cập nhật (mặc định: info_label_process)
    """
    if ui is None:
        print("⚠️ update_ui_label() - ui = None")
        return

    label = getattr(ui, target, None)
    if label is None:
        print(f"⚠️ UI không có thuộc tính '{target}'")
        return

    try:
        QMetaObject.invokeMethod(
            label,
            "setText",
            Qt.QueuedConnection,
            Q_ARG(str, str(text))
        )
    except Exception as e:
        print(f"⚠️ Lỗi khi cập nhật label: {e}")
