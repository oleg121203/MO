import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt6.QtCore import Qt

class InstallWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Налаштування інтерфейсу
        self.setWindowTitle("Installation Progress")
        self.setGeometry(100, 100, 600, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Напівпрозорий інтерфейс
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Основний віджет
        widget = QWidget()
        layout = QVBoxLayout()

        # Тулбар (заголовок)
        self.label = QLabel("Installation in Progress...")
        self.label.setStyleSheet("font-size: 20px; color: white;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Прогрес-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar { color: white; }")

        # Бігучий рядок
        self.running_text = QLabel("Installing dependencies... Please wait.")
        self.running_text.setStyleSheet("font-size: 16px; color: white;")
        self.running_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Додаємо елементи до layout
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.running_text)
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_text(self, message):
        self.running_text.setText(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InstallWindow()
    window.show()
    sys.exit(app.exec())