#!/bin/bash

# Удаление старых версий
rm -rf ~/hurobot &>/dev/null
sed -i '/alias hurobot/d' ~/.bashrc &>/dev/null

# Установка пакетов
pkg update -y
pkg install -y python git libjpeg-turbo libcrypt
pip install --upgrade pip wheel

# Установка зависимостей
yes | pip install telethon requests pillow python-whois pytz

# Клонирование репозитория
git clone --depth 1 https://github.com/rud1x/HuroBot_tg.git ~/hurobot

# Создание алиаса
echo 'alias hurobot="cd ~/hurobot && python hurobot.py"' >> ~/.bashrc
source ~/.bashrc

# Первый запуск
cd ~/hurobot && python hurobot.py
