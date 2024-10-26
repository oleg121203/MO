from __future__ import annotations  # Повинно бути першим

import sys
import os
import json
import traceback
import logging
from functools import wraps
from datetime import datetime
from typing import Tuple, List, Dict, Any

import asyncio
import aiosqlite
import pandas as pd
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QScrollArea, QMessageBox,
    QLineEdit, QSlider, QComboBox, QFormLayout, QTabWidget, QFileDialog,
    QDialog
)
from PyQt6.QtCore import (
    Qt, QPoint, pyqtSignal, QObject, QTimer
)
from PyQt6.QtGui import (
    QColor, QBrush, QFont, QPainter, QPen
)
from qasync import QEventLoop, asyncSlot

from telethon import errors, functions, types
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import (
    Channel, UserStatusOffline, UserStatusOnline, UserStatusRecently,
    UserStatusLastMonth, UserStatusLastWeek
)

from modules.mdb1_database import DatabaseModule
from modules.mt1_telegram import TelegramModule
from modules.config_manager import ConfigManager

# Создание переводов
translations = {
    'en': {
        'control_interface': 'Control Interface',
        'database_connected': 'Database Connected',
        'telegram_connected': 'Telegram Connected',
        'smart_search': 'Smart Search',
        'search_accounts': 'Search Accounts',
        'pause': '⏸ Pause',
        'continue': '▶️ Continue',
        'stop': '■ Stop',
        'groups': 'Groups',
        'accounts': 'Accounts',
        'status_ready': 'Status: Ready',
        'transparency': 'Transparency',
        'settings': 'Settings',
        'theme': 'Theme',
        'language': 'Language',
        'hacker': 'Hacker',
        'friendly': 'Friendly',
        'error': 'Error',
        'access_denied': 'Access Denied',
        'cannot_access_group': 'Cannot access participants of group',
        'processing_group': 'Processing group',
        'search_completed': 'Search completed.',
        'accounts_process_paused': 'Accounts process paused.',
        'accounts_process_resumed': 'Accounts process resumed.',
        'accounts_process_stopped': 'Accounts process stopped.',
        'groups_process_paused': 'Groups process paused.',
        'groups_process_resumed': 'Groups process resumed.',
        'groups_process_stopped': 'Groups process stopped.',
        'authorization_cancelled': 'Authorization Cancelled',
        'authorization_cancelled_by_user': 'Authorization was cancelled by the user.',
        'public_groups_search': 'Public Groups Search',
        'added_new_groups': 'Added new groups',
        'no_new_groups_found': 'No new groups found to add.',
        'status': 'Status',
        'code_from_telegram': 'Enter the code from Telegram:',
        'password': 'Enter your password:',
        'confirmation_code': 'Confirmation Code',
        'cancelled_by_user': 'Cancelled by user.',
        'group_added': 'Group added to database.',
        'account_added': 'Account added to database.',
        'group_updated': 'Group updated in database.',
        'account_updated': 'Account updated in database.',
        'failed_to_connect_db': 'Failed to connect to the database.',
        'disconnected_from_telegram': 'Disconnected from Telegram.',
        'disconnected_from_db': 'Disconnected from the database.',
        'process_stopped': 'Process stopped.',
        'no_connection_telegram': 'No connection to Telegram.',
        'load_groups_first': 'Load the groups first.',
        'searching_public_groups': 'Searching public groups...',
        'searching_keyword': 'Searching for keyword',
        'processing_file': 'Processing file',
        'files_dropped': 'Files dropped',
        'groups_added': 'Groups added',
        'groups_already_loaded': 'Groups already loaded or links are incorrect.',
        'process_stopped_on_exit': 'Processes stopped upon window closing.',
        'phone_number': 'Phone Number',
        'general': 'General',
        'interface': 'Interface',
        'save': 'Save',
        'due_to_insufficient_permissions': 'due to insufficient permissions.',
        'please_fill_all_fields': 'Please fill in all fields.',
        'save_interface_settings': 'Save Interface Settings',
        'save_all_settings': 'Save All Settings',
        'settings_saved': 'Settings saved.',
        'select_config_file': 'Select Configuration File',
        'import_config': 'Import Config',
        'export_config': 'Export Config',
        'config_imported': 'Configuration imported.',
        'config_exported': 'Configuration exported.',
        'select_file': 'Select File',
        'file_saved': 'File saved.',
        'file_loaded': 'File loaded.',
        'open': 'Open',
        'cancel': 'Cancel',
        'cannot_load_config': 'Cannot load configuration file.'
    },
    'uk': {
        'control_interface': 'Контрольний Інтерфейс',
        'database_connected': 'База Даних Підключена',
        'telegram_connected': 'Telegram Підключено',
        'smart_search': 'Розумний Пошук',
        'search_accounts': 'Пошук Акаунтів',
        'pause': '⏸ Пауза',
        'continue': '▶️ Продовжити',
        'stop': '■ Стоп',
        'groups': 'Групи',
        'accounts': 'Акаунти',
        'status_ready': 'Статус: Готово',
        'transparency': 'Прозорість',
        'settings': 'Налаштування',
        'theme': 'Тема',
        'language': 'Мова',
        'hacker': 'Хакерська',
        'friendly': 'Дружня',
        'error': 'Помилка',
        'access_denied': 'Доступ Заборонено',
        'cannot_access_group': 'Не можу отримати доступ до учасників групи',
        'processing_group': 'Обробка групи',
        'search_completed': 'Пошук завершено.',
        'accounts_process_paused': 'Процес акаунтів призупинено.',
        'accounts_process_resumed': 'Процес акаунтів відновлено.',
        'accounts_process_stopped': 'Процес акаунтів зупинено.',
        'groups_process_paused': 'Процес груп призупинено.',
        'groups_process_resumed': 'Процес груп відновлено.',
        'groups_process_stopped': 'Процес груп зупинено.',
        'authorization_cancelled': 'Авторизацію скасовано',
        'authorization_cancelled_by_user': 'Авторизацію було скасовано користувачем.',
        'public_groups_search': 'Пошук Публічних Груп',
        'added_new_groups': 'Додано нові групи',
        'no_new_groups_found': 'Не знайдено нових груп для додавання.',
        'status': 'Статус',
        'code_from_telegram': 'Введіть код з Telegram:',
        'password': 'Введіть ваш пароль:',
        'confirmation_code': 'Код Підтвердження',
        'cancelled_by_user': 'Скасовано користувачем.',
        'group_added': 'Групу додано до бази даних.',
        'account_added': 'Акаунт додано до бази даних.',
        'group_updated': 'Групу оновлено в базі даних.',
        'account_updated': 'Акаунт оновлено в базі даних.',
        'failed_to_connect_db': 'Не вдалося підключитися до бази даних.',
        'disconnected_from_telegram': 'Відключено від Telegram.',
        'disconnected_from_db': 'Відключено від бази даних.',
        'process_stopped': 'Процес зупинено.',
        'no_connection_telegram': 'Немає підключення до Telegram.',
        'load_groups_first': 'Спочатку завантажте групи.',
        'searching_public_groups': 'Пошук публічних груп...',
        'searching_keyword': 'Пошук за ключовим словом',
        'processing_file': 'Обробка файлу',
        'files_dropped': 'Файли перетягнуті',
        'groups_added': 'Групи додано',
        'groups_already_loaded': 'Групи вже завантажені або посилання некоректні.',
        'process_stopped_on_exit': 'Процеси зупинено при закритті вікна.',
        'phone_number': 'Номер Телефону',
        'general': 'Загальні',
        'interface': 'Інтерфейс',
        'save': 'Зберегти',
        'due_to_insufficient_permissions': 'через недостатні привілеї.',
        'please_fill_all_fields': 'Будь ласка, заповніть усі поля.',
        'save_interface_settings': 'Зберегти Налаштування Інтерфейсу',
        'save_all_settings': 'Зберегти Усі Налаштування',
        'settings_saved': 'Налаштування збережено.',
        'select_config_file': 'Виберіть Файл Конфігурації',
        'import_config': 'Імпортувати Конфігурацію',
        'export_config': 'Експортувати Конфігурацію',
        'config_imported': 'Конфігурацію імпортовано.',
        'config_exported': 'Конфігурацію експортовано.',
        'select_file': 'Виберіть Файл',
        'file_saved': 'Файл збережено.',
        'file_loaded': 'Файл завантажено.',
        'open': 'Відкрити',
        'cancel': 'Скасувати',
        'cannot_load_config': 'Не вдається завантажити файл конфігурації.',
        'enter_keywords': 'Введіть ключові слова',
        'enter_keywords_for_search': 'Введіть ключові слова для пошуку публічних груп:',
        'keywords_example': 'наприклад: спорт, музика, технології'
    }
}

