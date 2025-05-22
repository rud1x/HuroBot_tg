#!/bin/bash

# Фиолетовые цвета
PURPLE='\033[0;35m'
DARK_PURPLE='\033[1;35m'
NC='\033[0m'

# Функция для обработки ошибок
error_exit() {
    echo -e "${DARK_PURPLE}✗ Ошибка: $1${NC}" >&2
    exit 1
}

# Улучшенный спиннер
spinner() {
    local pid=$!
    local delay=0.15
    local spinstr='⣾⣽⣻⢿⡿⣟⣯⣷'
    
    while kill -0 $pid 2>/dev/null; do
        for i in {0..7}; do
            printf "${PURPLE}%s${NC}" "${spinstr:$i:1}"
            sleep $delay
            printf "\b"
        done
    done
    printf " \b"
}

# Заголовок
clear
echo -e "${DARK_PURPLE}"
echo "╔════════════════════════════════════╗"
echo "║      УСТАНОВЩИК HURObot PRO        ║"
echo "╚════════════════════════════════════╝"
echo -e "${NC}"

# Шаг 1: Восстановление окружения Termux
printf "${PURPLE}• Восстановление окружения Termux...${NC}"
{
    pkg install -y termux-tools termux-exec >/dev/null 2>&1
    termux-exec
    export LD_PRELOAD=$PREFIX/lib/libtermux-exec.so
} & spinner
printf "\b✓\n"

# Шаг 2: Полная переустановка curl и зависимостей
printf "${PURPLE}• Исправление системных библиотек...${NC}"
{
    pkg uninstall -y curl libcurl >/dev/null 2>&1
    pkg install -y libcurl curl >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Шаг 3: Обновление системы
printf "${PURPLE}• Обновление пакетов...${NC}"
{
    pkg update -y >/dev/null 2>&1
    pkg upgrade -y >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Шаг 4: Установка базовых зависимостей
printf "${PURPLE}• Установка зависимостей...${NC}"
{
    pkg install -y python git wget libjpeg-turbo openssl >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Шаг 5: Альтернативная загрузка requirements.txt
printf "${PURPLE}• Получение списка библиотек...${NC}"
{
    if command -v wget >/dev/null; then
        wget -q https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/requirements.txt -O /tmp/huro_req.txt
    else
        curl -s -o /tmp/huro_req.txt https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/requirements.txt
    fi
} & spinner
printf "\b✓\n"

# Шаг 6: Установка Python-библиотек
printf "${PURPLE}• Установка Python-пакетов...${NC}"
{
    pip install --upgrade pip wheel >/dev/null 2>&1
    pip install -r /tmp/huro_req.txt >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Шаг 7: Клонирование репозитория
printf "${PURPLE}• Загрузка HURObot...${NC}"
{
    rm -rf ~/hurobot 2>/dev/null
    git clone -q https://github.com/rud1x/HuroBot_tg.git ~/hurobot
} & spinner
printf "\b✓\n"

# Шаг 8: Настройка алиаса
printf "${PURPLE}• Настройка команды...${NC}"
{
    echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc
    source ~/.bashrc >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Завершение
echo -e "\n${DARK_PURPLE}╔════════════════════════════════════╗"
echo "║          УСТАНОВКА ЗАВЕРШЕНА         ║"
echo "╚════════════════════════════════════╝${NC}"
echo -e "${PURPLE}Для запуска: ${DARK_PURPLE}hurobot${NC}"
echo -e "${PURPLE}Если не работает: ${DARK_PURPLE}exec bash${NC}"
