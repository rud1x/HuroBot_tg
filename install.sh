#!/bin/bash

# Фиолетовые цвета
PURPLE='\033[0;35m'
DARK_PURPLE='\033[1;35m'
LIGHT_PURPLE='\033[1;95m'
NC='\033[0m'

# Функция для обработки ошибок
error_exit() {
    echo -e "${DARK_PURPLE}ОШИБКА: $1${NC}" >&2
    exit 1
}

# Упрощенный спиннер
spinner() {
    local pid=$!
    local delay=0.1
    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    
    while kill -0 $pid 2>/dev/null; do
        for i in {0..9}; do
            printf "\b${spinstr:$i:1}"
            sleep $delay
        done
    done
    printf "\b "
}

# Заголовок
clear
echo -e "${DARK_PURPLE}"
echo "╔════════════════════════════════════╗"
echo "║      УСТАНОВЩИК HURObot            ║"
echo "╚════════════════════════════════════╝"
echo -e "${NC}"

# Проверка интернета
printf "${PURPLE}• Проверка подключения...${NC}"
if ! ping -c 1 google.com >/dev/null 2>&1; then
    error_exit "Нет интернета"
fi
printf "\b✓\n"

# Фикс для Termux
printf "${PURPLE}• Настройка Termux...${NC}"
{
    pkg install -y termux-exec libpcre2 >/dev/null 2>&1 && \
    termux-exec >/dev/null 2>&1 && \
    export LD_PRELOAD=$PREFIX/lib/libtermux-exec.so >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Обновление пакетов
printf "${PURPLE}• Обновление системы...${NC}"
{
    pkg update -y >/dev/null 2>&1 && \
    pkg upgrade -y >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Установка зависимостей
printf "${PURPLE}• Установка зависимостей...${NC}"
{
    pkg install -y python git wget libjpeg-turbo openssl >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Обновление pip
printf "${PURPLE}• Обновление pip...${NC}"
{
    pip install --upgrade pip wheel >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Загрузка requirements.txt
printf "${PURPLE}• Загрузка библиотек...${NC}"
{
    wget -q https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/requirements.txt -O /tmp/hurobot_req.txt 2>/dev/null || \
    curl -s -o /tmp/hurobot_req.txt https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/requirements.txt 2>/dev/null
} & spinner
printf "\b✓\n"

# Установка Python-библиотек
printf "${PURPLE}• Установка Python-пакетов...${NC}"
{
    pip install -r /tmp/hurobot_req.txt >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Клонирование репозитория
printf "${PURPLE}• Загрузка HURObot...${NC}"
{
    rm -rf ~/hurobot 2>/dev/null && \
    git clone -q https://github.com/rud1x/HuroBot_tg.git ~/hurobot 2>/dev/null
} & spinner
printf "\b✓\n"

# Настройка алиаса
printf "${PURPLE}• Настройка команд...${NC}"
{
    echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc && \
    source ~/.bashrc >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Завершение
echo -e "\n${DARK_PURPLE}╔════════════════════════════════════╗"
echo -e "║          УСТАНОВКА ЗАВЕРШЕНА         ║"
echo -e "╚════════════════════════════════════╝${NC}"
echo -e "${LIGHT_PURPLE}Команда для запуска: ${PURPLE}hurobot${NC}"
echo -e "${LIGHT_PURPLE}Если не работает: ${PURPLE}source ~/.bashrc${NC}\n"
