#!/bin/bash

# Клонування репозиторію, якщо ще не клоновано
git clone git@github.com:oleg121203/MO.git || cd MO

# Переходимо в директорію репозиторію
cd MO

# Перевірка наявності змін
git pull

# Копіюємо нові файли
cp /mnt/data/gui_refactored_corrected.py .
cp /mnt/data/mdb1_database_corrected_v2.py .
cp /mnt/data/mt1_telegram_refactored_corrected.py .
cp /mnt/data/config_manager_corrected.py .
cp /mnt/data/main_corrected.py .

# Додаємо зміни до коміту
git add .

# Створюємо коміт із повідомленням
git commit -m "Updated corrected source files for main modules"

# Завантажуємо на сервер GitHub
git push origin main
