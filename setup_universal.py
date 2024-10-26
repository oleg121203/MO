#!/usr/bin/env python3
# setup_universal.py

import sys
import subprocess
import os
import re
from pathlib import Path
import logging
import platform
import ast
from pathlib import Path
import subprocess
import sys
import os
from pathlib import Path

CONFIG = {
        "env_folder": "myenv",  # Назва папки для віртуального середовища
        "python_version": "3.11",  # Версія Python для створення середовища
        "files_to_scan": "main.py modules",  # Список файлів та папок для сканування
        "entry_point": "main.py",  # Файл, який буде запущений після встановлення залежностей
        "config_output": "config_output.txt",  # Файл для запису конфігурації після виконання скрипта
        "bootstrap_dependencies": {  # Залежності, необхідні для роботи скрипта
            "requests": "2.28.1",
            "colorama": "0.4.4",
            "tqdm": "4.64.1",  # Додаємо tqdm до bootstrap залежностей для прогрес-барів
            "stdlib-list": "0.8.0",  # Додаємо stdlib-list для визначення стандартних бібліотек
            "PyQt6": "6.5.0"  # Додаємо PyQt6 з конкретною версією
        },
        "local_packages": ["modules"]  # Список локальних пакетів для виключення
    }

def create_and_activate_venv():
            env_path = Path('myenv')
            if not env_path.exists():
                subprocess.check_call([sys.executable, '-m', 'venv', str(env_path)])
                print("Віртуальне середовище створено.")

            # Зберігаємо шлях до інтерпретатора у віртуальному середовищі
            venv_python = env_path / 'bin' / 'python' if os.name != 'nt' else env_path / 'Scripts' / 'python'
            return venv_python

def install_packages(venv_python):
            packages = [
                "requests==2.28.1", 
                "colorama==0.4.4", 
                "tqdm==4.64.1", 
                "stdlib-list==0.8.0", 
                "PyQt6==6.5.0"
            ]
            try:
                # Встановлення пакетів безпосередньо через віртуальне середовище
                subprocess.check_call([str(venv_python), '-m', 'pip', 'install'] + packages)
                print("Усі пакети успішно встановлено.")
            except subprocess.CalledProcessError as e:
                print(f"Помилка при встановленні пакетів: {e}")

def main():
            venv_python = create_and_activate_venv()
            install_packages(venv_python)

if __name__ == "__main__":
            main()
    
            

def main():
    # Створення віртуального середовища, якщо потрібно
    env_dir = "./venv"
    if not os.path.exists(env_dir):
        print("Створюємо віртуальне середовище...")
        subprocess.check_call([sys.executable, '-m', 'venv', env_dir])

    # Активація віртуального середовища
    activate_script = f"{env_dir}/bin/activate_this.py" if os.name != 'nt' else f"{env_dir}\\Scripts\\activate_this.py"
    with open(activate_script) as file:
        exec(file.read(), dict(__file__=activate_script))

    # Встановлення необхідних пакетів
    install_packages()

if __name__ == "__main__":
    main()

def create_and_activate_venv():
    env_path = Path('myenv')
    if not env_path.exists():
        subprocess.check_call([sys.executable, '-m', 'venv', 'myenv'])
    activate_script = env_path / 'bin' / 'activate_this.py'
    if activate_script.exists():
        exec(open(str(activate_script)).read(), {'__file__': str(activate_script)})
    else:
        print("Неможливо активувати віртуальне середовище.")

create_and_activate_venv()
# Далі йде ваш код для встановлення пакетів...
# Конфігураційна секція з детальним описом параметрів



