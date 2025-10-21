# photoshop_thread.py
from PyQt5.QtCore import QThread, pyqtSignal
import photoshop.api as ps
import pythoncom
import sys

class PhotoshopConnectThread(QThread):
    connected = pyqtSignal(object)
    failed = pyqtSignal(str)

    def run(self):
        # ✅ Kiểm tra xem có đang chạy dưới dạng EXE không
        is_frozen = getattr(sys, 'frozen', False)
        
        try:
            if is_frozen:
                # 🚨 Đang chạy EXE - cần khởi tạo COM
                pythoncom.CoInitialize()
            
            app = ps.Application()
            print("✅ Photoshop connected successfully!")
            self.connected.emit(app)

        except Exception as e:
            print("❌ Photoshop connect error:", e)
            self.failed.emit(str(e))
        
        # ❌ KHÔNG gọi CoUninitialize() ở đây - giữ COM alive
    