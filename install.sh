#!/bin/bash

WW=$(tput setaf 7 2>/dev/null || echo "")
RED=$(tput setaf 1 2>/dev/null || echo "")
RZ=$(tput setaf 8 2>/dev/null || echo "")
NC=$(tput sgr0 2>/dev/null || echo "")

REPO_URL="https://github.com/rud1x/HuroBot_tg.git"
INSTALL_DIR="$HOME/hurobot"

detect_system() {
    if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux" ]; then echo "termux"; return; fi
    if [ -f /etc/debian_version ]; then echo "debian"; return; fi
    if [ -f /etc/arch-release ]; then echo "arch"; return; fi
    if [ -f /etc/fedora-release ]; then echo "fedora"; return; fi
    echo "unknown"
}

SYSTEM=$(detect_system)
echo "Система: $SYSTEM"

spinner() {
    local pid=$!
    local spin=('⣾' '⣽' '⣻' '⢿' '⡿' '⣟' '⣯' '⣷')
    local i=0
    tput civis 2>/dev/null
    while kill -0 "$pid" 2>/dev/null; do
        printf "%s" "${RED}${spin[i]}${NC}"
        sleep 0.1
        printf "\b"
        i=$(( (i+1) % 8 ))
    done
    tput cnorm 2>/dev/null
    printf " \b"
}

show_banner() {
    clear 2>/dev/null || printf '\033[2J\033[H'
    echo -e "${RED}         ${WW} __      _____    __  __  _____  _      __    __  __ "
    echo -e "${RED}  /\  /\ ${WW}/ __\    \_   \/\ \ \/ _\/__   \/_\    / /   /__\/__\\"
    echo -e "${RED} / /_/ /${WW}/__\//     / /\/  \/ /\ \   / /\//_\\\\/ /   /_\ / \//"
    echo -e "${RED}/ __  /${WW}/ \/  \  /\/ /_/ /\  / _\ \ / / /  _  \/ /___//__/ _  \\"
    echo -e "${RED}\/ /_/ ${WW}\_____/  \____/\_\ \/  \__/ \/  \_/ \_/\____/\__/\/ \_/${NC}"
    echo -e "\nТелеграм канал: ${RED}@hurodev${NC}"
    echo -e "${RZ}--------------------------------------------------${NC}"
}

show_banner

printf "${RED}[+]${WW} Устанавливаем системные пакеты...${NC}"
case "$SYSTEM" in
    termux)
        {
            pkg install -y python git libjpeg-turbo libpng freetype openssl
        } & spinner
        ;;
    debian)
        {
            sudo apt update -qq
            sudo apt install -y python3 python3-pip python3-venv git libjpeg-dev zlib1g-dev libpng-dev
        } & spinner
        ;;
    arch)
        {
            sudo pacman -Sy --noconfirm python python-pip git libjpeg-turbo zlib libpng
        } & spinner
        ;;
    fedora)
        {
            sudo dnf install -y python3 python3-pip git libjpeg-turbo-devel zlib-devel libpng-devel
        } & spinner
        ;;
    *)
        echo -e "\n${RED}[✖]${WW} Неизвестная система. Установи python3, pip, git вручную.${NC}"
        exit 1
        ;;
esac
printf "\b✓\n"

printf "${RED}[+]${WW} Загружаем HURObot...${NC}"
{
    if [ -d "$INSTALL_DIR" ]; then
        mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%s)" 2>/dev/null
    fi
    git clone "$REPO_URL" "$INSTALL_DIR"
} & spinner
printf "\b✓\n"

if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}[✖]${WW} Не удалось склонировать репозиторий. Проверь сеть и доступ к GitHub.${NC}"
    exit 1
fi

printf "${RED}[+]${WW} Создаём venv и ставим зависимости...${NC}"
{
    cd "$INSTALL_DIR" || exit 1
    python3 -m venv venv 2>/dev/null || python -m venv venv 2>/dev/null

    if [ -f "venv/bin/pip" ]; then PIP="venv/bin/pip"; else PIP="venv/Scripts/pip.exe"; fi
    $PIP install --upgrade pip wheel --no-cache-dir
    $PIP install -r requirements.txt --no-cache-dir
} & spinner
printf "\b✓\n"

if [ ! -f "$INSTALL_DIR/venv/bin/python" ] && [ ! -f "$INSTALL_DIR/venv/Scripts/python.exe" ]; then
    echo -e "${RED}[✖]${WW} Виртуальное окружение не создано. Установи зависимости вручную:${NC}"
    echo -e "  cd $INSTALL_DIR && python3 -m venv venv && venv/bin/pip install -r requirements.txt"
    exit 1
fi

printf "${RED}[+]${WW} Настраиваем команду запуска...${NC}"
{
    if [ -f "$INSTALL_DIR/venv/bin/python" ]; then PY="$INSTALL_DIR/venv/bin/python"; else PY="$INSTALL_DIR/venv/Scripts/python.exe"; fi

    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"

    cat > "$BIN_DIR/hurobot" <<EOF
#!/bin/bash
cd "$INSTALL_DIR"
exec "$PY" "$INSTALL_DIR/hurobot.py" "\$@"
EOF
    chmod +x "$BIN_DIR/hurobot"
} & spinner
printf "\b✓\n"

clear 2>/dev/null || printf '\033[2J\033[H'
show_banner
echo -e "ㅤㅤㅤ${RED}Установка завершена!${NC}"
echo -e "ㅤㅤㅤДля запуска: ${RED}hurobot${NC}"
echo -e ""
echo -e "${RZ}Если команда не найдена — добавь в PATH:${NC}"
echo -e "${RZ}  export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
echo -e "${RZ}--------------------------------------------------${NC}"