current_language = 'uk'  # По умолчанию украинский язык
current_theme = 'hacker'  # По умолчанию тема "Хакерская"

# Темы
themes = {
    'hacker': {
        'background_color': 'rgba(0, 20, 0, 0.9)',
        'text_color': '#00FF00',
        'button_color': '#006400',
        'button_hover_color': '#00FF00',
        'progress_chunk_color': '#00FF00',
        'progress_background_color': 'rgba(0, 25, 0, 0.2)',
        'tab_selected_color': '#00FF00',
        'tab_unselected_color': '#006400'
    },
    'friendly': {
        'background_color': 'rgba(240, 248, 255, 0.9)',  # AliceBlue
        'text_color': '#000080',  # Navy
        'button_color': '#ADD8E6',  # LightBlue
        'button_hover_color': '#87CEEB',  # SkyBlue
        'progress_chunk_color': '#1E90FF',  # DodgerBlue
        'progress_background_color': 'rgba(220, 220, 220, 0.5)',
        'tab_selected_color': '#87CEEB',
        'tab_unselected_color': '#ADD8E6'
    }
}

class AuthDialog(QDialog):
    def __init__(self, title, label, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.value = None

        layout = QVBoxLayout()

        self.label = QLabel(label)
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Normal)
        layout.addWidget(self.label)
        layout.addWidget(self.input)

        self.button = QPushButton("OK")
        self.button.clicked.connect(self.accept)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def accept(self):
        self.value = self.input.text()
        super().accept()

    async def asyncExec(self):
        """Асинхронний метод для виконання діалогу."""
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def on_accept():
            future.set_result(True)
            self.close()

        def on_reject():
            future.set_result(False)
            self.close()

        self.accepted.connect(on_accept)
        self.rejected.connect(on_reject)
        self.show()

        return await future

class ConfigGUI(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle(self.translate('settings'))
        self.setModal(True)
        self.init_ui()

    def translate(self, key):
        return translations[current_language].get(key, key)

    def init_ui(self):
        layout = QVBoxLayout()

        # Создаем вкладки
        self.tabs = QTabWidget()
        self.general_tab = QWidget()
        self.interface_tab = QWidget()

        # Вкладка "Общие" (General)
        general_layout = QFormLayout()
        # Поля конфигурации Telegram
        self.api_id_input = QLineEdit()
        self.api_hash_input = QLineEdit()
        self.phone_number_input = QLineEdit()
        general_layout.addRow(QLabel("API ID:"), self.api_id_input)
        general_layout.addRow(QLabel("API Hash:"), self.api_hash_input)
        general_layout.addRow(QLabel(self.translate('phone_number')), self.phone_number_input)

        # Поля конфигурации базы данных
        self.db_host_input = QLineEdit()
        self.db_user_input = QLineEdit()
        self.db_password_input = QLineEdit()
        self.db_name_input = QLineEdit()
        general_layout.addRow(QLabel("DB Host:"), self.db_host_input)
        general_layout.addRow(QLabel("DB User:"), self.db_user_input)
        general_layout.addRow(QLabel("DB Password:"), self.db_password_input)
        general_layout.addRow(QLabel("DB Name:"), self.db_name_input)

        self.general_tab.setLayout(general_layout)

        # Вкладка "Интерфейс" (Interface)
        interface_layout = QFormLayout()
        # Слайдер прозрачности
        self.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.transparency_slider.setMinimum(50)
        self.transparency_slider.setMaximum(100)
        self.transparency_slider.setValue(100)
        self.transparency_slider.valueChanged.connect(self.update_transparency_live)
        interface_layout.addRow(QLabel(self.translate('transparency')), self.transparency_slider)
        # Настройка языка
        self.language_selector = QComboBox()
        self.language_selector.addItems(['English', 'Українська'])
        self.language_selector.setCurrentIndex(0 if current_language == 'en' else 1)
        self.language_selector.currentIndexChanged.connect(self.update_language)
        interface_layout.addRow(QLabel(self.translate('language')), self.language_selector)
        # Выбор темы
        self.theme_selector = QComboBox()
        self.theme_selector.addItems([self.translate('hacker'), self.translate('friendly')])
        self.theme_selector.setCurrentIndex(0 if current_theme == 'hacker' else 1)
        self.theme_selector.currentIndexChanged.connect(self.update_theme)
        interface_layout.addRow(QLabel(self.translate('theme')), self.theme_selector)
        self.interface_tab.setLayout(interface_layout)

        # Добавляем вкладки в TabWidget
        self.tabs.addTab(self.general_tab, self.translate('general'))
        self.tabs.addTab(self.interface_tab, self.translate('interface'))

        layout.addWidget(self.tabs)

        # Кнопки сохранения настроек
        buttons_layout = QHBoxLayout()
        self.save_interface_button = QPushButton(self.translate('save_interface_settings'))
        self.save_interface_button.clicked.connect(self.save_interface_settings)
        self.save_all_button = QPushButton(self.translate('save_all_settings'))
        self.save_all_button.clicked.connect(self.save_all_settings)
        buttons_layout.addWidget(self.save_interface_button)
        buttons_layout.addWidget(self.save_all_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.apply_theme()
        self.load_existing_settings()

    def apply_theme(self):
        theme = themes[current_theme]
        background_color = theme['background_color']
        text_color = theme['text_color']
        button_color = theme['button_color']
        button_hover_color = theme['button_hover_color']
        tab_selected_color = theme['tab_selected_color']
        tab_unselected_color = theme['tab_unselected_color']

        # Применяем стили к окну настроек
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {background_color};
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QLineEdit {{
                background-color: white;
                color: black;
            }}
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
            }}
            QPushButton:hover {{
                background-color: {button_hover_color};
            }}
            QTabWidget::pane {{
                border: 1px solid {text_color};
            }}
            QTabBar::tab {{
                background: {tab_unselected_color};
                color: {text_color};
                padding: 10px;
            }}
            QTabBar::tab:selected {{
                background: {tab_selected_color};
            }}
        """)

    def load_existing_settings(self):
        # Загружаем существующие настройки
        telegram_config = self.config_manager.config.get('telegram', {})
        self.api_id_input.setText(telegram_config.get('api_id', ''))
        self.api_hash_input.setText(telegram_config.get('api_hash', ''))
        self.phone_number_input.setText(telegram_config.get('phone_number', ''))

        database_config = self.config_manager.config.get('database', {})
        self.db_host_input.setText(database_config.get('host', ''))
        self.db_user_input.setText(database_config.get('user', ''))
        self.db_password_input.setText(database_config.get('password', ''))
        self.db_name_input.setText(database_config.get('database', ''))

        interface_config = self.config_manager.config.get('interface', {})
        self.transparency_slider.setValue(interface_config.get('transparency', 100))
        language = interface_config.get('language', 'uk')
        theme = interface_config.get('theme', 'hacker')

        self.language_selector.setCurrentIndex(0 if language == 'en' else 1)
        self.theme_selector.setCurrentIndex(0 if theme == 'hacker' else 1)

    def update_transparency_live(self):
        """Обновляет прозрачность окна настроек в реальном времени."""
        opacity = self.transparency_slider.value() / 100.0
        self.parent().setWindowOpacity(opacity)

    def update_language(self):
        """Обновляет язык интерфейса."""
        global current_language
        current_language = 'en' if self.language_selector.currentIndex() == 0 else 'uk'
        self.parent().change_language(self.language_selector.currentIndex())
        self.update_translations()
        self.apply_theme()

    def update_theme(self):
        """Обновляет тему интерфейса."""
        global current_theme
        current_theme = 'hacker' if self.theme_selector.currentIndex() == 0 else 'friendly'
        self.parent().change_theme(self.theme_selector.currentIndex())
        self.apply_theme()

    def update_translations(self):
        """Обновляет переводы окна настроек."""
        self.setWindowTitle(self.translate('settings'))
        self.tabs.setTabText(0, self.translate('general'))
        self.tabs.setTabText(1, self.translate('interface'))
        self.save_interface_button.setText(self.translate('save_interface_settings'))
        self.save_all_button.setText(self.translate('save_all_settings'))

    def translate(self, key):
        return translations[current_language].get(key, key)

    def save_interface_settings(self):
        """Сохраняет настройки интерфейса."""
        global current_language, current_theme
        current_language = 'en' if self.language_selector.currentIndex() == 0 else 'uk'
        current_theme = 'hacker' if self.theme_selector.currentIndex() == 0 else 'friendly'

        # Сохраняем настройки интерфейса
        self.config_manager.config['interface'] = {
            'transparency': self.transparency_slider.value(),
            'language': current_language,
            'theme': current_theme
        }

        self.config_manager.save_config()
        QMessageBox.information(self, self.translate('settings'), self.translate('settings_saved'))

    def save_all_settings(self):
        """Сохраняет все настройки."""
        api_id = self.api_id_input.text().strip()
        api_hash = self.api_hash_input.text().strip()
        phone_number = self.phone_number_input.text().strip()
        db_host = self.db_host_input.text().strip()
        db_user = self.db_user_input.text().strip()
        db_password = self.db_password_input.text().strip()
        db_name = self.db_name_input.text().strip()

        if not all([api_id, api_hash, phone_number, db_host, db_user, db_password, db_name]):
            QMessageBox.warning(self, self.translate('error'), self.translate('please_fill_all_fields'))
            return

        # Обновляем конфигурацию
        self.config_manager.config['telegram'] = {
            'api_id': api_id,
            'api_hash': api_hash,
            'phone_number': phone_number
        }

        self.config_manager.config['database'] = {
            'host': db_host,
            'user': db_user,
            'password': db_password,
            'database': db_name
        }

        # Сохраняем настройки интерфейса
        self.save_interface_settings()

        self.config_manager.save_config()
        QMessageBox.information(self, self.translate('settings'), self.translate('settings_saved'))
        self.accept()

    def run(self):
        """Запускает диалог."""
        self.exec()

class TrafficLightWidget(QWidget):
    def __init__(self, parent=None, initial_state="off", size=(30, 30)):
        super().__init__(parent)
        self.state = initial_state
        self.setFixedSize(*size)

    def set_state(self, state):
        self.state = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor("grey")
        if self.state == "green":
            color = QColor("#00FF7F")
        elif self.state == "red":
            color = QColor("red")
        elif self.state == "yellow":
            color = QColor("yellow")
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawEllipse(0, 0, self.width(), self.height())



class KeywordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.translate('enter_keywords'))
        self.setModal(True)
        self.keywords = None

        self.init_ui()
        self.apply_theme()

    def translate(self, key):
        return translations[current_language].get(key, key)

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel(self.translate('enter_keywords_for_search'))
        self.input = QLineEdit()
        self.input.setPlaceholderText(self.translate('keywords_example'))
        layout.addWidget(self.label)
        layout.addWidget(self.input)

        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton(self.translate('search'))
        self.cancel_button = QPushButton(self.translate('cancel'))
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # Устанавливаем большую прозрачность
        self.setWindowOpacity(0.9)

    def apply_theme(self):
        theme = themes[current_theme]
        background_color = theme['background_color']
        text_color = theme['text_color']
        button_color = theme['button_color']
        button_hover_color = theme['button_hover_color']

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {background_color};
                color: {text_color};
                border-radius: 10px;
            }}
            QLabel {{
                color: {text_color};
            }}
            QLineEdit {{
                background-color: white;
                color: black;
            }}
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {button_hover_color};
            }}
        """)

    def accept(self):
        self.keywords = self.input.text()
        super().accept()

    async def asyncExec(self):
        """Асинхронний метод для виконання діалогу."""
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def on_accept():
            future.set_result(True)
            self.close()

        def on_reject():
            future.set_result(False)
            self.close()

        self.accepted.connect(on_accept)
        self.rejected.connect(on_reject)
        self.show()

        return await future

