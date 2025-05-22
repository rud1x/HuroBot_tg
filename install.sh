#!/bin/bash

# Фиолетовые цвета
WW='\033[97m'
RED='\033[91m'
NC='\033[0m'
RZ= '\033[90m'
# Анимация спиннера
spinner() {
    local pid=$!
    local spin=('⣾' '⣽' '⣻' '⢿' '⡿' '⣟' '⣯' '⣷')
    while kill -0 $pid 2>/dev/null; do
        for i in "${spin[@]}"; do
            printf "${WW}%s${NC}" "$i"
            sleep 0.1
            printf "\b"
        done
    done
    printf " \b"
}

# Заголовок
clear

echo "${RED}                __    ___  ___    ___  _____  ${WW}  _____    __  __  _____  _      __    __  __ "
echo "${RED}  /\  /\/\ /\  /__\  /___\/ __\  /___\/__   \ ${WW}  \_   \/\ \ \/ _\/__   \/_\    / /   /__\/__\"
echo "${RED} / /_/ / / \ \/ \// //  //__\// //  //  / /\/ ${WW}   / /\/  \/ /\ \   / /\//_\\  / /   /_\ / \//"
echo "${RED}/ __  /\ \_/ / _  \/ \_// \/  \/ \_//  / /    ${WW}/\/ /_/ /\  / _\ \ / / /  _  \/ /___//__/ _  \"
echo "${RED}\/ /_/  \___/\/ \_/\___/\_____/\___/   \/     ${WW}\____/\_\ \/  \__/ \/  \_/ \_/\____/\__/\/ \_/"                                                                               
echo "\nТелеграмм канал:${WW}@hurodev${RED}/n" 
echo "${RZ}--------------------------------------------------${NC}"

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

# Проверяем наличие requirements.txt
if [ -f "requirements.txt" ]; then
    # Устанавливаем все зависимости
    pip install -r requirements.txt >/dev/null 2>&1
    
    # Проверяем каждую библиотеку отдельно
    while read -r lib; do
        # Пропускаем пустые строки и комментарии
        [[ -z "$lib" || "$lib" == "#"* ]] && continue
        
        # Удаляем версии из названия (если есть)
        clean_lib=$(echo "$lib" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1)
        
        # Проверяем установлена ли библиотека
        if ! pip show "$clean_lib" >/dev/null 2>&1; then
            pip install "$lib" >/dev/null 2>&1
        fi
    done < requirements.txt
else
    # Базовые библиотеки, если файл не найден
    pip install requests telethon pillow python-whois pytz >/dev/null 2>&1
fi
} & spinner
printf "\b✓\n"

# 4. Настройка алиаса
printf "${RED}[+]${WW} Настраиваем команду...${NC}"
{
echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc
source ~/.bashrc >/dev/null 2>&1
} & spinner
printf "\b✓\n"

clear

echo "${RED}                __    ___  ___    ___  _____  ${WW}  _____    __  __  _____  _      __    __  __ "
echo "${RED}  /\  /\/\ /\  /__\  /___\/ __\  /___\/__   \ ${WW}  \_   \/\ \ \/ _\/__   \/_\    / /   /__\/__\"
echo "${RED} / /_/ / / \ \/ \// //  //__\// //  //  / /\/ ${WW}   / /\/  \/ /\ \   / /\//_\\  / /   /_\ / \//"
echo "${RED}/ __  /\ \_/ / _  \/ \_// \/  \/ \_//  / /    ${WW}/\/ /_/ /\  / _\ \ / / /  _  \/ /___//__/ _  \"
echo "${RED}\/ /_/  \___/\/ \_/\___/\_____/\___/   \/     ${WW}\____/\_\ \/  \__/ \/  \_/ \_/\____/\__/\/ \_/"                                                                                      
echo "\nТелеграмм канал:${WW}@hurodev${RED}\n" 
echo "${RZ}--------------------------------------------------${NC}"
echo "ㅤㅤㅤ${RED}Установка завершена!${NC}"
echo "ㅤㅤㅤДля запуска: ${RED}hurobot${NC}"
