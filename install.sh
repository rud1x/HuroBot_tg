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

# 1. Исправление окружения
printf "${PURPLE}• Исправляем окружение Termux...${NC}"
{
pkg uninstall curl libcurl -y >/dev/null 2>&1
pkg install -y termux-exec curl libcurl python git libjpeg-turbo openssl >/dev/null 2>&1
termux-exec >/dev/null 2>&1
export LD_LIBRARY_PATH=$PREFIX/lib >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# 2. Получение requirements.txt
printf "${PURPLE}• Загружаем список библиотек...${NC}"
REQ_FILE="/data/data/com.termux/files/usr/tmp/huro_req.txt"
if ! curl -sL "https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/requirements.txt" -o "$REQ_FILE" 2>/dev/null; then
    printf "\n${PURPLE}Используем базовые библиотеки...${NC}"
    echo "requests" > "$REQ_FILE"
    echo "telethon" >> "$REQ_FILE"
    echo "pillow" >> "$REQ_FILE"
    echo "python-whois" >> "$REQ_FILE"
    echo "pytz" >> "$REQ_FILE"
fi & spinner
printf "\b✓\n"

# 3. Установка Python-зависимостей
printf "${PURPLE}• Устанавливаем Python-библиотеки...${NC}"
{
python -m pip install --upgrade pip wheel >/dev/null 2>&1
pip install -r "$REQ_FILE" >/dev/null 2>&1 || \
while read lib; do
    [ -n "$lib" ] && pip install "$lib" >/dev/null 2>&1
done < "$REQ_FILE"
} & spinner
printf "\b✓\n"

# 4. Установка бота
printf "${PURPLE}• Загружаем HURObot...${NC}"
{
rm -rf ~/hurobot 2>/dev/null
git clone -q https://github.com/rud1x/HuroBot_tg.git ~/hurobot 2>/dev/null
} & spinner
printf "\b✓\n"

# Финал
echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc
source ~/.bashrc >/dev/null 2>&1

echo -e "\n${DARK_PURPLE}╔════════════════════════════════════╗"
echo "║       Установка завершена!       ║"
echo "╚════════════════════════════════════╝${NC}"
echo -e "Для запуска: hurobot"
