#!/bin/bash

# Фиолетовые цвета
PURPLE='\033[0;35m'
DARK_PURPLE='\033[1;35m'
LIGHT_PURPLE='\033[1;95m'
NC='\033[0m'

# Анимация спиннера (улучшенная)
spinner() {
    local pid=$!
    local delay=0.15
    local spinstr='⣷⣯⣟⡿⢿⣻⣽⣾'
    
    while kill -0 $pid 2>/dev/null; do
        for i in {0..7}; do
            printf "${PURPLE}%s${NC}" "${spinstr:$i:1}"
            sleep $delay
            printf "\b"
        done
    done
    printf " \b"
}

# Тихий режим для ошибок
exec 2>/dev/null

# Заголовок
clear
echo -e "${DARK_PURPLE}"
echo "╔════════════════════════════════════╗"
echo "║      Установщик HURObot            ║"
echo "╚════════════════════════════════════╝"
echo -e "${NC}"

# Шаги установки с анимацией
steps=(
    "Настройка Termux"
    "Обновление системы"
    "Установка зависимостей"
    "Загрузка библиотек"
    "Установка Python-пакетов"
    "Загрузка HURObot"
    "Настройка команд"
)

commands=(
    "pkg install -y termux-exec && termux-exec"
    "pkg update -y && pkg upgrade -y"
    "pkg install -y curl python git libjpeg-turbo openssl"
    "curl -sL https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/requirements.txt -o /tmp/huro_req.txt"
    "pip install -q --upgrade pip wheel && pip install -q -r /tmp/huro_req.txt"
    "rm -rf ~/hurobot && git clone -q https://github.com/rud1x/HuroBot_tg.git ~/hurobot"
    "echo -e \"\nalias hurobot='cd ~/hurobot && python hurobot.py'\" >> ~/.bashrc && source ~/.bashrc"
)

for i in "${!steps[@]}"; do
    printf "${PURPLE}• ${steps[$i]}...${NC}"
    eval "${commands[$i]}" >/dev/null & spinner
    printf "\b✓\n"
done

# Итоговое сообщение
echo -e "\n${DARK_PURPLE}╔════════════════════════════════════╗"
echo "║      Установка завершена успешно!     ║"
echo "╚════════════════════════════════════╝${NC}"
echo -e "${LIGHT_PURPLE}Для запуска: ${PURPLE}hurobot${NC}"
echo -e "${LIGHT_PURPLE}Если не работает: ${PURPLE}source ~/.bashrc${NC}\n"
