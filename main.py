import sys
import asyncio
import logging
import tracemalloc
from PyQt6.QtWidgets import QApplication, QMessageBox
from modules.config_manager import ConfigManager
from modules.mdb1_database import Database
from modules.mt1_telegram import Telegram
from modules.gui import ConfigGUI, MainWindow
import qasync

# Запуск отслеживания использования памяти (опционально)
tracemalloc.start()

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Создаём приложение PyQt6 с qasync
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    async def run():
        try:
            # Загрузка конфигурации
            config_manager = ConfigManager()
            config_exists = config_manager.load_config()

            # Если конфигурации нет или она неполная, открываем GUI для ввода данных
            if not config_exists or not config_manager.is_config_complete():
                config_gui = ConfigGUI(config_manager)
                config_gui.run()
                # После закрытия ConfigGUI, повторно загружаем конфигурацию
                config_manager.load_config()
                if not config_manager.is_config_complete():
                    QMessageBox.critical(None, "Ошибка", "Конфигурация не была заполнена корректно. Приложение будет закрыто.")
                    sys.exit(1)

            # Инициализируем модули базы данных и Telegram с конфигурацией
            db_config = {
                'path': config_manager.config.get('database', {}).get('path', 'app_database.db')
            }
            tg_config = config_manager.config.get('telegram', {})

            db_module = DatabaseModule(config=db_config)
            telegram_module = TelegramModule(
                api_id=int(tg_config.get('api_id')),
                api_hash=tg_config.get('api_hash'),
                phone_number=tg_config.get('phone_number')
            )

            # Инициализация базы данных
            init_success = await db_module.initialize()
            if not init_success:
                QMessageBox.critical(None, "Ошибка", "Не удалось инициализировать базу данных. Приложение будет закрыто.")
                sys.exit(1)

            # Проверка подключения к базе данных
            db_connected = await db_module.is_connected()

            # Создаём главное окно
            main_window = MainWindow(
                db_module=db_module,
                telegram_module=telegram_module,
                db_connected=db_connected,  # Статус подключения к базе данных
                tg_connected=False,  # Пока подключение к Telegram не установлено
                config_manager=config_manager
            )
            main_window.show()

            # Подключаем сигнал aboutToQuit к асинхронному методу очистки
            app.aboutToQuit.connect(lambda: asyncio.create_task(main_window.on_about_to_quit()))

            # Запускаем подключение к Telegram
            asyncio.create_task(main_window.connect_to_telegram())

        except Exception as e:
            logging.exception("Произошла неожиданная ошибка:")
            QMessageBox.critical(None, "Ошибка", f"Произошла неожиданная ошибка: {e}")
            sys.exit(1)

    # Запускаем асинхронную функцию run в рамках установленной петли событий
    loop.create_task(run())

    # Запускаем цикл событий
    with loop:
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            logging.info("Приложение прервано пользователем.")
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

if __name__ == "__main__":
    main()