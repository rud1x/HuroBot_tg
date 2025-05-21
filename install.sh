#!/bin/bash

# Цвета и анимации
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
NC='\033[0m'
spinner=('⣾' '⣽' '⣻' '⢿' '⡿' '⣟' '⣯' '⣷')

# Функция для анимации спиннера
show_spinner() {
  local pid=$!
  local i=0
  while kill -0 $pid 2>/dev/null; do
    i=$(( (i+1) % 8 ))
    printf "\r[${spinner[$i]}] $1..."
    sleep 0.1
  done
  printf "\r\033[K"
}

# Функция для отображения прогресса
progress_bar() {
  local duration=$1
  local block=$2
  local progress=0
  while [ $progress -le 100 ]; do
    echo -ne "\r[${CYAN}"
    for i in $(seq 1 $((progress/2))); do echo -n "█"; done
    for i in $(seq $((progress/2 + 1)) 50); do echo -n "░"; done
    echo -ne "${NC}] ${progress}%"
    progress=$((progress + 2))
    sleep $duration
  done
  echo
}

# Очистка предыдущих установок
echo -e "${YELLOW}♻️ Очистка старых файлов...${NC}"
(rm -rf ~/hurobot ~/.bashrc.bak &>/dev/null) & show_spinner "Удаление предыдущей версии"
(sed -i.bak '/alias hurobot/d' ~/.bashrc &>/dev/null) & show_spinner "Очистка алиасов"

# Обновление пакетов
echo -e "\n${CYAN}🔄 Обновление системы...${NC}"
(pkg update -y &>/dev/null) & show_spinner "Обновление пакетов"
progress_bar 0.05

# Установка зависимостей
echo -e "\n${YELLOW}📦 Установка компонентов...${NC}"
(pkg install -y python git libjpeg-turbo openssl &>/dev/null) & show_spinner "Базовые зависимости"
(pip install --upgrade pip wheel &>/dev/null) & show_spinner "Обновление PIP"

# Установка Python-библиотек
echo -e "\n${GREEN}🐍 Установка библиотек Python...${NC}"
LIBRARIES=("telethon>=1.36.0" "requests" "pillow" "python-whois" "pytz")
for lib in "${LIBRARIES[@]}"; do
  (pip install "$lib" &>/dev/null) & show_spinner "Установка $lib"
done
progress_bar 0.03

# Клонирование репозитория
echo -e "\n${CYAN}📥 Загрузка бота...${NC}"
(git clone --depth 1 https://github.com/rud1x/HuroBot_tg.git ~/hurobot &>/dev/null) & show_spinner "Клонирование репозитория"
progress_bar 0.02

# Настройка алиасов
echo -e "\n${YELLOW}⚙️ Настройка окружения...${NC}"
echo -e "\nalias hurobot='cd ~/hurobot && python hurobot.py'" >> ~/.bashrc
(source ~/.bashrc &>/dev/null) & show_spinner "Применение настроек"

# Завершение установки
echo -e "\n${GREEN}✅ Установка завершена!${NC}"
echo -e "Запустите бота командой: ${CYAN}hurobot${NC}\n"

# Первый запуск
cd ~/hurobot || exit
python hurobot.py
