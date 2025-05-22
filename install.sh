#!/bin/bash

# Цвета
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m'

# Функция для обработки ошибок
error_exit() {
    echo -e "${RED}ОШИБКА: $1${NC}" >&2
    exit 1
}

# Упрощенный спиннер
spinner() {
    local pid=$!
    local delay=0.1
    local spinstr='|/-\'
    
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
echo "╔════════════════════════════════════╗"
echo "║      Установщик HURObot PRO        ║"
echo "╚════════════════════════════════════╝"
echo -e "TG - @hurodev\n${NC}"

# Проверка интернета
echo -e "${YELLOW}Проверка подключения к интернету...${NC}"
if ! ping -c 1 google.com >/dev/null 2>&1; then
    error_exit "Требуется интернет-соединение!"
fi

# Фикс для Termux
echo -e "\n${YELLOW}Настройка окружения Termux...${NC}"
{
    pkg install -y termux-exec libpcre2 && \
    termux-exec && \
    export LD_PRELOAD=$PREFIX/lib/libtermux-exec.so
} >/dev/null 2>&1 & spinner || error_exit "Ошибка настройки Termux!"

# Обновление пакетов
echo -e "\n${YELLOW}Обновление системы...${NC}"
{
    pkg update -y && \
    pkg upgrade -y
} >/dev/null 2>&1 & spinner || error_exit "Ошибка обновления пакетов!"
echo -e "${GREEN}✓ Система обновлена${NC}"

# Установка основных зависимостей
echo -e "\n${YELLOW}Установка зависимостей...${NC}"
{
    pkg install -y python git wget libjpeg-turbo openssl grep
} >/dev/null 2>&1 & spinner || error_exit "Ошибка установки зависимостей!"
echo -e "${GREEN}✓ Зависимости установлены${NC}"

# Установка Python-библиотек
echo -e "\n${YELLOW}Обновление pip...${NC}"
{
    pip install --upgrade pip wheel
} >/dev/null 2>&1 & spinner || error_exit "Ошибка обновления pip!"

# Загрузка requirements.txt из репозитория
echo -e "\n${YELLOW}Загрузка списка библиотек...${NC}"
{
    wget -q https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/requirements.txt -O /tmp/hurobot_requirements.txt || \
    curl -s -o /tmp/hurobot_requirements.txt https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/requirements.txt
} & spinner || error_exit "Ошибка загрузки requirements.txt!"

# Установка библиотек из requirements.txt
echo -e "\n${YELLOW}Установка Python-библиотек...${NC}"
{
    pip install -r /tmp/hurobot_requirements.txt
} >/dev/null 2>&1 & spinner || error_exit "Ошибка установки библиотек!"
echo -e "${GREEN}✓ Библиотеки Python установлены${NC}"

# Клонирование репозитория
echo -e "\n${YELLOW}Загрузка HURObot...${NC}"
{
    rm -rf ~/hurobot 2>/dev/null && \
    git clone -q https://github.com/rud1x/HuroBot_tg.git ~/hurobot
} & spinner || error_exit "Ошибка загрузки бота!"
echo -e "${GREEN}✓ Бот успешно загружен${NC}"

# Настройка алиаса
echo -e "\n${YELLOW}Настройка алиаса...${NC}"
{
    echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc && \
    source ~/.bashrc
} >/dev/null 2>&1 & spinner || error_exit "Ошибка настройки алиаса!"
echo -e "${GREEN}✓ Алиас настроен${NC}"

# Завершение
echo -e "\n${CYAN}✅ Установка успешно завершена!${NC}"
echo -e "Для запуска бота используйте команду:"
echo -e "   ${YELLOW}hurobot${NC}"
echo -e "\nЕсли команда не работает, выполните:"
echo -e "   ${YELLOW}source ~/.bashrc${NC}"
echo -e "или перезапустите Termux"