class GroupsListWidget(QListWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setStyleSheet("""
            QListWidget {
                background-color: rgba(0, 30, 0, 0.4);
                color: white;
                border-radius: 10px;
            }
            QListWidget::item:selected {
                background-color: rgba(0, 30, 0, 0.4);
            }
            QListWidget::item:hover {
                background-color: rgba(0, 30, 0, 0.4);
            }
        """)

    def start_blinking(self, index):
        """Индикация обработки группы миганием фона."""
        item = self.item(index)
        if item:
            blink_color = QColor("yellow")
            item.setBackground(QBrush(blink_color))
            QTimer.singleShot(500, lambda: item.setBackground(QBrush()))
        else:
            logging.warning(f"No item at index {index} to blink.")

    def mark_processed(self, index):
        """Отмечает группу как обработанную, изменяя цвет шрифта."""
        item = self.item(index)
        if item:
            processed_font_color = QColor(204, 204, 0)
            item.setForeground(QBrush(processed_font_color))
        else:
            logging.warning(f"No item at index {index} to mark as processed.")

def telegram_activity_indicator(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if self.tg_connected:
            self.tg_light.set_state("yellow")
        result = await func(self, *args, **kwargs)
        if self.tg_connected:
            self.tg_light.set_state("green")
        return result
    return wrapper

def database_activity_indicator(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if self.db_connected:
            self.db_light.set_state("yellow")
        result = await func(self, *args, **kwargs)
        if self.db_connected:
            self.db_light.set_state("green")
        return result
    return wrapper

class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setStyleSheet("background-color: rgba(0, 40, 0, 0.3); border-radius: 10px;")
        self.init_ui()
        self.dragging = False

    def init_ui(self):
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(15, 0, 15, 0)
        top_bar_layout.setSpacing(10)

        # Поле заголовка
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        # Динамические виджеты (будут добавлены позже)
        self.dynamic_widgets_layout = QHBoxLayout()
        self.dynamic_widgets_layout.setSpacing(5)

        # Добавляем элементы в верхнюю панель
        top_bar_layout.addWidget(self.title_label)
        top_bar_layout.addStretch()
        top_bar_layout.addLayout(self.dynamic_widgets_layout)
        self.setLayout(top_bar_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.parent().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.parent().move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self, db_module, telegram_module, db_connected, tg_connected, config_manager):
        super().__init__()

        self.db_module = db_module
        self.telegram_module = telegram_module
        self.db_connected = db_connected
        self.tg_connected = tg_connected
        self.config_manager = config_manager
        self.setWindowTitle('Transparent Interface')
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Разрешаем прием перетаскиваемых файлов
        self.setAcceptDrops(True)

        # Инициализация флагов процессов
        self.is_paused_accounts = False
        self.stop_flag_accounts = False
        self.is_paused_groups = False
        self.stop_flag_groups = False

        self.connection = None  # Инициализируем self.connection

        self.max_groups = 10  # Ограничение на 10 групп

        self.groups_list = []
        self.accounts_list = []

        # Главный макет
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Верхняя панель с кнопками
        self.top_bar = TopBar(self)
        top_bar_layout = self.top_bar.layout()

        # Добавляем динамические виджеты в верхнюю панель
        self.add_dynamic_widgets_to_top_bar()

        # Окна отображения информации
        info_layout = QHBoxLayout()

        # Окно для информации о группах (слева)
        groups_layout = QVBoxLayout()
        self.groups_list_widget = GroupsListWidget(main_window=self)
        self.groups_list_widget.setStyleSheet("background-color: rgba(0, 30, 0, 0.4); color: white; border-radius: 10px;")

        # Нижняя панель над группами
        self.groups_status_label = QLabel()
        self.groups_status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.groups_status_label.setFont(QFont("Arial", 12))

        # Прогресс-бар для групп
        self.progress_bar_groups = QProgressBar()
        self.progress_bar_groups.setFixedHeight(25)
        self.progress_bar_groups.setTextVisible(False)
        self.progress_bar_groups.setVisible(False)

        # Кнопка умного поиска
        self.smart_search_button = QPushButton()
        self.smart_search_button.clicked.connect(self.smart_search_slot)

        # Кнопки паузы и остановки для умного поиска
        self.pause_button_groups = QPushButton()
        self.pause_button_groups.clicked.connect(self.pause_groups_process)

        self.stop_button_groups = QPushButton()
        self.stop_button_groups.clicked.connect(self.stop_groups_process)

        self.pause_button_groups.setVisible(False)
        self.stop_button_groups.setVisible(False)

        # Макет для прогресс-бара и кнопок для групп
        groups_control_layout = QHBoxLayout()
        groups_control_layout.addWidget(self.smart_search_button)
        groups_control_layout.addWidget(self.progress_bar_groups)
        groups_control_layout.addWidget(self.pause_button_groups)
        groups_control_layout.addWidget(self.stop_button_groups)

        groups_layout.addWidget(self.groups_status_label)
        groups_layout.addWidget(self.groups_list_widget)
        groups_layout.addLayout(groups_control_layout)

        # Окно для информации об аккаунтах (справа)
        accounts_layout = QVBoxLayout()

        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(5)
        self.accounts_table.setHorizontalHeaderLabels(['ID', 'First Name', 'Last Name', 'Username', 'Phone'])
        self.accounts_table.verticalHeader().setVisible(False)

        self.accounts_scroll_area = QScrollArea()
        self.accounts_scroll_area.setWidget(self.accounts_table)
        self.accounts_scroll_area.setWidgetResizable(True)
        self.accounts_scroll_area.setStyleSheet("border: none;")

        # Нижняя панель над аккаунтами
        self.accounts_status_label = QLabel()
        self.accounts_status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.accounts_status_label.setFont(QFont("Arial", 12))

        # Прогресс-бар для аккаунтов
        self.progress_bar_accounts = QProgressBar()
        self.progress_bar_accounts.setFixedHeight(25)
        self.progress_bar_accounts.setTextVisible(False)
        self.progress_bar_accounts.setVisible(False)

        # Кнопка поиска аккаунтов
        self.search_accounts_button = QPushButton()
        self.search_accounts_button.clicked.connect(self.search_accounts_in_groups_slot)

        # Кнопки паузы и остановки для аккаунтов
        self.pause_button_accounts = QPushButton()
        self.pause_button_accounts.clicked.connect(self.pause_accounts_process)

        self.stop_button_accounts = QPushButton()
        self.stop_button_accounts.clicked.connect(self.stop_accounts_process)

        self.pause_button_accounts.setVisible(False)
        self.stop_button_accounts.setVisible(False)

        # Макет для прогресс-бара и кнопок для аккаунтов
        accounts_control_layout = QHBoxLayout()
        accounts_control_layout.addWidget(self.search_accounts_button)
        accounts_control_layout.addWidget(self.progress_bar_accounts)
        accounts_control_layout.addWidget(self.pause_button_accounts)
        accounts_control_layout.addWidget(self.stop_button_accounts)

        accounts_layout.addWidget(self.accounts_status_label)
        accounts_layout.addWidget(self.accounts_scroll_area)
        accounts_layout.addLayout(accounts_control_layout)

        info_layout.addLayout(groups_layout)
        info_layout.addLayout(accounts_layout)

        # Окно статуса
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.status_label.setFont(QFont("Arial", 14))

        # Добавляем элементы в главный макет
        main_layout.addWidget(self.top_bar)
        main_layout.addLayout(info_layout)
        main_layout.addWidget(self.status_label)

        # Центральный виджет
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Применяем начальную тему и переводы
        self.apply_theme()
        self.update_translations()
        self.load_interface_settings()

        # Попытка подключиться к Telegram при запуске
        if not self.tg_connected:
            asyncio.create_task(self.connect_to_telegram())

        # Настройка периодической проверки соединения
        self.connection_check_timer = QTimer()
        self.connection_check_timer.timeout.connect(self.check_connections)
        self.connection_check_timer.start(60000)

    def translate(self, key):
        return translations[current_language].get(key, key)

    def apply_theme(self):
        theme = themes[current_theme]
        background_color = theme['background_color']
        text_color = theme['text_color']
        button_color = theme['button_color']
        button_hover_color = theme['button_hover_color']
        progress_chunk_color = theme['progress_chunk_color']
        progress_background_color = theme['progress_background_color']

        # Применяем стили к виджетам
        self.centralWidget().setStyleSheet(f"background-color: {background_color}; border-radius: 10px;")
        self.status_label.setStyleSheet(f"color: {text_color}; font-size: 16px;")
        self.top_bar.title_label.setStyleSheet(f"color: {text_color}; font-size: 20px;")

        # Обновляем стили кнопок
        button_style = f"""
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
                font-size: 14px;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {button_hover_color};
            }}
        """
        self.smart_search_button.setStyleSheet(button_style)
        self.search_accounts_button.setStyleSheet(button_style)
        self.pause_button_groups.setStyleSheet(button_style)
        self.stop_button_groups.setStyleSheet(button_style)
        self.pause_button_accounts.setStyleSheet(button_style)
        self.stop_button_accounts.setStyleSheet(button_style)

        # Обновляем прогресс-бары
        progress_bar_style = f"""
            QProgressBar {{
                background-color: {progress_background_color};
                color: {text_color};
                border: 1px solid {text_color};
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {progress_chunk_color};
                border-radius: 5px;
            }}
        """
        self.progress_bar_groups.setStyleSheet(progress_bar_style)
        self.progress_bar_accounts.setStyleSheet(progress_bar_style)

        # Обновляем метки
        label_style = f"color: {text_color}; font-size: 14px;"
        self.groups_status_label.setStyleSheet(label_style)
        self.accounts_status_label.setStyleSheet(label_style)

    def update_translations(self):
        self.top_bar.title_label.setText(self.translate('control_interface'))
        self.groups_status_label.setText(f"{self.translate('groups')} (0):")
        self.accounts_status_label.setText(f"{self.translate('accounts')} (0):")
        self.status_label.setText(self.translate('status_ready'))
        self.smart_search_button.setText(self.translate('smart_search'))
        self.search_accounts_button.setText(self.translate('search_accounts'))
        self.pause_button_groups.setText(self.translate('pause'))
        self.stop_button_groups.setText(self.translate('stop'))
        self.pause_button_accounts.setText(self.translate('pause'))
        self.stop_button_accounts.setText(self.translate('stop'))

    def add_dynamic_widgets_to_top_bar(self):
        # Индикатор подключения к базе данных
        self.db_light = TrafficLightWidget(parent=self.top_bar, initial_state="green" if self.db_connected else "off", size=(30, 30))
        db_light_label = QLabel(self.translate('database_connected'))
        db_light_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        db_light_label.setFont(QFont("Arial", 12))
        db_layout = QHBoxLayout()
        db_layout.setSpacing(5)
        db_layout.addWidget(self.db_light)
        db_layout.addWidget(db_light_label)

        # Индикатор подключения к Telegram
        self.tg_light = TrafficLightWidget(parent=self.top_bar, initial_state="green" if self.tg_connected else "off", size=(30, 30))
        tg_light_label = QLabel(self.translate('telegram_connected'))
        tg_light_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        tg_light_label.setFont(QFont("Arial", 12))
        tg_layout = QHBoxLayout()
        tg_layout.setSpacing(5)
        tg_layout.addWidget(self.tg_light)
        tg_layout.addWidget(tg_light_label)

        # Кнопка настроек
        settings_button = QPushButton("⚙️")
        settings_button.setFixedSize(40, 40)
        settings_button.clicked.connect(self.open_settings)

        # Кнопка минимизации окна
        minimize_button = QPushButton("_")
        minimize_button.setFixedSize(40, 40)
        minimize_button.clicked.connect(self.showMinimized)

        # Кнопка максимизации окна
        maximize_button = QPushButton("⬛")
        maximize_button.setFixedSize(40, 40)
        maximize_button.clicked.connect(self.showMaximized)

        # Кнопка закрытия окна
        close_button = QPushButton("X")
        close_button.setFixedSize(40, 40)
        close_button.clicked.connect(self.close)

        # Обновляем стили кнопок верхней панели
        self.update_top_bar_button_styles([settings_button, minimize_button, maximize_button, close_button])

        # Добавляем виджеты в динамический макет на верхней панели
        self.top_bar.dynamic_widgets_layout.addLayout(db_layout)
        self.top_bar.dynamic_widgets_layout.addLayout(tg_layout)
        self.top_bar.dynamic_widgets_layout.addWidget(settings_button)
        self.top_bar.dynamic_widgets_layout.addWidget(minimize_button)
        self.top_bar.dynamic_widgets_layout.addWidget(maximize_button)
        self.top_bar.dynamic_widgets_layout.addWidget(close_button)

    def update_top_bar_button_styles(self, buttons):
        theme = themes[current_theme]
        button_color = theme['button_color']
        text_color = theme['text_color']
        button_hover_color = theme['button_hover_color']

        button_style = f"""
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
                font-size: 16px;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {button_hover_color};
            }}
        """
        for button in buttons:
            button.setStyleSheet(button_style)

    def load_interface_settings(self):
        """Загружает настройки интерфейса."""
        interface_config = self.config_manager.config.get('interface', {})
        transparency = interface_config.get('transparency', 100)
        self.setWindowOpacity(transparency / 100.0)

    @asyncSlot()
    async def check_connections(self):
        # Индикаторы устанавливаются на желтый во время проверки
        self.tg_light.set_state("yellow")
        self.db_light.set_state("yellow")

        # Задержка на 5 секунд для симуляции проверки
        await asyncio.sleep(5)

        # Проверка подключения к Telegram
        if await self.telegram_module.is_connected():
            self.tg_connected = True
            self.tg_light.set_state("green")
            logging.debug("Telegram connection is active.")
        else:
            self.tg_connected = False
            self.tg_light.set_state("red")
            logging.warning("Telegram connection lost.")

        # Проверка подключения к базе данных
        if await self.db_module.is_connected():
            self.db_connected = True
            self.db_light.set_state("green")
            logging.debug("Database connection is active.")
        else:
            self.db_connected = False
            self.db_light.set_state("red")
            logging.warning("Database connection lost.")

    @asyncSlot()
    async def search_accounts_in_groups_slot(self):
        # Приховуємо кнопку пошуку та показуємо прогрес-бар та кнопки керування
        self.search_accounts_button.setVisible(False)
        self.progress_bar_accounts.setVisible(True)
        self.pause_button_accounts.setVisible(True)
        self.stop_button_accounts.setVisible(True)

        await self.search_accounts_in_groups(auto_start=False)

    @asyncSlot()
    async def smart_search_slot(self):
     # Сховати кнопку пошуку та показати прогрес-бар і кнопки керування
     self.smart_search_button.setVisible(False)
     self.progress_bar_groups.setVisible(True)
     self.pause_button_groups.setVisible(True)
     self.stop_button_groups.setVisible(True)

     keyword_dialog = KeywordDialog()
     if await keyword_dialog.asyncExec():  # Виклик асинхронного exec
        keywords = keyword_dialog.keywords
        if keywords:
            await self.search_public_groups(keywords)
        else:
            QMessageBox.warning(self, self.translate('error'), "Будь ласка, введіть ключові слова для пошуку.")
            # Якщо немає ключових слів, відновити видимість кнопок
            self.smart_search_button.setVisible(True)
            self.progress_bar_groups.setVisible(False)
            self.pause_button_groups.setVisible(False)
            self.stop_button_groups.setVisible(False)
     else:
        logging.info("Пошук публічних груп скасовано користувачем.")
        # Якщо скасовано, відновити видимість кнопок
        self.smart_search_button.setVisible(True)
        self.progress_bar_groups.setVisible(False)
        self.pause_button_groups.setVisible(False)
        self.stop_button_groups.setVisible(False)

    @telegram_activity_indicator
    async def connect_to_telegram(self):
     """Асинхронний метод для підключення до Telegram."""
     try:
        await self.telegram_module.connect()

        if not await self.telegram_module.is_user_authorized():
            # Відображаємо діалог для введення коду підтвердження
            code_dialog = AuthDialog(self.translate('confirmation_code'), self.translate('code_from_telegram'))
            if await code_dialog.asyncExec():  # Виклик асинхронного exec
                code = code_dialog.value
            else:
                QMessageBox.warning(self, self.translate('authorization_cancelled'), self.translate('authorization_cancelled_by_user'))
                return

            try:
                await self.telegram_module.sign_in(code)
            except errors.SessionPasswordNeededError:
                # Відображаємо діалог для введення пароля
                password_dialog = AuthDialog(self.translate('password'), self.translate('password'))
                if await password_dialog.asyncExec():  # Виклик асинхронного exec
                    password = password_dialog.value
                    await self.telegram_module.sign_in(password=password)
                else:
                    QMessageBox.warning(self, self.translate('authorization_cancelled'), self.translate('authorization_cancelled_by_user'))
                    return

        self.tg_connected = True
        self.tg_light.set_state("green")
        self.status_label.setText(f"{self.translate('status')}: {self.translate('telegram_connected')}.")
        logging.info("Connection to Telegram established.")
     except Exception as e:
        self.tg_connected = False
        self.tg_light.set_state("off")
        self.status_label.setText(f"{self.translate('status')}: {e}")
        logging.error(f"Error connecting to Telegram: {e}")
        QMessageBox.critical(self, self.translate('error'), f"{self.translate('error')} connecting to Telegram: {e}")

    def parse_keywords(self, keywords):
     phrases = [phrase.strip() for phrase in keywords.split(',') if phrase.strip()]
     any_keywords = []
     all_keywords = []

     for phrase in phrases:
        words = phrase.strip().split()
        if len(words) == 1:
            # Одно слово, добавляем в any_keywords
            any_keywords.append(words[0])
        else:
            # Несколько слов, добавляем в all_keywords
            all_keywords.extend(words)
     return any_keywords, all_keywords

    
    
    
    @telegram_activity_indicator
    @database_activity_indicator
    async def search_public_groups(self, keywords: str) -> None:
     if not self.tg_connected:
        QMessageBox.warning(self, self.translate('error'), self.translate('no_connection_telegram'))
        return

     # Ініціалізація флагів управління
     self.is_paused_groups = False
     self.stop_flag_groups = False

     self.status_label.setText("Status: Searching public groups...")
     self.progress_bar_groups.setMaximum(0)
     self.progress_bar_groups.setValue(0)

     self.connection = await self.db_module.connect()
     if not self.connection:
        QMessageBox.critical(self, self.translate('error'), "Failed to connect to the database.")
        return

     try:
        new_groups: List[str] = []

        any_keywords, all_keywords = self.parse_keywords(keywords)

        total_keywords = len(any_keywords) + (1 if all_keywords else 0)
        self.progress_bar_groups.setMaximum(total_keywords)

        # Обробка any_keywords
        for index, keyword in enumerate(any_keywords):
            if self.stop_flag_groups or len(new_groups) >= self.max_groups:
                self.status_label.setText("Status: Search stopped.")
                break

            while self.is_paused_groups:
                await asyncio.sleep(0.1)
                if self.stop_flag_groups:
                    self.status_label.setText("Status: Search stopped.")
                    return

            self.status_label.setText(f"Status: Searching for keyword '{keyword}'...")
            logging.debug(f"Searching public groups with keyword '{keyword}'")

            try:
                result = await self.telegram_module.client(functions.contacts.SearchRequest(
                    q=keyword,
                    limit=100  # Настройте по необхідності
                ))

                for chat in result.chats:
                    logging.debug(f"Result for keyword '{keyword}': {chat}")

                    if self.stop_flag_groups or len(new_groups) >= self.max_groups:
                        break

                    # Пропускаємо заборонені канали
                    if isinstance(chat, types.ChannelForbidden):
                        logging.debug(f"Skipping forbidden channel: {chat}")
                        continue

                    # Обробляємо тільки відкриті канали, які є мегагрупами та мають більше 50 000 учасників
                    if not isinstance(chat, types.Channel) or not chat.megagroup:
                        logging.debug(f"Skipping non-megagroup chat: {chat}")
                        continue

                    # Перевірка кількості учасників
                    if hasattr(chat, 'participants_count') and chat.participants_count < 10000:
                        logging.debug(f"Skipping group with less than 10,000 participants: {chat.title} ({chat.participants_count} participants)")
                        continue

                    # Безпечно отримуємо назву групи
                    group_name = getattr(chat, 'title', '').lower()

                    try:
                        full_chat = await self.telegram_module.client(GetFullChannelRequest(channel=chat))
                        group_description = getattr(full_chat.full_chat, 'about', '').lower()
                    except Exception as e:
                        logging.error(f"Failed to get full channel info for {chat}: {e}")
                        continue

                    keyword_lower = keyword.lower()

                    if keyword_lower in group_name:
                        # Ключове слово знайдено в назві, додаємо групу
                        group_link = f"https://t.me/{chat.username}" if chat.username else f"https://t.me/c/{chat.id}"
                        if group_link not in self.groups_list and group_link not in new_groups:
                            new_groups.append(group_link)
                            # Зберігаємо групу в базу даних
                            group_info = {
                                'id': chat.id,
                                'title': chat.title or '',
                                'username': chat.username or '',
                                'date': chat.date.strftime('%Y-%m-%d %H:%M:%S') if chat.date else '',
                                'participants_count': chat.participants_count if hasattr(chat, 'participants_count') else 0,
                                'description': group_description,
                                'restricted': getattr(chat, 'restricted', False),
                                'verified': getattr(chat, 'verified', False),
                                'megagroup': getattr(chat, 'megagroup', False),
                                'gigagroup': getattr(chat, 'gigagroup', False),
                                'scam': getattr(chat, 'scam', False)
                            }
                            await self.save_group_to_db(self.connection, group_info)
                    elif keyword_lower in group_description:
                        # Ключове слово знайдено в описі, додаємо групу
                        group_link = f"https://t.me/{chat.username}" if chat.username else f"https://t.me/c/{chat.id}"
                        if group_link not in self.groups_list and group_link not in new_groups:
                            new_groups.append(group_link)
                            # Зберігаємо групу в базу даних
                            group_info = {
                                'id': chat.id,
                                'title': chat.title or '',
                                'username': chat.username or '',
                                'date': chat.date.strftime('%Y-%m-%d %H:%M:%S') if chat.date else '',
                                'participants_count': chat.participants_count if hasattr(chat, 'participants_count') else 0,
                                'description': group_description,
                                'restricted': getattr(chat, 'restricted', False),
                                'verified': getattr(chat, 'verified', False),
                                'megagroup': getattr(chat, 'megagroup', False),
                                'gigagroup': getattr(chat, 'gigagroup', False),
                                'scam': getattr(chat, 'scam', False)
                            }
                            await self.save_group_to_db(self.connection, group_info)
            except Exception as e:
                logging.error(f"Error searching with keyword '{keyword}': {type(e).__name__}: {str(e)}")
                logging.error(traceback.format_exc())  # Логування повного traceback
                QMessageBox.critical(self, self.translate('error'), f"Error searching with keyword '{keyword}': {type(e).__name__}: {str(e)}")
                continue

            self.progress_bar_groups.setValue(index + 1)

            if len(new_groups) >= self.max_groups:
                logging.info(f"Reached the limit of {self.max_groups} groups.")
                break

        # Обробка all_keywords
        if all_keywords and not self.stop_flag_groups and len(new_groups) < self.max_groups:
            index = len(any_keywords)
            first_keyword = all_keywords[0]  # Використовуємо перше слово для пошуку
            self.status_label.setText(f"Status: Searching for all keywords '{' '.join(all_keywords)}'...")
            logging.debug(f"Searching public groups with all keywords '{' '.join(all_keywords)}'")

            try:
                result = await self.telegram_module.client(functions.contacts.SearchRequest(
                    q=first_keyword,
                    limit=100  # Настройте по необхідності
                ))

                for chat in result.chats:
                    logging.debug(f"Result for all keywords: {chat}")

                    if self.stop_flag_groups or len(new_groups) >= self.max_groups:
                        break

                    # Пропускаємо заборонені канали
                    if isinstance(chat, types.ChannelForbidden):
                        logging.debug(f"Skipping forbidden channel: {chat}")
                        continue

                    if not isinstance(chat, types.Channel) or not chat.megagroup:
                        logging.debug(f"Skipping non-megagroup chat: {chat}")
                        continue

                    group_name = getattr(chat, 'title', '').lower()

                    try:
                        full_chat = await self.telegram_module.client(GetFullChannelRequest(channel=chat))
                        group_description = getattr(full_chat.full_chat, 'about', '').lower()
                    except Exception as e:
                        logging.error(f"Failed to get full channel info for {chat}: {e}")
                        continue

                    # Перевіряємо, що всі ключові слова присутні в назві або описі
                    name_matches = sum(word.lower() in group_name for word in all_keywords)
                    description_matches = sum(word.lower() in group_description for word in all_keywords)

                    if name_matches + description_matches >= len(all_keywords):
                        group_link = f"https://t.me/{chat.username}" if chat.username else f"https://t.me/c/{chat.id}"
                        if group_link not in self.groups_list and group_link not in new_groups:
                            new_groups.append(group_link)
                            # Зберігаємо групу в базу даних
                            group_info = {
                                'id': chat.id,
                                'title': chat.title or '',
                                'username': chat.username or '',
                                'date': chat.date.strftime('%Y-%m-%d %H:%M:%S') if chat.date else '',
                                'participants_count': chat.participants_count if hasattr(chat, 'participants_count') else 0,
                                'description': group_description,
                                'restricted': getattr(chat, 'restricted', False),
                                'verified': getattr(chat, 'verified', False),
                                'megagroup': getattr(chat, 'megagroup', False),
                                'gigagroup': getattr(chat, 'gigagroup', False),
                                'scam': getattr(chat, 'scam', False)
                            }
                            await self.save_group_to_db(self.connection, group_info)
            except Exception as e:
                logging.error(f"Error searching with all keywords '{' '.join(all_keywords)}': {type(e).__name__}: {str(e)}")
                logging.error(traceback.format_exc())
                QMessageBox.critical(self, self.translate('error'), f"Error searching with all keywords '{' '.join(all_keywords)}': {type(e).__name__}: {str(e)}")

            self.progress_bar_groups.setValue(total_keywords)

        if new_groups:
            self.groups_list.extend(new_groups)
            self.update_groups_list()
            logging.info(f"Added new groups: {len(new_groups)}")
            QMessageBox.information(self, "Public Groups Search", f"Added new groups: {len(new_groups)}.")
            # Автоматично запускаємо пошук акаунтів у нових групах
            await self.search_accounts_in_groups(auto_start=True)
        else:
            logging.info("No new groups found to add.")
            QMessageBox.information(self, "Public Groups Search", "No new groups found to add.")

        self.status_label.setText("Status: Public groups search completed.")
        logging.info("Public groups search completed.")
     finally:
        await self.db_module.disconnect(self.connection)
        self.connection = None  # Очищуємо з'єднання
        # Відновлюємо видимість кнопок
        self.smart_search_button.setVisible(True)
        self.progress_bar_groups.setVisible(False)
        self.pause_button_groups.setVisible(False)
        self.stop_button_groups.setVisible(False)
        self.pause_button_groups.setText("⏸ Пауза")

    def open_settings(self):
        """Відкриває вікно налаштувань."""
        config_gui = ConfigGUI(self.config_manager, parent=self)
        config_gui.run()
        # Після закриття ConfigGUI, перезавантажуємо конфігурацію
        self.config_manager.load_config()
        if not self.config_manager.is_config_complete():
            QMessageBox.critical(self, "Error", "Configuration was not completed correctly. The application will be closed.")
            sys.exit(1)

    async def can_access_participants(self, chat):
        """Перевіряє, чи можемо ми отримати список учасників групи."""
        try:
            await self.telegram_module.client(GetFullChannelRequest(channel=chat))
            return True
        except ChatAdminRequiredError:
            logging.info(f"Cannot access participants of group {chat.title}: Admin privileges required.")
            return False
        except ChannelPrivateError:
            logging.info(f"Cannot access participants of group {chat.title}: The channel is private.")
            return False
        except Exception as e:
            logging.error(f"Unexpected error while checking access to group {chat.title}: {e}")
            return False

    @telegram_activity_indicator
    @database_activity_indicator
    async def search_accounts_in_groups(self, auto_start=False):
     if not self.tg_connected:
        QMessageBox.warning(self, self.translate('error'), self.translate('no_connection_telegram'))
        return

     if not self.groups_list:
        QMessageBox.warning(self, self.translate('error'), self.translate('load_groups_first'))
        return

     # Ініціалізація прапорів керування
     self.is_paused_accounts = False
     self.stop_flag_accounts = False

     if not auto_start:
        # Якщо пошук акаунтів розпочато вручну, кнопки вже налаштовані
        pass
     else:
        # Якщо пошук акаунтів розпочато автоматично після розумного пошуку
        self.search_accounts_button.setVisible(False)
        self.progress_bar_accounts.setVisible(True)
        self.pause_button_accounts.setVisible(True)
        self.stop_button_accounts.setVisible(True)

     self.accounts_table.setRowCount(0)
     self.accounts_list = []
     self.status_label.setText(f"{self.translate('status')}: {self.translate('processing_group')}s...")
     self.progress_bar_accounts.setMaximum(len(self.groups_list))
     self.progress_bar_accounts.setValue(0)

     connection = await self.db_module.connect()
     if not connection:
        QMessageBox.critical(self, self.translate('error'), self.translate('failed_to_connect_db'))
        return

     try:
        # Переконємося, що з'єднання з Telegram встановлено
        if not await self.telegram_module.is_connected():
            await self.telegram_module.connect()

        for index, group_link in enumerate(self.groups_list):
            if self.stop_flag_accounts:
                self.status_label.setText(f"{self.translate('status')}: {self.translate('process_stopped')}")
                break

            while self.is_paused_accounts:
                await asyncio.sleep(0.1)
                if self.stop_flag_accounts:
                    self.status_label.setText(f"{self.translate('status')}: {self.translate('process_stopped')}")
                    return

            self.groups_list_widget.start_blinking(index)
            self.status_label.setText(f"{self.translate('status')}: {self.translate('processing_group')} {index + 1}/{len(self.groups_list)}.")
            logging.debug(f"Processing group {group_link}")

            try:
                group_identifier = self.extract_group_identifier(group_link)
                if not group_identifier:
                    raise ValueError(f"Incorrect group link: {group_link}")

                group = await self.telegram_module.get_entity(group_identifier)

                # Перевіряємо, чи можемо ми отримати список учасників
                can_access = await self.can_access_participants(group)
                if not can_access:
                    logging.info(f"Skipping group {group_link} due to insufficient permissions.")
                    continue  # Пропускаємо цю групу

                # Отримуємо повну інформацію про групу
                full_chat = await self.telegram_module.client(GetFullChannelRequest(channel=group))
                participants_count = full_chat.full_chat.participants_count or 0
                description = full_chat.full_chat.about or ''

                # Збираємо інформацію про групу
                group_info = {
                    'id': group.id,
                    'title': group.title or '',
                    'username': group.username or '',
                    'date': group.date.strftime('%Y-%m-%d %H:%M:%S') if group.date else '',
                    'participants_count': participants_count,
                    'description': description,
                    'restricted': group.restricted,
                    'verified': group.verified,
                    'megagroup': group.megagroup,
                    'gigagroup': getattr(group, 'gigagroup', False),
                    'scam': group.scam,
                }
                await self.save_group_to_db(connection, group_info)

                try:
                    participants = await self.telegram_module.get_participants(group, aggressive=True)
                except errors.RPCError as e:
                    logging.error(f"Cannot get participants for group {group_link}: {e}")
                    # Пропускаємо цю групу
                    continue

                for user in participants:
                    if self.stop_flag_accounts:
                        self.status_label.setText(f"{self.translate('status')}: {self.translate('process_stopped')}")
                        return

                    while self.is_paused_accounts:
                        await asyncio.sleep(0.1)
                        if self.stop_flag_accounts:
                            self.status_label.setText(f"{self.translate('status')}: {self.translate('process_stopped')}")
                            return

                    # Збираємо інформацію про користувача
                    user_info = {
                        'id': user.id,
                        'first_name': user.first_name or '',
                        'last_name': user.last_name or '',
                        'username': user.username or '',
                        'phone': user.phone or '',
                        'status': self.get_user_status(user.status),
                        'bot': user.bot,
                        'verified': user.verified,
                        'restricted': user.restricted,
                        'scam': user.scam,
                        'fake': user.fake,
                        'access_hash': user.access_hash,
                        'last_online': self.get_last_online(user.status),
                    }
                    await self.save_user_to_db(connection, user_info)
                    await self.link_group_user(connection, group.id, user.id)

                    self.add_account_to_table(user_info)
                    self.accounts_list.append(user_info['id'])
                    logging.debug(f"Account added: {user_info['id']}")

                self.progress_bar_accounts.setValue(index + 1)

                # Після успішної обробки групи позначаємо її як оброблену
                self.groups_list_widget.mark_processed(index)

            except Exception as e:
                logging.error(f"Error processing group {group_link}: {e}")
                # Пропускаємо цю групу без зупинки програми
                continue

        self.status_label.setText(f"{self.translate('status')}: {self.translate('search_completed')}")
        logging.info("Account search completed.")

     except aiosqlite.OperationalError as db_error:
        self.tg_connected = False
        self.tg_light.set_state("off")
        self.status_label.setText(f"{self.translate('status')}: {db_error}")
        logging.error(f"Database error during group search: {db_error}")
        QMessageBox.critical(self, self.translate('error'), f"{self.translate('error')}: {db_error}")

     finally:
        await self.db_module.disconnect(connection)
        # Відновлюємо видимість кнопок
        self.search_accounts_button.setVisible(True)
        self.progress_bar_accounts.setVisible(False)
        self.pause_button_accounts.setVisible(False)
        self.stop_button_accounts.setVisible(False)
        self.pause_button_accounts.setText(self.translate('pause'))

    def get_user_status(self, status):
        if isinstance(status, UserStatusOnline):
           return 'Online'
        elif isinstance(status, UserStatusOffline):
           return f'Offline since {status.was_online.strftime("%Y-%m-%d %H:%M:%S")}'
        elif isinstance(status, UserStatusRecently):
           return 'Recently Online'
        elif isinstance(status, UserStatusLastWeek):
           return 'Last seen within a week'
        elif isinstance(status, UserStatusLastMonth):
           return 'Last seen within a month'
        else:
           return 'Unknown'

    def get_last_online(self, status):
        if isinstance(status, UserStatusOffline):
            return status.was_online.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return ''

    @database_activity_indicator
    async def save_group_to_db(self, connection, group_info):
     """Зберігає інформацію про групу в базу даних."""
     required_fields = ['id', 'title', 'username', 'date', 'participants_count', 'description', 'restricted', 'verified', 'megagroup', 'gigagroup', 'scam']
    
     # Перевірка наявності всіх необхідних полів
     for field in required_fields:
        if field not in group_info:
            group_info[field] = '' if field in ['title', 'username', 'description', 'date'] else False if field in ['restricted', 'verified', 'megagroup', 'gigagroup', 'scam'] else 0

     existing_group = await self.db_module.execute_query(connection, "SELECT * FROM groups WHERE id = ?", (group_info['id'],))
     if existing_group:
        update_query = """
            UPDATE groups
            SET title=?, username=?, date=?, participants_count=?, description=?, restricted=?, verified=?, megagroup=?, gigagroup=?, scam=?
            WHERE id=?
        """
        update_data = (
            group_info['title'], group_info['username'], group_info['date'],
            group_info['participants_count'], group_info['description'], group_info['restricted'],
            group_info['verified'], group_info['megagroup'], group_info['gigagroup'], group_info['scam'],
            group_info['id']
        )
        await self.db_module.execute_query(connection, update_query, update_data)
        logging.debug(self.translate('group_updated'))
     else:
        insert_query = """
            INSERT INTO groups (id, title, username, date, participants_count, description, restricted, verified, megagroup, gigagroup, scam)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        insert_data = (
            group_info['id'], group_info['title'], group_info['username'], group_info['date'],
            group_info['participants_count'], group_info['description'], group_info['restricted'],
            group_info['verified'], group_info['megagroup'], group_info['gigagroup'], group_info['scam']
        )
        await self.db_module.execute_query(connection, insert_query, insert_data)
        logging.debug(self.translate('group_added'))

    @database_activity_indicator
    async def save_user_to_db(self, connection, user_info):
     """Зберігає інформацію про користувача в базу даних."""
     existing_user = await self.db_module.execute_query(connection, "SELECT * FROM accounts WHERE id = ?", (user_info['id'],))
     if existing_user:
        update_query = """
            UPDATE accounts
            SET first_name=?, last_name=?, username=?, phone=?, status=?, bot=?, verified=?, restricted=?, scam=?, fake=?, access_hash=?, last_online=?
            WHERE id=?
        """
        update_data = (
            user_info['first_name'], user_info['last_name'], user_info['username'],
            user_info['phone'], user_info['status'], user_info['bot'], user_info['verified'],
            user_info['restricted'], user_info['scam'], user_info['fake'], user_info['access_hash'], user_info['last_online'],
            user_info['id']
        )
        await self.db_module.execute_query(connection, update_query, update_data)
        logging.debug(self.translate('account_updated'))
     else:
        insert_query = """
            INSERT INTO accounts (id, first_name, last_name, username, phone, status, bot, verified, restricted, scam, fake, access_hash, last_online)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        insert_data = (
            user_info['id'], user_info['first_name'], user_info['last_name'],
            user_info['username'], user_info['phone'], user_info['status'],
            user_info['bot'], user_info['verified'], user_info['restricted'],
            user_info['scam'], user_info['fake'], user_info['access_hash'], user_info['last_online']
        )
        await self.db_module.execute_query(connection, insert_query, insert_data)
        logging.debug(self.translate('account_added'))

    @database_activity_indicator
    async def link_group_user(self, connection, group_id, user_id):
        """Пов'язує групу та користувача в базі даних."""
        insert_relation_query = """
            INSERT OR IGNORE INTO group_user (group_id, user_id)
            VALUES (?, ?)
        """
        await self.db_module.execute_query(connection, insert_relation_query, (group_id, user_id))


    def add_account_to_table(self, user_info: Dict[str, Any]) -> None:
        """Додає знайдений акаунт до таблиці."""
        row_position = self.accounts_table.rowCount()
        self.accounts_table.insertRow(row_position)
        self.accounts_table.setItem(row_position, 0, QTableWidgetItem(str(user_info['id'])))
        self.accounts_table.setItem(row_position, 1, QTableWidgetItem(user_info['first_name']))
        self.accounts_table.setItem(row_position, 2, QTableWidgetItem(user_info['last_name']))
        self.accounts_table.setItem(row_position, 3, QTableWidgetItem(user_info['username']))
        self.accounts_table.setItem(row_position, 4, QTableWidgetItem(user_info['phone']))
        self.accounts_table.scrollToBottom()
        logging.debug(f"Account added: {user_info['id']}")
        # Оновлюємо кількість акаунтів у мітці
        self.accounts_status_label.setText(f"{self.translate('accounts')} ({len(self.accounts_list)}):")

    def extract_group_identifier(self, link):
        """
        Витягує ідентифікатор групи з посилання.
        Підтримує прямі посилання та запрошення.
        """
        try:
            if "t.me/joinchat/" in link:
                # Запрошення
                logging.debug(f"Group invitation: {link}")
                return link
            elif "t.me/" in link:
                # Пряме посилання на групу
                identifier = link.split("t.me/")[-1]
                logging.debug(f"Direct group link, identifier: {identifier}")
                return identifier
            else:
                # Можливо, це ID або щось інше
                logging.warning(f"Incorrect link format: {link}")
                return None
        except Exception as e:
            logging.error(f"Failed to extract group identifier from link {link}: {e}")
            return None

    def update_groups_list(self):
        """Оновлює список груп в інтерфейсі."""
        self.groups_list_widget.clear()
        for group in self.groups_list:
            item = QListWidgetItem(group)
            # Встановлюємо початковий колір шрифта, наприклад, білий
            initial_font_color = QColor(255, 255, 255)  # Білий колір
            item.setForeground(QBrush(initial_font_color))
            self.groups_list_widget.addItem(item)
        logging.debug(f"Groups list updated: {len(self.groups_list)} groups")
        # Оновлюємо кількість груп у мітці
        self.groups_status_label.setText(f"{self.translate('groups')} ({len(self.groups_list)}):")

    def dragEnterEvent(self, event):
        """Обробляє подію перетягування файлу над вікном."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            logging.debug("File dragged over the window.")
        else:
            event.ignore()

    @asyncSlot(list)
    async def process_dropped_files_slot(self, file_paths):
        """Обробляє перетягнуті файли."""
        logging.debug(f"Processing dropped files: {file_paths}")
        group_links = []
        for file_path in file_paths:
            try:
                links = self.extract_links_from_file(file_path)
                group_links.extend(links)
            except Exception as e:
                logging.error(f"Failed to process file {file_path}: {e}")
                QMessageBox.warning(self, self.translate('error'), f"Failed to process file {file_path}: {e}")
        # Видаляємо дублікати та додаємо нові групи
        new_links = set(group_links) - set(self.groups_list)
        if new_links:
            self.groups_list.extend(new_links)
            self.update_groups_list()
            self.status_label.setText(f"{self.translate('status')}: {self.translate('groups_added')}: {len(new_links)}.")
            logging.info(f"Groups added: {len(new_links)}")
        else:
            self.status_label.setText(f"{self.translate('status')}: {self.translate('groups_already_loaded')}")
            logging.info("No new groups to add.")

    def dropEvent(self, event):
        """Обробляє подію перетягування файлу у вікно."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            logging.debug(f"Files dropped: {file_paths}")
            self.process_dropped_files_slot(file_paths)
            event.acceptProposedAction()
        else:
            event.ignore()

    def extract_links_from_file(self, file_path):
        """Витягує посилання з файлу."""
        logging.debug(f"Processing file: {file_path}")
        ext = os.path.splitext(file_path)[1].lower()
        links = []

        try:
            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    links = [line.strip() for line in file if line.strip()]
            elif ext == '.csv':
                df = pd.read_csv(file_path)
                links = df.iloc[:, 0].astype(str).tolist()
            elif ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path)
                links = df.iloc[:, 0].astype(str).tolist()
            elif ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if isinstance(data, list):
                        links = data
                    elif isinstance(data, dict):
                        links = data.get('links', [])
            elif ext == '.pdf':
                reader = PdfReader(file_path)
                text = ''
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                links = [line.strip() for line in text.splitlines() if line.strip()]
            elif ext in ['.html', '.htm']:
                with open(file_path, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'lxml')
                    for a in soup.find_all('a', href=True):
                        link = a['href'].strip()
                        if link:
                            links.append(link)
            else:
                raise Exception(f"Unsupported file format: {ext}")
            logging.debug(f"Extracted links: {len(links)}")
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")
            raise e
        return links

    def closeEvent(self, event):
        """Обробляє подію закриття вікна."""
        asyncio.ensure_future(self.on_about_to_quit())
        event.accept()

    async def on_about_to_quit(self):
        """Асинхронное очищение перед ......"""
        self.stop_flag_accounts = True
        self.stop_flag_groups = True
        self.status_label.setText(f"{self.translate('status')}: {self.translate('process_stopped')}")
        logging.info(self.translate('process_stopped_on_exit'))

        # Відключення від Telegram
        if self.telegram_module:
            await self.telegram_module.disconnect()
            logging.info(self.translate('disconnected_from_telegram'))

        # Відключення від бази даних
        if self.db_module and self.connection:
            await self.db_module.disconnect(self.connection)
            logging.info(self.translate('disconnected_from_db'))
            self.connection = None  # Очистити з'єднання

    # Методи паузи та зупинки процесів (додайте відповідно до вашого коду)
    def pause_accounts_process(self):
        self.is_paused_accounts = not self.is_paused_accounts
        if self.is_paused_accounts:
            self.status_label.setText("Status: Accounts process paused.")
            logging.info("Accounts process paused.")
            self.pause_button_accounts.setText("▶️ Continue")
        else:
            self.status_label.setText("Status: Accounts process resumed.")
            logging.info("Accounts process resumed.")
            self.pause_button_accounts.setText("⏸ Пауза")
        # Логіка для паузи процесу акаунтів
        pass

    def stop_accounts_process(self):
        self.stop_flag_accounts = True
        self.status_label.setText("Status: Accounts process stopped.")
        logging.info("Accounts process stopped.")
        # Reset buttons visibility
        self.search_accounts_button.setVisible(True)
        self.progress_bar_accounts.setVisible(False)
        self.pause_button_accounts.setVisible(False)
        self.stop_button_accounts.setVisible(False)
        self.pause_button_accounts.setText("⏸ Пауза")
        # Логіка для зупинки процесу акаунтів
        pass

    def pause_groups_process(self):
        self.is_paused_groups = not self.is_paused_groups
        if self.is_paused_groups:
            self.status_label.setText("Status: Groups process paused.")
            logging.info("Groups process paused.")
            self.pause_button_groups.setText("▶️ Continue")
        else:
            self.status_label.setText("Status: Groups process resumed.")
            logging.info("Groups process resumed.")
            self.pause_button_groups.setText("⏸ Пауза")
        # Логіка для паузи процесу груп
        pass

    def stop_groups_process(self):
        self.stop_flag_groups = True
        self.status_label.setText("Status: Groups process stopped.")
        logging.info("Groups process stopped.")
        # Reset buttons visibility
        self.smart_search_button.setVisible(True)
        self.progress_bar_groups.setVisible(False)
        self.pause_button_groups.setVisible(False)
        self.stop_button_groups.setVisible(False)
        self.pause_button_groups.setText("⏸ Пауза")
        # Логіка для зупинки процесу груп
        pass

    def adjust_transparency(self, value):
        opacity = value / 100.0
        self.setWindowOpacity(opacity)

    def change_language(self, index):
        global current_language
        current_language = 'en' if index == 0 else 'uk'
        self.update_translations()

    def change_theme(self, index):
        global current_theme
        current_theme = 'hacker' if index == 0 else 'friendly'
        self.apply_theme()

    # Точка входа в приложение
if __name__ == "__main__":
    # Запуск главного цикла приложения
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Настройка логирования
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Инициализация модулей
    config_manager = ConfigManager()
    config_manager.load_config()

    db_module = DatabaseModule(
        host=config_manager.config.get('database', {}).get('host'),
        user=config_manager.config.get('database', {}).get('user'),
        password=config_manager.config.get('database', {}).get('password'),
        database=config_manager.config.get('database', {}).get('database')
    )
    telegram_module = TelegramModule(
        api_id=config_manager.config.get('telegram', {}).get('api_id'),
        api_hash=config_manager.config.get('telegram', {}).get('api_hash'),
        phone_number=config_manager.config.get('telegram', {}).get('phone_number')
    )

    # Попытка подключиться к базе данных
    loop.run_until_complete(db_module.connect())

    # Проверка начальных соединений
    db_connected = loop.run_until_complete(db_module.is_connected())
    tg_connected = False  # Будет обновлено после подключения к Telegram

    # Создание и отображение главного окна
    main_window = MainWindow(
        db_module=db_module,
        telegram_module=telegram_module,
        db_connected=db_connected,
        tg_connected=tg_connected,
        config_manager=config_manager
    )
    main_window.show()

    with loop:
        loop.run_forever()