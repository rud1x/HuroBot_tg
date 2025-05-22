#!/bin/bash

# Фиолетовая цветовая схема
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
pkg install -y termux-exec curl libcurl python git libjpeg-turbo openssl
termux-exec
export LD_LIBRARY_PATH=$PREFIX/lib
} >/dev/null 2>&1 & spinner
printf "\b✓\n"

# 2. Получение requirements.txt (3 попытки)
printf "${PURPLE}• Загружаем список библиотек...${NC}"
for i in {1..3}; do
    if curl -sL "https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/requirements.txt" -o /tmp/huro_req.txt; then
        break
    elif [ $i -eq 3 ]; then
        echo -e "\n${DARK_PURPLE}Не удалось загрузить requirements.txt, используем базовые библиотеки${NC}"
        echo "requests" > /tmp/huro_req.txt
        echo "telethon" >> /tmp/huro_req.txt
        echo "pillow" >> /tmp/huro_req.txt
    fi
    sleep 2
done & spinner
printf "\b✓\n"

# 3. Установка Python-зависимостей (с повтором)
printf "${PURPLE}• Устанавливаем Python-библиотеки...${NC}"
{
python -m pip install --upgrade pip wheel >/dev/null 2>&1

# Первая попытка
pip install -r /tmp/huro_req.txt >/dev/null 2>&1

# Вторая попытка для проблемных библиотек
grep -v "^#" /tmp/huro_req.txt | while read lib; do
    pip install --no-cache-dir "$lib" >/dev/null 2>&1 || \
    pip install --ignore-installed "$lib" >/dev/null 2>&1
done
} & spinner
printf "\b✓\n"

# 4. Установка бота
printf "${PURPLE}• Загружаем HURObot...${NC}"
{
rm -rf ~/hurobot 2>/dev/null
git clone -q https://github.com/rud1x/HuroBot_tg.git ~/hurobot
} & spinner
printf "\b✓\n"

# Финал
echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc
source ~/.bashrc

echo -e "\n${DARK_PURPLE}╔════════════════════════════════════╗"
echo "║       Установка завершена!       ║"
echo "╚════════════════════════════════════╝${NC}"
echo -e "\n${PURPLE}Для запуска: ${DARK_PURPLE}hurobot${NC}"
