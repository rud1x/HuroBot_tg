#!/bin/bash

# Фиолетовые цвета
PURPLE='\033[0;35m'
DARK_PURPLE='\033[1;35m'
NC='\033[0m'

# Анимация спиннера
spinner() {
    local pid=$!
    local spin=('⣾' '⣽' '⣻' '⢿' '⡿' '⣟' '⣯' '⣷')
    while kill -0 $pid 2>/dev/null; do
        for i in "${spin[@]}"; do
            printf "${PURPLE}%s${NC}" "$i"
            sleep 0.1
            printf "\b"
        done
    done
    printf " \b"
}

# Заголовок
clear
echo -e "${DARK_PURPLE}"
echo "╔════════════════════════════════════╗"
echo "║         Установщик HURObot         ║"
echo "╚════════════════════════════════════╝"
echo -e "${NC}"

# 1. Исправление окружения Termux
printf "${PURPLE}• Исправляем окружение Termux...${NC}"
{
pkg uninstall curl libcurl -y >/dev/null 2>&1
pkg install -y termux-exec curl libcurl python git libjpeg-turbo openssl >/dev/null 2>&1
termux-exec >/dev/null 2>&1
export LD_LIBRARY_PATH=$PREFIX/lib >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# 2. Клонирование репозитория
printf "${PURPLE}• Загружаем HURObot...${NC}"
{
rm -rf ~/hurobot 2>/dev/null
git clone -q https://github.com/rud1x/HuroBot_tg.git ~/hurobot 2>/dev/null
} & spinner
printf "\b✓\n"

# 3. Установка зависимостей из requirements.txt
printf "${PURPLE}• Устанавливаем зависимости...${NC}"
{
cd ~/hurobot
python -m pip install --upgrade pip wheel >/dev/null 2>&1

# Проверяем наличие requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt >/dev/null 2>&1 || {
        # Если не получилось установить все сразу, пробуем по одной
        while read lib; do
            [ -n "$lib" ] && pip install "$lib" >/dev/null 2>&1
        done < requirements.txt
    }
else
    # Базовые библиотеки, если файл не найден
    pip install requests telethon pillow python-whois pytz >/dev/null 2>&1
fi
} & spinner
printf "\b✓\n"

# 4. Настройка алиаса
printf "${PURPLE}• Настраиваем команду...${NC}"
{
echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc
source ~/.bashrc >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Завершение
echo -e "\n${DARK_PURPLE}╔════════════════════════════════════╗"
echo "║       Установка завершена!       ║"
echo "╚════════════════════════════════════╝${NC}"
echo -e "Для запуска: hurobot"
