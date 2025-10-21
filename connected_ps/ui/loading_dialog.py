from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
from PyQt5.QtGui import QMovie, QIcon, QPainterPath, QRegion, QPainter, QColor, QBrush, QPixmap
from PyQt5.QtCore import Qt, QSize, QRectF
import os
from dotenv import load_dotenv
load_dotenv()
class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WindowSystemMenuHint |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "resources", "app_icon.ico")
        gif_path = os.path.join(base_dir, "resources", "loading_spinner.gif")
        image_path = os.path.join(base_dir, "resources", "photoshop_logo.png")  # 🖼️ thêm ảnh của bạn ở đây

        self.setWindowIcon(QIcon(icon_path))
        self.setModal(True)
        self.setFixedSize(320, 260)
        self.radius = 20

        # 💫 Hiệu ứng bóng đổ nhẹ
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)

        # 🧱 Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        # Spacer trên
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 🖼️ Hình ảnh trên cùng
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        self.image_label.setStyleSheet("margin-bottom: 5px;")
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # 🌀 GIF loading
        self.spinner = QLabel()
        self.spinner.setAlignment(Qt.AlignCenter)
        self.movie = QMovie(gif_path)
        self.movie.setScaledSize(QSize(48, 48))
        self.spinner.setMovie(self.movie)
        self.movie.start()
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        # 🔤 Text
        self.label = QLabel("Connecting to Photoshop...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #cccccc; font-size: 15px;")
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        
        # 🧾 Version text (tự động từ .env)
        version = os.getenv("APP_VERSION", "v1.0.0")  # đọc version từ file .env, mặc định v1.0.0 nếu không có
        self.version_label = QLabel(f"ExrToPSB {version}")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("color: #999999; font-size: 13px; font-style: italic;")
        layout.addWidget(self.version_label, alignment=Qt.AlignCenter)


        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(layout)

    def paintEvent(self, event):
        """Vẽ nền bo tròn hoàn toàn"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), self.radius, self.radius)
        painter.fillPath(path, QBrush(QColor("#2b2b2b")))
        painter.setPen(QColor("#3a3a3a"))
        painter.drawPath(path)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
