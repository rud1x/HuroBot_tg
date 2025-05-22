#!/bin/bash

WW=$(tput setaf 7)
RED=$(tput setaf 1)
RZ=$(tput setaf 8)
NC=$(tput sgr0)

# Анимация спиннера (исправленная версия)
spinner() {
    local pid=$!
    local spin=('⣾' '⣽' '⣻' '⢿' '⡿' '⣟' '⣯' '⣷')
    local i=0
    tput civis # Скрываем курсор
    while kill -0 "$pid" 2>/dev/null; do
        printf "%s" "${RED}${spin[i]}${NC}"
        sleep 0.1
        printf "\b"
        i=$(( (i+1) % 8 ))
    done
    tput cnorm # Восстанавливаем курсор
    printf " \b"
}

# Очистка экрана и вывод заголовка
clear

echo -e "${RED}                __    ___  ___    ___  _____  ${WW}  _____    __  __  _____  _      __    __  __ "
echo -e "${RED}  /\  /\/\ /\  /__\  /___\/ __\  /___\/__   \ ${WW}  \_   \/\ \ \/ _\/__   \/_\    / /   /__\/__\\"
echo -e "${RED} / /_/ / / \ \/ \// //  //__\// //  //  / /\/ ${WW}   / /\/  \/ /\ \   / /\//_\\\\  / /   /_\ / \//"
echo -e "${RED}/ __  /\ \_/ / _  \/ \_// \/  \/ \_//  / /    ${WW}/\/ /_/ /\  / _\ \ / / /  _  \/ /___//__/ _  \\"
echo -e "${RED}\/ /_/  \___/\/ \_/\___/\_____/\___/   \/     ${WW}\____/\_\ \/  \__/ \/  \_/ \_/\____/\__/\/ \_/${NC}"                                                                                      
echo -e "\nТелеграмм канал: ${RED}@hurodev${NC}"
echo -e "${RZ}-----------------------------------------------------------------------------------------------${NC}"

# 1. Исправление окружения Termux
printf "${RED}[+]${WW} Исправляем окружение Termux...${NC}"
{
    pkg uninstall curl libcurl -y >/dev/null 2>&1
    pkg install -y termux-exec curl libcurl python git libjpeg-turbo openssl >/dev/null 2>&1
    termux-exec >/dev/null 2>&1
    export LD_LIBRARY_PATH=$PREFIX/lib >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# 2. Клонирование репозитория
printf "${RED}[+]${WW} Загружаем HURObot...${NC}"
{
    rm -rf ~/hurobot 2>/dev/null
    git clone https://github.com/rud1x/HuroBot_tg.git ~/hurobot >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# 3. Установка зависимостей
printf "${RED}[+]${WW} Устанавливаем зависимости...${NC}"
{
    cd ~/hurobot 2>/dev/null
    python -m pip install --upgrade pip wheel >/dev/null 2>&1

    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt >/dev/null 2>&1
        
        while read -r lib; do
            [[ -z "$lib" || "$lib" == "#"* ]] && continue
            clean_lib=$(echo "$lib" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1)
            
            if ! pip show "$clean_lib" >/dev/null 2>&1; then
                pip install "$lib" >/dev/null 2>&1
            fi
        done < requirements.txt
    else
        pip install requests telethon pillow python-whois pytz >/dev/null 2>&1
    fi
} & spinner
printf "\b✓\n"

# 4. Настройка алиаса
printf "${RED}[+]${WW} Настраиваем команду...${NC}"
{
    if ! grep -q "alias hurobot=" ~/.bashrc; then
        echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc
    fi
    source ~/.bashrc >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Финал установки
clear

echo -e "${RED}                __    ___  ___    ___  _____  ${WW}  _____    __  __  _____  _      __    __  __ "
echo -e "${RED}  /\  /\/\ /\  /__\  /___\/ __\  /___\/__   \ ${WW}  \_   \/\ \ \/ _\/__   \/_\    / /   /__\/__\\"
echo -e "${RED} / /_/ / / \ \/ \// //  //__\// //  //  / /\/ ${WW}   / /\/  \/ /\ \   / /\//_\\\\  / /   /_\ / \//"
echo -e "${RED}/ __  /\ \_/ / _  \/ \_// \/  \/ \_//  / /    ${WW}/\/ /_/ /\  / _\ \ / / /  _  \/ /___//__/ _  \\"
echo -e "${RED}\/ /_/  \___/\/ \_/\___/\_____/\___/   \/     ${WW}\____/\_\ \/  \__/ \/  \_/ \_/\____/\__/\/ \_/${NC}"                                                                                      
echo -e "\nТелеграмм канал: ${RED}@hurodev${NC}"
echo -e "${RZ}-----------------------------------------------------------------------------------------------${NC}"
echo -e "ㅤㅤㅤ${RED}Установка завершена!${NC}"
echo -e "ㅤㅤㅤДля запуска введите: ${RED}hurobot${NC}"
echo -e "${RZ}-----------------------------------------------------------------------------------------------${NC}"
echo -e "${RZ}* Если команда не работает, выполните: source ~/.bashrc ${NC}"