def install(package):
    """Функція для встановлення пакету через pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_packages():
    """Перевіряє наявність необхідних пакетів і встановлює відсутні."""
    try:
        from importlib import metadata
    except ImportError:
        # Для Python <3.8 можна встановити importlib-metadata
        install("importlib-metadata")
        from importlib import metadata

    required = CONFIG["bootstrap_dependencies"].keys()
    installed = {dist.metadata["Name"].lower(): dist.version for dist in metadata.distributions()}
    missing = []
    for pkg, ver in CONFIG["bootstrap_dependencies"].items():
        pkg_lower = pkg.lower()
        if pkg_lower not in installed:
            if ver:
                missing.append(f"{pkg}=={ver}")
            else:
                missing.append(pkg)
        else:
            if ver and installed[pkg_lower] != ver:
                missing.append(f"{pkg}=={ver}")

    if missing:
        print(f"Встановлюємо відсутні пакети: {missing}")
        for pkg in missing:
            try:
                install(pkg)
                logging.info(f"Успішно встановлено пакет: {pkg}")
            except subprocess.CalledProcessError as e:
                logging.error(f"Не вдалося встановити пакет: {pkg}. Помилка: {e}")
                print(f"[ERROR] Не вдалося встановити пакет: {pkg}. Перевірте лог для деталей.")
                sys.exit(1)
        # Перезапускаємо скрипт після встановлення пакетів
        print("Перезапускаємо скрипт для використання встановлених пакетів...")
        python = sys.executable
        os.execl(python, python, * sys.argv)
    else:
        logging.info("Всі Bootstrap залежності вже встановлені та оновлені.")
        print("Всі Bootstrap залежності вже встановлені та оновлені.")

# Виконуємо перевірку і встановлення необхідних пакетів
check_and_install_packages()

# Після цього імпортуємо встановлені пакети
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QProgressBar, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class InstallerThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def run(self):
        try:
            self.log_signal.emit("Починаємо виконання скрипта...")
            self.check_folder()
            python_exec = self.get_python_executable(CONFIG["python_version"])
            if not python_exec:
                self.install_python(CONFIG["python_version"])
                python_exec = self.get_python_executable(CONFIG["python_version"])
                if not python_exec:
                    self.error(f"Не вдалося знайти або встановити Python версії {CONFIG['python_version']}.")
            self.log(f"Використовується Python: {python_exec}")
            self.progress_signal.emit(10)

            self.create_virtualenv(python_exec)
            self.progress_signal.emit(20)

            self.ensure_pip(python_exec)
            self.progress_signal.emit(30)

            self.install_bootstrap_dependencies(python_exec)
            self.progress_signal.emit(40)

            packages = self.collect_packages()
            self.log(f"Знайдені пакети: {packages}")
            self.progress_signal.emit(50)

            os_type = platform.system().lower()
            self.log(f"Визначено тип ОС: {os_type}")
            if os_type.startswith('win'):
                os_specific_deps = {"pywin32": "305"}
            elif os_type.startswith('linux'):
                os_specific_deps = {"python-ldap": "3.3.1"}
            elif os_type.startswith('darwin'):
                os_specific_deps = {"pyobjc": "8.2"}  # Виправлена версія pyobjc
            else:
                os_specific_deps = {}
                self.log(f"Невідома ОС. Використовуються тільки загальні залежності.")

            project_dependencies = {
                "common": {
                    "flask": "2.2.2",
                    "sqlalchemy": "1.4.27",
                    "PyQt6": "6.5.0"  # Додаємо PyQt6 з конкретною версією
                }
            }
            if os_specific_deps:
                project_dependencies[os_type] = os_specific_deps

            combined_dependencies = project_dependencies.get("common", {}).copy()
            combined_dependencies.update(os_specific_deps)
            self.log(f"Використовуються залежності для {os_type}: {os_specific_deps}")
            self.progress_signal.emit(60)

            for pkg in packages:
                if pkg.lower() not in [k.lower() for k in combined_dependencies.keys()]:
                    combined_dependencies[pkg] = None  # Не вказуємо конкретну версію
            self.log(f"Повний список залежностей для встановлення: {combined_dependencies}")
            self.progress_signal.emit(65)

            self.install_project_dependencies_wrapper(python_exec, combined_dependencies)
            self.progress_signal.emit(85)

            self.run_entry_point(python_exec)
            self.write_config_output({"entry_point": CONFIG["entry_point"]})
            self.progress_signal.emit(95)

            self.log("Скрипт виконано успішно.")
            self.log("\n[INFO] Для активації віртуального середовища, виконайте наступну команду:")
            if os.name == 'nt':
                self.log("    .\\myenv\\Scripts\\Activate.ps1  # Для PowerShell")
                self.log("    myenv\\Scripts\\activate.bat  # Для Command Prompt")
            else:
                self.log("    source myenv/bin/activate  # Для macOS та Linux")
            self.progress_signal.emit(100)

        except Exception as e:
            self.error(str(e))
        finally:
            self.finished_signal.emit()

    def log(self, message):
        self.log_signal.emit(message)
        logging.info(message)

    def error(self, message):
        self.log_signal.emit(f"[ERROR] {message}")
        logging.error(message)
        # Не завершуємо потік тут, щоб GUI залишався відкритим для перегляду помилок

    def check_folder(self):
        env_path = Path(CONFIG["env_folder"])
        if env_path.exists():
            self.log(f"Папка середовища '{CONFIG['env_folder']}' існує.")
        else:
            self.log(f"Папка середовища '{CONFIG['env_folder']}' не знайдена. Створюємо...")
            env_path.mkdir(parents=True)
            self.log(f"Папка '{CONFIG['env_folder']}' створена.")

    def get_python_executable(self, version):
        possible_names = [f"python{version}", f"python{version.replace('.', '')}", "python3", "python"]
        for name in possible_names:
            try:
                result = subprocess.run([name, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    ver = result.stdout.strip().split()[1]
                    if ver.startswith(version):
                        return name
            except FileNotFoundError:
                continue
        return None

    def install_python(self, version):
        self.error(f"Python версії {version} не знайдено. Будь ласка, встановіть її вручну.")
        # Можливо, додати посилання на офіційний сайт Python для завантаження

    def create_virtualenv(self, python_exec):
        env_path = Path(CONFIG["env_folder"])
        activate_path = env_path / "Scripts" / "activate" if os.name == 'nt' else env_path / "bin" / "activate"
        if not activate_path.exists():
            self.log("Створюємо віртуальне середовище...")
            subprocess.check_call([python_exec, "-m", "venv", CONFIG["env_folder"]])
            self.log("Віртуальне середовище створене.")
        else:
            self.log("Віртуальне середовище вже існує.")

    def ensure_pip(self, python_exec):
        self.log("Перевіряємо наявність pip...")
        try:
            subprocess.check_call([python_exec, "-m", "pip", "--version"])
            self.log("pip встановлений.")
        except subprocess.CalledProcessError:
            self.log("pip не знайдено. Встановлюємо pip...")
            subprocess.check_call([python_exec, "-m", "ensurepip"])
        self.log("Оновлюємо pip до останньої версії...")
        subprocess.check_call([python_exec, "-m", "pip", "install", "--upgrade", "pip"])
        self.progress_signal.emit(35)

    def parse_imports(self, file_path):
        imports = set()
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                node = ast.parse(f.read(), filename=file_path)
                for stmt in node.body:
                    if isinstance(stmt, ast.Import):
                        for alias in stmt.names:
                            module = alias.name.split('.')[0]
                            if module != "__future__":
                                imports.add(module)
                    elif isinstance(stmt, ast.ImportFrom):
                        if stmt.module:
                            module = stmt.module.split('.')[0]
                            if module != "__future__":
                                imports.add(module)
            except SyntaxError as e:
                self.log(f"Syntax error while parsing {file_path}: {e}")
        return imports

    def parse_files_to_scan(self, files_str):
        files = re.split(r'[,\s]+', files_str)
        files = [f.strip() for f in files if f.strip()]
        for i in range(len(files)):
            path = Path(files[i])
            if path.suffix == '' and path.exists() and path.is_file():
                files[i] = str(path.with_suffix('.py'))
        return files

    def collect_packages(self):
        packages = set()
        files_str = CONFIG["files_to_scan"]
        files = self.parse_files_to_scan(files_str)
        all_py_files = []
        
        for item in files:
            path = Path(item)
            self.log(f"Перевіряємо: {path}")
            if path.exists():
                if path.is_file():
                    if not path.suffix:
                        path = path.with_suffix('.py')
                        self.log(f"Додаємо розширення '.py' до файлу: {path}")
                    if path.exists() and path.suffix == '.py':
                        all_py_files.append(path)
                        self.log(f"Додаємо файл до списку: {path}")
                    elif path.exists() and path.suffix != '.py':
                        self.log(f"Файл '{path}' не має розширення .py і буде пропущений.")
                    else:
                        self.error(f"Файл '{path}' не знайдено.")
                elif path.is_dir():
                    self.log(f"Скануємо папку: {path}")
                    for py_file in path.rglob('*.py'):
                        all_py_files.append(py_file)
                        self.log(f"Додаємо файл до списку: {py_file}")
                else:
                    path_with_ext = path.with_suffix('.py')
                    if path_with_ext.exists() and path_with_ext.suffix == '.py':
                        all_py_files.append(path_with_ext)
                        self.log(f"Додаємо файл до списку: {path_with_ext}")
                    else:
                        self.error(f"Файл або папка '{item}' не знайдено або не має розширення .py.")
            else:
                self.error(f"Файл або папка '{item}' не знайдено.")
        
        for file_path in all_py_files:
            file_packages = self.parse_imports(file_path)
            packages.update(file_packages)
            self.log(f"Знайдено пакети в '{file_path}': {file_packages}")
        
        # Виключаємо локальні пакети
        packages = packages - set(CONFIG["local_packages"])
        self.log(f"Зібрані пакети після виключення локальних: {packages}")
        
        return packages

    def install_bootstrap_dependencies(self, python_exec):
        self.log("Перевіряємо наявність Bootstrap залежностей...")
        missing = []
        for pkg, ver in CONFIG["bootstrap_dependencies"].items():
            try:
                result = subprocess.check_output([python_exec, "-m", "pip", "show", pkg], text=True)
                match = re.search(r'^Version: (\S+)', result, re.MULTILINE)
                if match:
                    current_ver = match.group(1)
                    if ver is not None and current_ver != ver:
                        self.log(f"Залежність '{pkg}' має версію {current_ver}, потрібна версія {ver}.")
                        missing.append(f"{pkg}=={ver}")
                else:
                    if ver is not None:
                        missing.append(f"{pkg}=={ver}")
                    else:
                        missing.append(pkg)
            except subprocess.CalledProcessError:
                if ver is not None:
                    missing.append(f"{pkg}=={ver}")
                else:
                    missing.append(pkg)
        
        if missing:
            self.log(f"Встановлюємо Bootstrap залежності: {missing}")
            for pkg in missing[:]:
                try:
                    subprocess.check_call([python_exec, "-m", "pip", "install", pkg])
                    self.log(f"Успішно встановлено {pkg}")
                except subprocess.CalledProcessError as e:
                    self.log(f"Не вдалося встановити {pkg}. Помилка: {e}")
                    if pkg.startswith("tqdm"):
                        self.log("Відмовляємося від модуля 'tqdm'. Продовжуємо без нього.")
                        missing.remove(pkg)
            
            if missing and not any(pkg.startswith("tqdm") for pkg in missing):
                self.log("Деякі Bootstrap залежності не були встановлені: " + ", ".join(missing))
            
            if "--booted" not in sys.argv:
                self.log("Перезапускаємо скрипт для застосування нових залежностей...")
                script_path = Path(__file__).resolve()
                subprocess.check_call([python_exec, str(script_path), "--booted"])
                sys.exit(0)
        else:
            self.log("Bootstrap залежності вже встановлені та оновлені.")

    def install_project_dependencies(self, python_exec, dependencies, stdlib_modules, tqdm_available):
        self.log("Перевіряємо наявність необхідних проектних пакетів...")
        installed = {}
        try:
            from importlib import metadata
        except ImportError:
            install("importlib-metadata")
            from importlib import metadata

        for dist in metadata.distributions():
            name = dist.metadata["Name"].lower()
            version = dist.version
            installed[name] = version

        to_install = []
        to_upgrade = []
        
        for pkg, ver in dependencies.items():
            pkg_lower = pkg.lower()
            if pkg_lower in stdlib_modules:
                self.log(f"Залежність '{pkg}' є стандартною бібліотекою Python або локальним пакетом. Пропускаємо.")
                continue
            if pkg_lower not in installed:
                if ver:
                    to_install.append(f"{pkg}=={ver}")
                else:
                    to_install.append(pkg)
            else:
                if ver and installed[pkg_lower] != ver:
                    to_upgrade.append(f"{pkg}=={ver}")

        if to_install:
            self.log(f"Встановлюємо пакети: {to_install}")
            for pkg in to_install:
                try:
                    subprocess.check_call([python_exec, "-m", "pip", "install", pkg])
                    self.progress_signal.emit(70)
                except subprocess.CalledProcessError:
                    self.log(f"Не вдалося встановити пакет: {pkg}")
        
        if to_upgrade:
            self.log(f"Оновлюємо пакети: {to_upgrade}")
            for pkg in to_upgrade:
                try:
                    subprocess.check_call([python_exec, "-m", "pip", "install", pkg])
                    self.progress_signal.emit(80)
                except subprocess.CalledProcessError:
                    self.log(f"Не вдалося оновити пакет: {pkg}")
        else:
            self.log("Усі пакети мають необхідні версії.")
        
        # Перевірка застарілих пакетів
        outdated = self.get_outdated_packages(python_exec, dependencies)
        if outdated:
            self.log(f"Оновлюємо застарілі пакети: {outdated}")
            for pkg in outdated:
                try:
                    subprocess.check_call([python_exec, "-m", "pip", "install", "--upgrade", pkg])
                    self.progress_signal.emit(90)
                except subprocess.CalledProcessError:
                    self.log(f"Не вдалося оновити застарілий пакет: {pkg}")
        else:
            self.log("Усі пакети вже оновлені до необхідних версій.")

    def get_outdated_packages(self, python_exec, dependencies):
        result = subprocess.check_output([python_exec, "-m", "pip", "list", "--outdated"], text=True)
        outdated = []
        lines = result.splitlines()
        for line in lines[2:]:  # Пропускаємо заголовки
            parts = line.split()
            if len(parts) >= 1:
                pkg = parts[0]
                pkg_lower = pkg.lower()
                if pkg_lower in [k.lower() for k in dependencies.keys()]:
                    outdated.append(pkg)
        return outdated

    def install_project_dependencies_wrapper(self, python_exec, dependencies):
        try:
            from tqdm import tqdm
            tqdm_available = True
        except ImportError:
            tqdm_available = False
            self.log("Модуль 'tqdm' не доступний. Використовуємо звичайні логування.")
        
        try:
            from stdlib_list import stdlib_list
            stdlib_modules = set(stdlib_list(sys.version[:3]))
        except ImportError:
            self.log("Модуль 'stdlib-list' не встановлено. Використовуємо обмежений список стандартних модулів.")
            stdlib_modules = {
                'sys', 'os', 'json', 'logging', 'traceback', 'functools', 'datetime',
                'asyncio', 'typing', 'bs4', 'pandas', 'qasync', 'telethon'
            }
        
        # Додаємо локальні пакети до списку стандартних для виключення
        stdlib_modules.update([pkg.lower() for pkg in CONFIG["local_packages"]])
        
        # Додатково додаємо відсутні стандартні бібліотеки вручну
        additional_stdlib = [
            'logging', 'json', 'sys', 'os', 'functools', 'asyncio', 
            'typing', 'traceback', 'datetime', 'subprocess'
        ]
        stdlib_modules.update([pkg.lower() for pkg in additional_stdlib])
        
        # Додаткове логування для перевірки stdlib_modules
        self.log(f"Standard library modules: {stdlib_modules}")
        
        self.install_project_dependencies(python_exec, dependencies, stdlib_modules, tqdm_available)

    def run_entry_point(self, python_exec):
        entry = CONFIG["entry_point"]
        entry_path = Path(entry)
        if not entry_path.exists():
            self.error(f"Точка входу '{entry}' не знайдена.")
        self.log(f"Запускаємо файл '{entry}'...")
        try:
            subprocess.check_call([python_exec, str(entry_path)])
        except subprocess.CalledProcessError as e:
            self.error(f"Не вдалося запустити '{entry}'. Помилка: {e}")

    def write_config_output(self, config):
        with open(CONFIG["config_output"], "w") as f:
            f.write(f"Executed script. Entry point: {config['entry_point']}\n")
        self.log(f"Configuration output written to {CONFIG['config_output']}")

class SetupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal Setup Installer")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        self.init_thread()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Верхня частина: прогрес-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Нижня частина: перелік встановлених файлів
        self.log_list = QListWidget()
        main_layout.addWidget(self.log_list)
        
        central_widget.setLayout(main_layout)
    
    def init_thread(self):
        self.installer_thread = InstallerThread()
        self.installer_thread.log_signal.connect(self.update_log)
        self.installer_thread.progress_signal.connect(self.update_progress)
        self.installer_thread.finished_signal.connect(self.on_finished)
        self.installer_thread.start()

    def update_log(self, message):
        item = QListWidgetItem(message)
        self.log_list.addItem(item)
        self.log_list.scrollToBottom()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_finished(self):
        self.log_list.addItem(QListWidgetItem("Встановлення завершено."))
        self.progress_bar.setValue(100)

def main_gui():
    app = QApplication(sys.argv)
    window = SetupWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main_gui()