#!/usr/bin/env python3
# setup.nv.py

import os
import sys
import subprocess
import re
from pathlib import Path
import logging
import platform

# Конфігураційна секція з детальним описом параметрів
CONFIG = {
    "env_folder": "myenv",  # Назва папки для віртуального середовища
    "python_version": "3.11",  # Версія Python для створення середовища
    "files_to_scan": "main.py, modules",  # Список файлів та папок для сканування
    "entry_point": "main.py",  # Файл, який буде запущений після встановлення залежностей
    "config_output": "config_output.txt",  # Файл для запису конфігурації після виконання скрипта
    "bootstrap_dependencies": {  # Залежності, необхідні для роботи скрипта
        "requests": "2.28.1",
        "colorama": "0.4.4",
        "tqdm": "4.64.1"  # Додаємо tqdm до bootstrap залежностей для прогрес-барів
    },
}

# Налаштування логування
logging.basicConfig(
    filename='script.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(message):
    """
    Функція для логування інформаційних повідомлень.
    Виводить повідомлення в консоль та записує у файл логів.
    """
    print(f"[INFO] {message}")
    logging.info(message)

def error(message):
    """
    Функція для логування помилок.
    Виводить повідомлення в консоль, записує у файл логів та завершує виконання скрипта.
    """
    print(f"[ERROR] {message}")
    logging.error(message)
    sys.exit(1)

def write_config_output(config):
    """
    Функція для запису інформації про виконання скрипта у файл конфігурації.
    """
    with open(CONFIG["config_output"], "w") as f:
        f.write(f"Executed script. Entry point: {config['entry_point']}\n")
    log(f"Configuration output written to {CONFIG['config_output']}")

def check_folder():
    """
    Функція для перевірки наявності папки віртуального середовища.
    Якщо папка не існує, створює її.
    """
    env_path = Path(CONFIG["env_folder"])
    if env_path.exists():
        log(f"Папка середовища '{CONFIG['env_folder']}' існує.")
    else:
        log(f"Папка середовища '{CONFIG['env_folder']}' не знайдена. Створюємо...")
        env_path.mkdir(parents=True)
        log(f"Папка '{CONFIG['env_folder']}' створена.")

def get_python_executable(version):
    """
    Функція для пошуку виконуваного файлу Python з вказаною версією.
    Повертає ім'я виконавчого файлу Python або None, якщо не знайдено.
    """
    possible_names = [f"python{version}", f"python{version.replace('.', '')}", "python3", "python"]
    for name in possible_names:
        try:
            result = subprocess.run([name, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                # Перевірка версії
                ver = result.stdout.strip().split()[1]
                if ver.startswith(version):
                    return name
        except FileNotFoundError:
            continue
    return None

def install_python(version):
    """
    Функція для повідомлення про відсутність необхідної версії Python.
    """
    error(f"Python версії {version} не знайдено. Будь ласка, встановіть її вручну.")

def create_virtualenv(python_exec):
    """
    Функція для створення віртуального середовища за допомогою вказаного виконуваного файлу Python.
    """
    env_path = Path(CONFIG["env_folder"])
    if not (env_path / "Scripts" / "activate").exists() and not (env_path / "bin" / "activate").exists():
        log("Створюємо віртуальне середовище...")
        subprocess.check_call([python_exec, "-m", "venv", CONFIG["env_folder"]])
        log("Віртуальне середовище створене.")
    else:
        log("Віртуальне середовище вже існує.")

def activate_virtualenv():
    """
    Функція для активації віртуального середовища.
    Зверніть увагу, що активація в поточному скрипті не змінює середовище для подальших команд.
    Тому скрипт використовує повні шляхи до pip та python.
    """
    env_path = Path(CONFIG["env_folder"])
    if os.name == 'nt':
        activate_script = env_path / "Scripts" / "activate"
    else:
        activate_script = env_path / "bin" / "activate"
    
    if activate_script.exists():
        log("Віртуальне середовище активовано.")
    else:
        error("Скрипт активації середовища не знайдено.")

def ensure_pip(python_exec):
    """
    Функція для перевірки наявності pip у віртуальному середовищі.
    Якщо pip відсутній, встановлює його за допомогою ensurepip.
    Потім оновлює pip до останньої версії.
    """
    log("Перевіряємо наявність pip...")
    
    try:
        # Спочатку спробуємо перевірити версію pip
        subprocess.check_call([python_exec, "-m", "pip", "--version"])
        log("pip встановлений.")
    except subprocess.CalledProcessError:
        log("pip не знайдено. Підключаємо ensurepip для встановлення pip...")
        try:
            # Спробуємо використати ensurepip для встановлення pip
            subprocess.check_call([python_exec, "-m", "ensurepip"])
            log("pip успішно встановлено за допомогою ensurepip.")
        except subprocess.CalledProcessError as e:
            # Якщо ensurepip відсутній або не вдалося встановити pip, повідомимо про це
            error(f"Не вдалося встановити pip за допомогою ensurepip. Помилка: {e}")
    
    # Оновлюємо pip до останньої версії, якщо pip вже встановлений
    try:
        log("Оновлюємо pip до останньої версії...")
        subprocess.check_call([python_exec, "-m", "pip", "install", "--upgrade", "pip"])
        log("pip успішно оновлено.")
    except subprocess.CalledProcessError as e:
        error(f"Не вдалося оновити pip. Помилка: {e}")

def parse_imports(file_path):
    """
    Функція для парсингу імпортів у файлі Python.
    Повертає набір модулів, які імпортуються у файлі.
    """
    imports = set()
    import_regex = re.compile(r'^\s*(?:import|from)\s+(\S+)')
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = import_regex.match(line)
            if match:
                module = match.group(1).split('.')[0]
                if module != "__future__":
                    imports.add(module)
    return imports

def parse_files_to_scan(files_str):
    """
    Функція для парсингу рядка файлів та папок для сканування.
    Розділяє рядок за комами або пробілами, видаляє зайві пробіли.
    Додає .py до файлів, якщо його немає.
    Не додає .py до папок.
    """
    files = re.split(r'[,\s]+', files_str)
    files = [f.strip() for f in files if f.strip()]
    
    # Додаємо .py до файлів, якщо його немає, але не до папок
    for i in range(len(files)):
        path = Path(files[i])
        if path.suffix == '' and path.exists() and path.is_file():
            files[i] = str(path.with_suffix('.py'))
    
    return files

def collect_packages():
    """
    Функція для збору всіх імпортованих пакетів у вказаних файлах та папках.
    Рекурсивно сканує папки для пошуку всіх .py файлів.
    Повертає:
        set: Набір унікальних пакетів, які імпортуються у проекті.
    """
    packages = set()
    files_str = CONFIG["files_to_scan"]
    files = parse_files_to_scan(files_str)
    all_py_files = []
    
    for item in files:
        path = Path(item)
        log(f"Перевіряємо: {path}")
        if path.exists():
            if path.is_file():
                # Якщо файл без .py, додаємо .py
                if not path.suffix:
                    path = path.with_suffix('.py')
                    log(f"Додаємо розширення '.py' до файлу: {path}")
                if path.exists() and path.suffix == '.py':
                    all_py_files.append(path)
                    log(f"Додаємо файл до списку: {path}")
                elif path.exists() and path.suffix != '.py':
                    log(f"Файл '{path}' не має розширення .py і буде пропущений.")
                else:
                    error(f"Файл '{path}' не знайдено.")
            elif path.is_dir():
                log(f"Скануємо папку: {path}")
                # Рекурсивно додаємо всі .py файли в папці
                for py_file in path.rglob('*.py'):
                    all_py_files.append(py_file)
                    log(f"Додаємо файл до списку: {py_file}")
            else:
                # Якщо не файл і не папка, можливо, це файл без розширення
                path_with_ext = path.with_suffix('.py')
                if path_with_ext.exists() and path_with_ext.suffix == '.py':
                    all_py_files.append(path_with_ext)
                    log(f"Додаємо файл до списку: {path_with_ext}")
                else:
                    error(f"Файл або папка '{item}' не знайдено або не має розширення .py.")
        else:
            error(f"Файл або папка '{item}' не знайдено.")
    
    for file_path in all_py_files:
        file_packages = parse_imports(file_path)
        packages.update(file_packages)
        log(f"Знайдено пакети в '{file_path}': {file_packages}")
    
    return packages

def install_bootstrap_dependencies(python_exec):
    """
    Функція для встановлення Bootstrap залежностей.
    Перевіряє наявність кожної залежності та її версії.
    Якщо залежність відсутня або має неправильну версію, встановлює або оновлює її.
    Якщо не вдалося встановити 'tqdm', пропускає його.
    """
    log("Перевіряємо наявність Bootstrap залежностей...")
    missing = []
    for pkg, ver in CONFIG["bootstrap_dependencies"].items():
        try:
            # Перевіряємо наявність пакета та його версії
            result = subprocess.check_output([python_exec, "-m", "pip", "show", pkg], text=True)
            match = re.search(r'^Version: (\S+)', result, re.MULTILINE)
            if match:
                current_ver = match.group(1)
                if current_ver != ver:
                    log(f"Залежність '{pkg}' має версію {current_ver}, потрібна версія {ver}.")
                    missing.append(f"{pkg}=={ver}")
            else:
                missing.append(f"{pkg}=={ver}")
        except subprocess.CalledProcessError:
            # Якщо пакет не знайдено, додаємо до списку для встановлення
            missing.append(f"{pkg}=={ver}")

    if missing:
        log(f"Встановлюємо Bootstrap залежності: {missing}")
        for pkg in missing[:]:  # Створюємо копію списку для безпечної модифікації
            try:
                subprocess.check_call([python_exec, "-m", "pip", "install", pkg])
                log(f"Успішно встановлено {pkg}")
            except subprocess.CalledProcessError as e:
                log(f"Не вдалося встановити {pkg}. Помилка: {e}")
                # Пропускаємо модуль, якщо не вдалося його встановити
                if pkg.startswith("tqdm"):
                    log("Відмовляємося від модуля 'tqdm'. Продовжуємо без нього.")
                    missing.remove(pkg)
        
        if missing and not any(pkg.startswith("tqdm") for pkg in missing):
            log("Деякі Bootstrap залежності не були встановлені: " + ", ".join(missing))
        
        # Перезапускаємо скрипт після встановлення залежностей, якщо ще не перезапущений
        if "--booted" not in sys.argv:
            log("Перезапускаємо скрипт для застосування нових залежностей...")
            script_path = Path(__file__).resolve()
            subprocess.check_call([python_exec, str(script_path), "--booted"])
            sys.exit(0)
    else:
        log("Bootstrap залежності вже встановлені та оновлені.")

def install_project_dependencies(python_exec, dependencies, tqdm_available):
    """
    Функція для встановлення та оновлення проектних залежностей.
    Перевіряє наявність кожної залежності та її версії.
    Якщо залежність відсутня або має неправильну версію, встановлює або оновлює її.
    Використовує tqdm для прогрес-барів, якщо він доступний.
    """
    log("Перевіряємо наявність необхідних проектних пакетів...")
    installed_packages = subprocess.check_output([python_exec, "-m", "pip", "freeze"], text=True)
    installed = {}
    for pkg in installed_packages.splitlines():
        if '==' in pkg:
            name, ver = pkg.split('==')
            installed[name.lower()] = ver
    to_install = []
    to_upgrade = []
    
    for pkg, ver in dependencies.items():
        pkg_lower = pkg.lower()
        if pkg_lower not in installed:
            to_install.append(f"{pkg}=={ver}")
        else:
            if installed[pkg_lower] != ver:
                to_upgrade.append(f"{pkg}=={ver}")
    
    if tqdm_available:
        try:
            from tqdm import tqdm
        except ImportError:
            log("Модуль 'tqdm' не доступний. Використовуємо звичайні логування.")
            tqdm_available = False
    
    if to_install:
        if tqdm_available:
            iterator = tqdm(to_install, desc="Встановлення проектних пакетів", unit="pkg")
        else:
            iterator = to_install
        for pkg in iterator:
            if tqdm_available:
                pass  # tqdm вже показує прогрес
            log(f"Встановлюємо пакет: {pkg}")
            try:
                subprocess.check_call([python_exec, "-m", "pip", "install", pkg])
            except subprocess.CalledProcessError:
                log(f"Не вдалося встановити пакет: {pkg}")
    else:
        log("Усі необхідні пакети вже встановлені.")
    
    if to_upgrade:
        if tqdm_available:
            iterator = tqdm(to_upgrade, desc="Оновлення проектних пакетів", unit="pkg")
        else:
            iterator = to_upgrade
        for pkg in iterator:
            if tqdm_available:
                pass  # tqdm вже показує прогрес
            log(f"Оновлюємо пакет: {pkg}")
            try:
                subprocess.check_call([python_exec, "-m", "pip", "install", pkg])
            except subprocess.CalledProcessError:
                log(f"Не вдалося оновити пакет: {pkg}")
    else:
        log("Усі пакети мають необхідні версії.")
    
    # Перевірка наявності застарілих пакетів і оновлення, якщо потрібно
    outdated = get_outdated_packages(python_exec, dependencies)
    if outdated:
        if tqdm_available:
            iterator = tqdm(outdated, desc="Оновлення застарілих пакетів", unit="pkg")
        else:
            iterator = outdated
        for pkg in iterator:
            if tqdm_available:
                pass  # tqdm вже показує прогрес
            log(f"Оновлюємо застарілий пакет: {pkg}")
            try:
                subprocess.check_call([python_exec, "-m", "pip", "install", "--upgrade", pkg])
            except subprocess.CalledProcessError:
                log(f"Не вдалося оновити застарілий пакет: {pkg}")
    else:
        log("Усі пакети вже оновлені до необхідних версій.")

def get_outdated_packages(python_exec, dependencies):
    """
    Функція для отримання списку застарілих пакетів серед тих, що в dependencies.
    """
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

def install_project_dependencies_wrapper(python_exec, dependencies):
    """
    Обгортка для встановлення проектних залежностей з підтримкою tqdm.
    Перевіряє, чи доступний tqdm, і передає відповідний параметр.
    """
    try:
        from tqdm import tqdm
        tqdm_available = True
    except ImportError:
        tqdm_available = False
        log("Модуль 'tqdm' не доступний. Використовуємо звичайні логування.")
    
    install_project_dependencies(python_exec, dependencies, tqdm_available)

def run_entry_point(python_exec):
    """
    Функція для запуску файлу, вказаного як точка входу.
    """
    entry = CONFIG["entry_point"]
    entry_path = Path(entry)
    if not entry_path.exists():
        error(f"Точка входу '{entry}' не знайдена.")
    log(f"Запускаємо файл '{entry}'...")
    try:
        subprocess.check_call([python_exec, str(entry_path)])
    except subprocess.CalledProcessError as e:
        error(f"Не вдалося запустити '{entry}'. Помилка: {e}")

def main():
    """
    Головна функція скрипта.
    Визначає тип ОС, перевіряє наявність необхідної версії Python, створює віртуальне середовище,
    активує його, перевіряє Bootstrap залежності та встановлює проектні залежності.
    """
    log("Починаємо виконання скрипта...")
    
    check_folder()  # Перевіряємо наявність папки для віртуального середовища

    # Вибираємо виконуваний файл Python
    python_exec = get_python_executable(CONFIG["python_version"])
    if not python_exec:
        install_python(CONFIG["python_version"])
        python_exec = get_python_executable(CONFIG["python_version"])
        if not python_exec:
            error(f"Не вдалося знайти або встановити Python версії {CONFIG['python_version']}.")
    log(f"Використовується Python: {python_exec}")

    create_virtualenv(python_exec)  # Створюємо віртуальне середовище
    activate_virtualenv()  # Активація віртуального середовища

    ensure_pip(python_exec)  # Перевіряємо наявність pip
    install_bootstrap_dependencies(python_exec)  # Встановлюємо Bootstrap залежності

    # Збираємо пакети
    packages = collect_packages()
    log(f"Знайдені пакети: {packages}")

    # Визначаємо OS специфічні залежності
    os_type = platform.system().lower()
    log(f"Визначено тип ОС: {os_type}")
    if os_type.startswith('win'):
        os_specific_deps = {"pywin32": "305"}
    elif os_type.startswith('linux'):
        os_specific_deps = {"python-ldap": "3.3.1"}
    elif os_type.startswith('darwin'):
        os_specific_deps = {"pyobjc": "8.2.1"}
    else:
        os_specific_deps = {}
        log(f"Невідома ОС. Використовуються тільки загальні залежності.")
    
    # Збираємо повний список проектних залежностей
    project_dependencies = {
        "common": {
            "flask": "2.2.2",
            "sqlalchemy": "1.4.27"
        }
    }
    if os_specific_deps:
        project_dependencies[os_type] = os_specific_deps
    
    # Об'єднуємо загальні залежності з OS специфічними
    combined_dependencies = project_dependencies.get("common", {}).copy()
    combined_dependencies.update(os_specific_deps)
    log(f"Використовуються залежності для {os_type}: {os_specific_deps}")

    # Встановлюємо необхідні пакети
    install_project_dependencies_wrapper(python_exec, combined_dependencies)

    # Запускаємо точку входу
    run_entry_point(python_exec)

    # Записуємо конфігураційний вихід
    write_config_output({"entry_point": CONFIG["entry_point"]})

    log("Скрипт виконано успішно.")

if __name__ == "__main__":
    main()