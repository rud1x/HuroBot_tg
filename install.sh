#!/bin/bash

# Удаление старых версий
rm -rf ~/hurobot 2>/dev/null

# Обновление системы
echo "🔄 Обновление пакетов..."
pkg update -y -q && pkg upgrade -y -q

# Установка зависимостей
echo "📦 Установка компонентов..."
pkg install -y -q python git libjpeg-turbo openssl

# Python-библиотеки
echo "🐍 Установка библиотек..."
pip install -q --upgrade pip wheel
pip install -q telethon requests pillow python-whois pytz

# Клонирование репозитория
echo "📥 Загрузка бота..."
git clone -q https://github.com/rud1x/HuroBot_tg.git ~/hurobot

# Настройка алиаса
echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'\nsource ~/.bashrc" >> ~/.bashrc
exec bash -c "cd ~/hurobot && python hurobot.py"

# Инструкция
echo -e "\n\033[1;32m✅ Установка завершена!\033[0m"
echo -e "Для запуска бота введите: \033[1;36mhurobot\033[0m"
echo -e "Если команда не работает, сначала выполните: \033[1;33msource ~/.bashrc\033[0m\n"
