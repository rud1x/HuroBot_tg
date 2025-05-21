#!/bin/bash

# Цвета
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Анимация спиннера
spinner() {
    local pid=$!
    local delay=0.1
    local spinstr='⣾⣽⣻⢿⡿⣟⣯⣷'
    
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Заголовок
clear
echo -e "${CYAN}"
echo "╔══════════════════════════════╗"
echo "║    Установка HURObot         ║"
echo "╚══════════════════════════════╝"
echo -e "\nTG - @hurodev\n"
echo -e "${NC}"

# Удаление старых версий
(rm -rf ~/hurobot 2>/dev/null) & spinner

# Обновление системы
(pkg update -y >/dev/null 2>&1 && pkg upgrade -y >/dev/null 2>&1) & spinner
echo -e "\n${GREEN}✓ Система обновлена${NC}"

# Установка зависимостей
(pkg install -y python git libjpeg-turbo openssl >/dev/null 2>&1) & spinner
echo -e "${GREEN}✓ Зависимости установлены${NC}"

# Python-библиотеки
(pip install -q --upgrade pip wheel >/dev/null 2>&1) & spinner
(pip install -q telethon requests pillow python-whois pytz >/dev/null 2>&1) & spinner
echo -e "${GREEN}✓ Библиотеки Python готовы${NC}"

# Клонирование репозитория
(git clone -q https://github.com/rud1x/HuroBot_tg.git ~/hurobot >/dev/null 2>&1) & spinner
echo -e "${GREEN}✓ Бот загружен${NC}"

# Настройка алиаса
echo -e "alias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc
source ~/.bashrc >/dev/null 2>&1

# Инструкция
echo -e "\n${CYAN}═══════════════════════════════════════════════════"
echo -e "✅ Установка успешно завершена!"
echo -e "═══════════════════════════════════════════════════${NC}"
echo -e "\nДля запуска бота используйте команду:"
echo -e "   ${YELLOW}hurobot${NC}"

