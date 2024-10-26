import os
import subprocess
import time
import logging
from pathlib import Path
import argparse
import sys
import shutil

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("setup.log", mode='a', encoding='utf-8')
    ]
)

# Конфігурація
CONFIG = {
    "env_folder": "venv",
    "python_version": "3.12",  # Наприклад, "3.8"
    "files_to_scan": ["main.py", "modules"],
    "entry_point": "main.py",
    "config_output": "config_output.txt",
    "bootstrap_dependencies": {
        "pipreqs": "0.4.11"  # Додано pipreqs для автоматичного визначення залежностей
    }
}

def parse_arguments():
    parser = argparse.ArgumentParser(description='Автоматизація налаштування середовища Python')
    parser.add_argument('--env-folder', default=CONFIG['env_folder'], help='Папка віртуального середовища')
    parser.add_argument('--python-version', default=CONFIG['python_version'], help='Версія Python для віртуального середовища (наприклад, "3.8")')
    parser.add_argument('--files-to-scan', default=','.join(CONFIG['files_to_scan']), help='Файли та папки для сканування, через кому')
    parser.add_argument('--entry-point', default=CONFIG['entry_point'], help='Точка входу додатка')
    parser.add_argument('--config-output', default=CONFIG['config_output'], help='Файл для виводу конфігурації')
    parser.add_argument('--bootstrap-dependencies', default=','.join([f"{k}=={v}" for k, v in CONFIG['bootstrap_dependencies'].items()]),
                        help='Початкові залежності для встановлення, формат: пакет==версія, через кому')
    return parser.parse_args()

def update_config(args):
    CONFIG['env_folder'] = args.env_folder
    CONFIG['python_version'] = args.python_version
    CONFIG['files_to_scan'] = [f.strip() for f in args.files_to_scan.split(',')]
    CONFIG['entry_point'] = args.entry_point
    CONFIG['config_output'] = args.config_output
    dependencies = {}
    for dep in args.bootstrap_dependencies.split(','):
        if '==' in dep:
            pkg, ver = dep.split('==')
            dependencies[pkg.strip()] = ver.strip()
        else:
            dependencies[dep.strip()] = None
    CONFIG['bootstrap_dependencies'] = dependencies

def get_pip_command():
    if os.name == 'nt':
        pip_path = Path(CONFIG['env_folder']) / 'Scripts' / 'pip.exe'
    else:
        pip_path = Path(CONFIG['env_folder']) / 'bin' / 'pip'
    return str(pip_path)

def get_python_command():
    if os.name == 'nt':
        python_path = Path(CONFIG['env_folder']) / 'Scripts' / 'python.exe'
    else:
        python_path = Path(CONFIG['env_folder']) / 'bin' / 'python'
    return str(python_path)

def get_pipreqs_command():
    if os.name == 'nt':
        pipreqs_path = Path(CONFIG['env_folder']) / 'Scripts' / 'pipreqs.exe'
    else:
        pipreqs_path = Path(CONFIG['env_folder']) / 'bin' / 'pipreqs'
    return str(pipreqs_path)

def find_python_executable(version):
    """
    Спроба знайти Python з вказаною версією у системі.
    """
    logging.info(f"Шукаємо Python версії {version} у системі.")
    if os.name == 'nt':
        # На Windows шукаємо 'python{version}.exe' у PATH
        executable = f'python{version}.exe'
    else:
        # На Unix-подібних системах шукаємо 'python{version}'
        executable = f'python{version}'
    
    python_path = shutil.which(executable)
    if python_path:
        logging.info(f"Знайдено Python: {python_path}")
        return python_path
    else:
        logging.error(f"Python версії {version} не знайдено у PATH.")
        return None

def create_virtual_env():
    env_path = Path(CONFIG['env_folder'])
    if not env_path.exists():
        logging.info(f"Створення віртуального середовища в {CONFIG['env_folder']}")
        try:
            if CONFIG['python_version']:
                python_executable = find_python_executable(CONFIG['python_version'])
                if not python_executable:
                    logging.error(f"Не вдалося знайти Python версії {CONFIG['python_version']}. Будь ласка, встановіть його перед запуском скрипта.")
                    sys.exit(1)
                subprocess.run([python_executable, '-m', 'venv', CONFIG['env_folder']], check=True)
            else:
                subprocess.run([sys.executable, '-m', 'venv', CONFIG['env_folder']], check=True)
            logging.info("Віртуальне середовище створено.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Помилка при створенні віртуального середовища: {e}")
            sys.exit(1)
    else:
        logging.info("Віртуальне середовище вже існує.")

