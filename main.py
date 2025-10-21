import sys
import pythoncom  # ✅ thêm dòng này
from PyQt5.QtWidgets import QApplication
from connected_ps.process.photoshop_thread import PhotoshopConnectThread
from connected_ps.ui.loading_dialog import LoadingDialog
from process.main_controller import MainController

if __name__ == "__main__":
    # ✅ Khởi tạo COM context cho Photoshop
    pythoncom.CoInitialize()

    try:
        
        app = QApplication(sys.argv)

        loading = LoadingDialog()
        loading.show()
        QApplication.processEvents()


        connect_thread = PhotoshopConnectThread()
        global ui  # giữ biến toàn cục

        def on_connected():
            global ui
            print("✅ Photoshop connected!")
            loading.close()
            ui = MainController()
            ui.show()

        def on_failed(error_msg):
            loading.label.setText(f"❌ Unable to connect to Photoshop: {error_msg}")

        connect_thread.connected.connect(on_connected)
        connect_thread.failed.connect(on_failed)
        connect_thread.start()

        sys.exit(app.exec_())

    finally:
        # ✅ Giải phóng COM context khi thoát
        pythoncom.CoUninitialize()
