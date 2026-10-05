<div align="center">

  <img src="https://i.ibb.co/v08LpSt/IMG-20260409-190254-955.jpg" width="150" alt="HuroBot Logo" style="border-radius: 18px;" />

  <h1 align="center" style="font-style: italic; color: #ff4500;">HURObot</h1>

  <p align="center">
    <strong>Многофункциональный Telegram-userbot для управления аккаунтами, автоматизации и OSINT</strong>
  </p>

  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=20&duration=3000&pause=1000&color=FF4500&center=true&vCenter=true&width=700&lines=Multi-Account+Management;Media+Save+%2B+Auto-Archive;OSINT+Toolkit;Spam+%2B+Utilities;Termux+Ready" alt="Typing SVG" />

  <br>

  <a href="https://github.com/rud1x/HuroBot_tg/releases/latest">
    <img src="https://img.shields.io/badge/Версия-v1.3.0-ff4500?style=for-the-badge&logo=github&logoColor=white" alt="Release"/>
  </a>
  <a href="https://t.me/hurodev">
    <img src="https://img.shields.io/badge/Telegram-@hurodev-26A5E4?style=for-the-badge&color=ff4500&logo=telegram&logoColor=white" alt="Telegram"/>
  </a>
  <a href="https://github.com/rud1x/HuroBot_tg">
    <img src="https://img.shields.io/github/stars/rud1x/HuroBot_tg?style=for-the-badge&color=ff4500&logo=github" alt="Stars"/>
  </a>

</div>

<br>

### <img src="https://api.iconify.design/ph:lightning-duotone.svg?color=%23ff4500" width="22" align="top"> Что это

HURObot — userbot на Telethon, который держит несколько аккаунтов сразу, сохраняет медиа, чистит чаты, пробивает данные и делает всю рутину, которую обычно делают руками.

Запускается на Termux, VPS или локальной машине. Данные — только у тебя. Никаких ботов-посредников, никаких облаков.

<br>

### <img src="https://api.iconify.design/ph:sparkle-duotone.svg?color=%23ff4500" width="22" align="top"> Возможности

| Категория | Функции |
|---|---|
| **Аккаунты** | Мультиаккаунтность, 2FA, сессии, массовое удаление |
| **Медиа** | Автосохранение T-медиа, сжатие изображений, резерв удалённых сообщений |
| **Спам** | Рассылки, стикер-бомбы, краш-атаки, упоминания, смс-бомбер |
| **OSINT** | Геолокация IP, пробив номеров и почт, WHOIS доменов |
| **Утилиты** | Сокращение ссылок, экспорт чатов, анимация текста |

<br>

### <img src="https://api.iconify.design/ph:download-simple-duotone.svg?color=%23ff4500" width="22" align="top"> Установка

#### Termux — одной командой

```
pkg install -y wget && wget -qO- "https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/install.sh" | sed 's/\r$//' | bash
```

Установщик сам:

* поставит Python 3.10+ и зависимости
* клонирует репозиторий
* поправит формат файлов (CRLF → LF)
* настроит переменные окружения
* запустит первичную конфигурацию

После установки:

```
hurobot
```

#### Ручная сборка

```
git clone https://github.com/rud1x/HuroBot_tg.git
cd HuroBot_tg
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python hurobot.py
```

<br>

### <img src="https://api.iconify.design/ph:terminal-window-duotone.svg?color=%23ff4500" width="22" align="top"> Команды

#### 🔐 Аккаунты

```
.delme [код]   — полная очистка чата (нужно подтверждение)
```

#### 💾 Медиа

```
.save          — сохранить самоудаляющийся файл (ответом на сообщение)
.clone [URL]   — скопировать пост из канала
```

#### 💥 Спам

```
.spam [N] [текст]  — рассылка сообщений
.sti [N]           — спам стикерами (ответом на стикер)
.crash             — отправка ресурсоёмких стикеров (20 шт.)
.bomb              — бомбер по номеру телефона (5 минут)
```

#### 🕵️ OSINT

```
.data              — информация о пользователе (ответом)
.osint [значение]  — проверка IP / номера / почты
.whois [домен]     — WHOIS-данные
```

#### ⚡ Утилиты

```
.tagall            — упоминание всех участников
.iter [-n]         — экспорт участников чата (-n для номеров)
.short [URL]       — сокращение ссылок
```

<br>

### <img src="https://api.iconify.design/ph:warning-duotone.svg?color=%23ff4500" width="22" align="top"> Важно

**Легальность.** Некоторые функции (`.crash`, `.spam`) могут нарушать правила Telegram. Используй только в тестовых чатах.

**Безопасность.** Храни файлы сессий в защищённом месте.

**Ответственность.** Перед использованием протестируй бота в тестовом чате. Автор не несёт ответственности за блокировки аккаунтов.

<br>

### <img src="https://api.iconify.design/ph:arrows-clockwise-duotone.svg?color=%23ff4500" width="22" align="top"> Обновление

Бот сам проверяет обновления при запуске:

* авто-установка новой версии
* авто-установка библиотек
* авто-установка зависимостей

<br>

### <img src="https://api.iconify.design/ph:code-duotone.svg?color=%23ff4500" width="22" align="top"> Стек

<div align="left">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,sqlite,html,css,js,git,linux&theme=dark" alt="HURObot Tech Stack" />
  </a>
</div>

<br>

### <img src="https://api.iconify.design/ph:heart-duotone.svg?color=%23ff4500" width="22" align="top"> Поддержка

Официальный канал: [@hurodev](https://t.me/hurodev)
Баги и предложения: [Issues](https://github.com/rud1x/HuroBot_tg/issues)

Если HURObot сэкономил тебе время — поставь звёздочку ⭐️

<br>

<div align="left">
  <a href="https://t.me/hurodev">
    <img src="https://img.shields.io/badge/Telegram-@hurodev-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram"/>
  </a>
  <a href="https://github.com/rud1x">
    <img src="https://img.shields.io/badge/GitHub-rud1x-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Profile"/>
  </a>
</div>