def install_bootstrap_dependencies():
    """
    Встановлює початкові залежності, необхідні для подальшого налаштування, такі як pipreqs.
    """
    logging.info("Відлік до інсталяції початкових залежностей: 5 секунд")
    time.sleep(5)
    logging.info("ІНСТАЛЮЄМО ПОЧАТКОВІ ЗАЛЕЖНОСТІ:")

    pip_command = get_pip_command()
    if not Path(pip_command).exists():
        logging.error(f"Pip не знайдено за шляхом: {pip_command}")
        sys.exit(1)

    # Створення requirements_bootstrap.txt
    bootstrap_requirements_file = Path('requirements_bootstrap.txt')
    with bootstrap_requirements_file.open('w', encoding='utf-8') as f:
        for pkg, ver in CONFIG['bootstrap_dependencies'].items():
            if ver:
                f.write(f"{pkg}=={ver}\n")
            else:
                f.write(f"{pkg}\n")

    # Встановлення початкових залежностей
    try:
        subprocess.run([pip_command, 'install', '-r', str(bootstrap_requirements_file)], check=True)
        logging.info("Початкові залежності успішно встановлені.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Помилка при встановленні початкових залежностей: {e}")
        sys.exit(1)
    finally:
        # Видалення requirements_bootstrap.txt після встановлення
        if bootstrap_requirements_file.exists():
            bootstrap_requirements_file.unlink()

    # Перевірка встановлення pipreqs
    pipreqs_command = get_pipreqs_command()
    if not Path(pipreqs_command).exists():
        logging.error("pipreqs не вдалося встановити у віртуальному середовищі.")
        sys.exit(1)
    else:
        logging.info("pipreqs встановлено успішно.")

def generate_requirements():
    """
    Використовує pipreqs для автоматичного генераування requirements.txt на основі імпортів у коді.
    """
    logging.info("Генеруємо requirements.txt за допомогою pipreqs.")
    pipreqs_command = get_pipreqs_command()
    if not Path(pipreqs_command).exists():
        logging.error(f"pipreqs не знайдено за шляхом: {pipreqs_command}")
        sys.exit(1)
    
    try:
        subprocess.run([pipreqs_command, '--force', '--ignore', 'venv'], check=True)
        with open('requirements.txt', 'w') as f:
            f.write(subprocess.check_output([pipreqs_command, '--force', '--ignore', 'venv']))
        logging.info("requirements.txt успішно zgенеровано.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Помилка при генерації requirements.txt: {e}")
        sys.exit(1)

def install_dependencies():
    """
    Встановлює залежності згенерованого requirements.txt.
    """
    logging.info("Відлік до інсталяції залежностей: 5 секунд")
    time.sleep(5)
    logging.info("ІНСТАЛЮЄМО ЗАЛЕЖНОСТІ:")

    pip_command = get_pip_command()
    if not Path(pip_command).exists():
        logging.error(f"Pip не знайдено за шляхом: {pip_command}")
        sys.exit(1)

    requirements_file = Path('requirements.txt')
    if not requirements_file.exists():
        logging.error("requirements.txt не знайдено. Переконайтеся, що pipreqs успішно згенерував файл.")
        sys.exit(1)

    # Встановлення залежностей
    try:
        subprocess.run([pip_command, 'install', '-r', str(requirements_file)], check=True)
        logging.info("Залежності успішно встановлені.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Помилка при встановленні залежностей: {e}")
        sys.exit(1)

def check_missing_dependencies():
    """
    Перевіряє, чи всі залежності встановлені. Якщо ні, завершує скрипт з помилкою.
    """
    try:
        import pkg_resources
        from pkg_resources import DistributionNotFound, VersionConflict

        requirements_file = Path('requirements.txt')
        if not requirements_file.exists():
            logging.warning("requirements.txt не знайдено. Пропускаємо перевірку залежностей.")
            return

        with requirements_file.open('r') as f:
            requirements = f.read().splitlines()

        pkg_resources.require(requirements)
        logging.info("Усі залежності встановлені.")
    except (DistributionNotFound, VersionConflict) as e:
        logging.error(f"Відсутні або несумісні залежності: {e}")
        sys.exit(1)

def run_entry_point():
    entry_point = Path(CONFIG['entry_point'])
    if not entry_point.exists():
        logging.error(f"Точка входу {CONFIG['entry_point']} не знайдена.")
        sys.exit(1)

    python_command = get_python_command()
    if not Path(python_command).exists():
        logging.error(f"Python не знайдено за шляхом: {python_command}")
        sys.exit(1)

    logging.info(f"Запуск основного додатка: {CONFIG['entry_point']}")
    try:
        subprocess.run([python_command, str(entry_point)], check=True)
        logging.info("Додаток успішно запущено.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Помилка при запуску додатка: {e}")
        sys.exit(1)

def scan_files():
    # Приклад функції для сканування файлів
    logging.info("Сканування файлів:")
    for file in CONFIG['files_to_scan']:
        path = Path(file)
        if path.exists():
            if path.is_file():
                logging.info(f"Знайдено файл: {file}")
            elif path.is_dir():
                logging.info(f"Знайдено директорію: {file}")
            else:
                logging.warning(f"Невідомий тип: {file}")
        else:
            logging.warning(f"Не знайдено: {file}")

def save_config():
    config_output = Path(CONFIG['config_output'])
    try:
        with config_output.open('w', encoding='utf-8') as f:
            for key, value in CONFIG.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                elif isinstance(value, dict):
                    value = ', '.join([f"{k}=={v}" for k, v in value.items() if v])
                f.write(f"{key}: {value}\n")
        logging.info(f"Конфігурація збережена у {CONFIG['config_output']}")
    except Exception as e:
        logging.error(f"Помилка при збереженні конфігурації: {e}")

def main():
    args = parse_arguments()
    update_config(args)

    save_config()
    create_virtual_env()
    install_bootstrap_dependencies()
    generate_requirements()
    install_dependencies()
    check_missing_dependencies()  # Додано перевірку залежностей
    scan_files()
    run_entry_point()

if __name__ == "__main__":
    main()
