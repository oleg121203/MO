import os
import sys
import subprocess
import logging
from pathlib import Path
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication
from install_gui import InstallWindow

# Конфігураційна секція
CONFIG = {
    "env_folder": "myenv",  
    "python_version": "3.11", 
    "bootstrap_dependencies": {  
        "requests": "2.28.1",
        "colorama": "0.4.4",
        "tqdm": "4.64.1"
    },
}

# Налаштування логування
logging.basicConfig(
    filename='script.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class InstallerThread(QThread):
    progress_signal = pyqtSignal(int)
    text_signal = pyqtSignal(str)

    def run(self):
        self.text_signal.emit("Створення віртуального середовища...")
        self.create_virtualenv()
        
        self.text_signal.emit("Перевірка та встановлення pip...")
        self.ensure_pip()
        
        self.text_signal.emit("Встановлення залежностей...")
        self.install_bootstrap_dependencies()
        
        self.text_signal.emit("Завершено.")
        self.progress_signal.emit(100)

    def create_virtualenv(self):
        env_path = Path(CONFIG["env_folder"])
        if not env_path.exists():
            subprocess.check_call([sys.executable, '-m', 'venv', str(env_path)])
        self.progress_signal.emit(20)
    
    def ensure_pip(self):
        python_exec = self.get_python_executable()
        subprocess.check_call([python_exec, "-m", "pip", "install", "--upgrade", "pip"])
        self.progress_signal.emit(40)
    
    def get_python_executable(self):
        env_path = Path(CONFIG["env_folder"])
        if os.name == 'nt':
            return env_path / "Scripts" / "python"
        else:
            return env_path / "bin" / "python"
    
    def install_bootstrap_dependencies(self):
        python_exec = self.get_python_executable()
        for pkg, ver in CONFIG["bootstrap_dependencies"].items():
            subprocess.check_call([python_exec, "-m", "pip", "install", f"{pkg}=={ver}"])
        self.progress_signal.emit(80)


def main():
    app = QApplication(sys.argv)
    window = InstallWindow()
    
    installer_thread = InstallerThread()
    installer_thread.progress_signal.connect(window.update_progress)
    installer_thread.text_signal.connect(window.update_text)
    
    installer_thread.start()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()