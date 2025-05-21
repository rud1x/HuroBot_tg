#!/bin/bash

# Установка зависимостей
pkg update -y
pkg install -y git python
pip install --upgrade pip
pip install telethon requests pillow python-whois pytz

# Клонирование репозитория
git clone https://github.com/rud1x/HuroBot_tg.git ~/hurobot

# Создание алиаса
echo 'alias hurobot="cd ~/hurobot && python hurobot.py"' >> ~/.bashrc
source ~/.bashrc

# Первый запуск
cd ~/hurobot && python hurobot.py