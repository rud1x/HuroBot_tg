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
git clone https://github.com/rud1x/HuroBot_tg.git ~/hurobot >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# 3. Установка зависимостей
printf "${PURPLE}• Устанавливаем зависимости...${NC}"
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
printf "${PURPLE}• Настраиваем команду...${NC}"
{
echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc
source ~/.bashrc >/dev/null 2>&1
} & spinner
printf "\b✓\n"

# Завершение
echo -e "\n${DARK_PURPLE}╔════════════════════════════════════╗"
echo "║         Установка завершена!       ║"
echo "╚════════════════════════════════════╝"
echo -e "Для запуска: ${DARK_PURPLE}hurobot${NC}"
