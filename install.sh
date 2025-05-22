#!/bin/bash

# Фиолетовая цветовая схема
PURPLE='\033[0;35m'
DARK_PURPLE='\033[1;35m'
NC='\033[0m'

# Функция для надежной установки пакетов
safe_install() {
    for pkg in "$@"; do
        printf "${PURPLE}• Устанавливаем $pkg...${NC}"
        while ! pkg install -y $pkg >/dev/null 2>&1; do
            sleep 1
        done
        printf "\b✓\n"
    done
}

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
echo "║         Установщик HURObot          ║"
echo "╚════════════════════════════════════╝"
echo -e "${NC}"

# Основная установка
printf "${PURPLE}• Исправляем окружение Termux...${NC}"
pkg uninstall curl libcurl -y >/dev/null 2>&1
safe_install termux-exec curl libcurl python git libjpeg-turbo openssl
termux-exec
export LD_LIBRARY_PATH=$PREFIX/lib
printf "\b✓\n"

# Установка Python-зависимостей
printf "${PURPLE}• Обновляем pip...${NC}"
python -m pip install --upgrade pip wheel >/dev/null 2>&1 & spinner
printf "\b✓\n"

# Основные библиотеки (дублируем в самом скрипте на случай проблем)
LIBS=("requests" "telethon" "pillow" "python-whois" "pytz")
for lib in "${LIBS[@]}"; do
    printf "${PURPLE}• Устанавливаем $lib...${NC}"
    pip install -q $lib >/dev/null 2>&1 & spinner
    printf "\b✓\n"
done

# Установка бота
printf "${PURPLE}• Загружаем HURObot...${NC}"
rm -rf ~/hurobot 2>/dev/null
git clone -q https://github.com/rud1x/HuroBot_tg.git ~/hurobot & spinner
printf "\b✓\n"

# Настройка алиаса
echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc
source ~/.bashrc

# Проверка установки
echo -e "\n${DARK_PURPLE}╔════════════════════════════════════╗"
echo "║      Установка завершена!          ║"
echo "╚════════════════════════════════════╝${NC}"
echo -e "Проверяем установленные библиотеки:"
pip list | grep -E 'requests|telethon|pillow|python-whois|pytz'
echo -e "\n${PURPLE}Для запуска: ${DARK_PURPLE}hurobot${NC}"
