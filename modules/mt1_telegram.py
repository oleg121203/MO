from telethon import errors, functions, types
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import (
from modules.mt1_telegram import TelegramModule
        'telegram_connected': 'Telegram Connected',
        'code_from_telegram': 'Enter the code from Telegram:',
        'disconnected_from_telegram': 'Disconnected from Telegram.',
        'no_connection_telegram': 'No connection to Telegram.',
        'telegram_connected': 'Telegram Підключено',
        'code_from_telegram': 'Введіть код з Telegram:',
        'disconnected_from_telegram': 'Відключено від Telegram.',
        'no_connection_telegram': 'Немає підключення до Telegram.',
        # Поля конфигурации Telegram
        # Попытка подключиться к Telegram при запуске
        # Индикатор подключения к Telegram
        # Проверка подключения к Telegram
            logging.debug("Telegram connection is active.")
            logging.warning("Telegram connection lost.")
     """Асинхронний метод для підключення до Telegram."""
        logging.info("Connection to Telegram established.")
        logging.error(f"Error connecting to Telegram: {e}")
        QMessageBox.critical(self, self.translate('error'), f"{self.translate('error')} connecting to Telegram: {e}")
        # Переконємося, що з'єднання з Telegram встановлено
        # Відключення від Telegram
    telegram_module = TelegramModule(
    tg_connected = False  # Будет обновлено после подключения к Telegram

