    # HURObot - Полный исправленный код (19 Мая 2025)
import os
import asyncio
import sys
import random
import time
import requests
import re
import urllib.request
import hashlib
import subprocess
from getpass import getpass
from datetime import datetime
import pytz
from telethon import TelegramClient, events
from telethon.errors import (
    FloodWaitError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
    MessageNotModifiedError
)
from telethon.tl.functions.account import UpdateStatusRequest
from telethon.tl.functions.messages import DeleteHistoryRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import DocumentAttributeFilename
from PIL import Image
import io
import telethon
import whois
import traceback

# ======================
# СИСТЕМА ОБНОВЛЕНИЙ
# ======================
GITHUB_RAW_URL = "https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/hurobot.py"
VERSION_PATTERN = r"# HURObot - Полный исправленный код \((\d{1,2} \w+ \d{4})\)"

async def force_update():
    """Принудительное обновление скрипта"""
    try:
        print(f"\n{COLORS['header']}Проверка актуальности файлов...{COLORS['reset']}")
        
        # Получение удаленной версии
        with urllib.request.urlopen(GITHUB_RAW_URL) as response:
            remote_content = response.read().decode('utf-8')
            remote_version = re.search(VERSION_PATTERN, remote_content).group(1)
            
        # Получение текущей версии
        with open(__file__, 'r', encoding='utf-8') as f:
            current_content = f.read()
            current_version = re.search(VERSION_PATTERN, current_content).group(1)
            
        # Проверка хешей
        if hashlib.md5(current_content.encode()).hexdigest() == hashlib.md5(remote_content.encode()).hexdigest():
            return False
            
        # Начало обновления
        print(f"\n{COLORS['success']}Найдено обновление!{COLORS['reset']}")
        print(f"{COLORS['info']}Текущая версия: {current_version}{COLORS['reset']}")
        print(f"{COLORS['success']}Новая версия: {remote_version}{COLORS['reset']}")
        print(f"\n{COLORS['header']}Загружаю обновление...{COLORS['reset']}")
        
        # Замена файла
        temp_file = "hurobot_temp.py"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(remote_content)
            
        os.replace(temp_file, __file__)
        
        # Перезапуск
        print(f"{COLORS['success']}✓ Обновление успешно загружено!{COLORS['reset']}")
        print(f"{COLORS['info']}Перезапускаю скрипт...{COLORS['reset']}")
        subprocess.Popen([sys.executable, __file__])
        sys.exit(0)
        
    except Exception as e:
        print(f"{COLORS['error']}❌ Ошибка при обновлении: {str(e)}{COLORS['reset']}")
        return False

# Проверка версии Telethon
required_version = "1.36.0"
current_version = telethon.__version__
if current_version < required_version:
    print(f"Ошибка: Требуется Telethon версии {required_version} или выше. Установлена версия {current_version}.")
    print("Обновите Telethon командой: pip install --upgrade telethon")
    sys.exit(1)

# Фиолетовая палитра цветов для консоли
COLORS = {
    'header': '\033[38;2;186;85;211m',     # Яркий фиолетовый
    'input': '\033[38;2;230;230;250m',     # Лавандовый
    'success': '\033[38;2;221;160;221m',   # Розовато-фиолетовый
    'error': '\033[38;2;255;0;255m',       # Яркий пурпурный
    'info': '\033[38;2;147;112;219m',      # Средне-фиолетовый
    'prompt': '\033[38;2;218;112;214m',    # Орхидея
    'accent1': '\033[38;2;138;43;226m',    # Сине-фиолетовый
    'accent2': '\033[38;2;148;0;211m',     # Темный фиолетовый
    'accent3': '\033[38;2;153;50;204m',    # Темная орхидея
    'reset': '\033[0m'                   
}

# Замените на ваши API_ID и API_HASH с my.telegram.org
API_ID = 21551581  
API_HASH = '70d80bdf86811654363e45c01c349e98'  
SESSION_PREFIX = "account_"
TEMP_SESSION = "temp.session"
ACCOUNT_DATA = {}

# -------------------------------
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# -------------------------------
def show_banner():
    """Отображает баннер HURObot в консоли."""
    try:
        with open(__file__, 'r', encoding='utf-8') as f:
            content = f.read()
            version = re.search(VERSION_PATTERN, content).group(1)
    except:
        version = "N/A"
    
    print(f"""{COLORS['header']}
██╗░░██╗██╗░░░██╗██████╗░░█████╗░██████╗░░█████╗░████████╗
██║░░██║██║░░░██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝
███████║██║░░░██║██████╔╝██║░░██║██████╔╝██║░░██║░░░██║░░░
██╔══██║██║░░░██║██╔══██╗██║░░██║██╔══██╗██║░░██║░░░██║░░░
██║░░██║╚██████╔╝██║░░██║╚█████╔╝██████╔╝╚█████╔╝░░░██║░░░
╚═╝░░╚═╝░╚═════╝░╚═╝░░╚═╝░╚════╝░╚═════╝░░╚════╝░░░░╚═╝░░░

Версия: {version}
Телеграмм канал - @hurodev
{COLORS['reset']}""")
    print(f"{COLORS['accent2']}═{COLORS['reset']}" * 50)

def clear_screen():
    """Очищает экран консоли (Windows или Linux)."""
    os.system('cls' if os.name == 'nt' else 'clear')

async def safe_delete(file_path):
    """Безопасно удаляет файл сессии."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"{COLORS['error']}Ошибка удаления файла: {str(e)}{COLORS['reset']}")
    return False

async def load_valid_accounts():
    """Загружает все действительные аккаунты из сессий."""
    global ACCOUNT_DATA
    ACCOUNT_DATA = {}
    for session_file in os.listdir('.'):
        if session_file.startswith(SESSION_PREFIX) and session_file.endswith(".session"):
            try:
                async with TelegramClient(session_file, API_ID, API_HASH) as client:
                    if await client.is_user_authorized():
                        me = await client.get_me()
                        account_id = int(session_file.split('_')[1].split('.')[0])
                        ACCOUNT_DATA[account_id] = {
                            'phone': me.phone,
                            'name': me.username or me.first_name or f"Аккаунт {account_id}",
                            'session': session_file
                        }
            except Exception as e:
                print(f"{COLORS['error']}Ошибка загрузки сессии {session_file}: {str(e)}{COLORS['reset']}")
                await safe_delete(session_file)
                continue

async def delete_all_accounts():
    """Удаляет все аккаунты и их сессии."""
    deleted = 0
    for account_num in list(ACCOUNT_DATA.keys()):
        session_file = ACCOUNT_DATA[account_num]['session']
        if await safe_delete(session_file):
            del ACCOUNT_DATA[account_num]
            deleted += 1
    print(f"{COLORS['success']}Удалено аккаунтов: {deleted}{COLORS['reset']}")
    await asyncio.sleep(1)

async def create_account():
    clear_screen()
    show_banner()
    print(f"{COLORS['header']}Добавление нового аккаунта{COLORS['reset']}")
    print(f"{COLORS['accent2']}═{COLORS['reset']}" * 50)

    client = None
    try:
        await safe_delete(TEMP_SESSION)
        
        while True:
            phone = input(f"{COLORS['prompt']}Введите номер (+код страны номер, пример: +79123456789): {COLORS['reset']}").strip()
            if re.match(r'^\+\d{8,15}$', phone):
                break
            print(f"{COLORS['error']}❌ Неверный формат! Пример: +79123456789{COLORS['reset']}")

        if any(acc['phone'] == phone for acc in ACCOUNT_DATA.values()):
            print(f"{COLORS['error']}❌ Этот номер уже зарегистрирован!{COLORS['reset']}")
            await asyncio.sleep(1)
            return

        client = TelegramClient(TEMP_SESSION, API_ID, API_HASH)
        await client.connect()

        sent_code = await client.send_code_request(phone)
        print(f"\n{COLORS['success']}✓ Код отправлен на {phone}{COLORS['reset']}")

        code = input(f"{COLORS['prompt']}Введите код из Telegram: {COLORS['reset']}").strip().replace(' ', '')

        try:
            await client.sign_in(phone, code=code, phone_code_hash=sent_code.phone_code_hash)
        except SessionPasswordNeededError:
            password = getpass(f"{COLORS['prompt']}🔐 Введите 2FA пароль (скрыт): {COLORS['reset']}")
            await client.sign_in(password=password)

        me = await client.get_me()
        account_id = max(ACCOUNT_DATA.keys(), default=0) + 1
        new_session = f"{SESSION_PREFIX}{account_id}.session"
        
        await client.disconnect()
        await asyncio.sleep(1)

        if os.path.exists(TEMP_SESSION):
            if os.path.exists(new_session):
                os.remove(new_session)
            os.rename(TEMP_SESSION, new_session)

        ACCOUNT_DATA[account_id] = {
            'phone': phone,
            'name': me.first_name or me.username or f"Аккаунт {account_id}",
            'session': new_session
        }

        print(f"\n{COLORS['success']}✓ Успешно! {me.first_name} добавлен{COLORS['reset']}")
        await load_valid_accounts()

    except PhoneNumberInvalidError:
        print(f"{COLORS['error']}❌ Неверный номер телефона!{COLORS['reset']}")
    except PhoneCodeInvalidError:
        print(f"{COLORS['error']}❌ Неверный код подтверждения!{COLORS['reset']}")
    except Exception as e:
        print(f"{COLORS['error']}❌ Критическая ошибка: {str(e)}{COLORS['reset']}")

        traceback.print_exc()
    finally:
        if client and client.is_connected():
            await client.disconnect()
        await safe_delete(TEMP_SESSION)
    
    input(f"\n{COLORS['input']}Нажмите Enter для продолжения...{COLORS['reset']}")

def compress_image(image_bytes):
    """Сжимает изображение для экономии места."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB')
        img.thumbnail((500, 500), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        return output.getvalue()
    except Exception as e:
        print(f"{COLORS['error']}Ошибка сжатия изображения: {str(e)}{COLORS['reset']}")
        return image_bytes

# -------------------------------
# ОСНОВНАЯ ЛОГИКА
# -------------------------------
def get_moscow_time():
    """Возвращает текущее время в Москве."""
    return datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')

async def save_self_destruct_photo(client, event):
    """Сохраняет самоудаляющееся фото в 'Избранное'."""
    try:
        if not event.is_private:
            return False

        ttl = getattr(event, 'ttl_seconds', None) or getattr(event.media, 'ttl_seconds', None)
        if not ttl or ttl <= 0:
            return False

        is_photo = hasattr(event.media, 'photo')
        if not is_photo:
            return False

        media_bytes = await client.download_media(event.media, file=bytes)
        if not media_bytes:
            return False

        compressed_bytes = compress_image(media_bytes)

        sender = await event.get_sender()
        username = sender.username or sender.first_name or "Неизвестный отправитель"
        caption = (
            f"✦ Сохранено самоудаляющееся фото\n"
            f"➤ От: {username}\n"
            f"➤ Время сохранения (МСК): {get_moscow_time()}\n"
            f"➤ ID сообщения: {event.id}\n"
            "\n"
            "**HURObot // @hurodev**"
        )

        await client.send_file(
            'me',
            compressed_bytes,
            caption=caption,
            force_document=False,
            attributes=[DocumentAttributeFilename(file_name=f"self_destruct_{event.id}.jpg")]
        )

        return True
    except Exception as e:
        print(f"{COLORS['error']}Ошибка сохранения фото: {str(e)}{COLORS['reset']}")
    return False

async def shorten_url(url):
    """Сокращает URL через tinyurl."""
    try:
        response = requests.get(f"http://tinyurl.com/api-create.php?url={url}", timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"{COLORS['error']}Ошибка при сокращении URL: {str(e)}{COLORS['reset']}")
        return url

# -------------------------------
# КЛАСС СОСТОЯНИЯ КЛИЕНТА
# -------------------------------
class ClientState:
    """Хранит состояние клиента (анимация, онлайн и т.д.)."""
    def __init__(self):
        self.typing_animation = False
        self.active_animation = None
        self.animation_lock = asyncio.Lock()
        self.keep_online = False
        self.spam_online = False
        self.pending_confirmation = {}
        self.online_task = None
        self.spam_online_task = None
        self.current_message_id = None
        self.last_user_activity = 0

    async def stop_animation(self):
        """Останавливает текущую анимацию набора."""
        async with self.animation_lock:
            if self.active_animation:
                self.active_animation.cancel()
                try:
                    await self.active_animation
                except (asyncio.CancelledError, Exception):
                    pass
                self.active_animation = None
            self.current_message_id = None

# -------------------------------
# ОБРАБОТКА АККАУНТА (13 КОМАНД)
# -------------------------------
async def run_account(account_num):
    """Запускает аккаунт и обрабатывает команды."""
    session_file = ACCOUNT_DATA[account_num]['session']
    phone = ACCOUNT_DATA[account_num]['phone']
    name = ACCOUNT_DATA[account_num]['name']
    running = True
    
    async def console_input_listener():
        nonlocal running
        while running:
            user_input = await asyncio.get_event_loop().run_in_executor(
                None, input, 
                f"{COLORS['input']}Введите 1 для возврата в меню: {COLORS['reset']}"
            )
            if user_input.strip() == '1':
                running = False
                await client.disconnect()

    try:
        async with TelegramClient(session_file, API_ID, API_HASH) as client:
            state = ClientState()
            client._hurobot_state = state
            input_task = asyncio.create_task(console_input_listener())

            async def keep_online_task():
                while state.keep_online and client.is_connected():
                    try:
                        await client(UpdateStatusRequest(offline=False))
                        await asyncio.sleep(random.randint(30, 40))
                    except FloodWaitError as e:
                        print(f"{COLORS['error']}FloodWait: {e.seconds} сек{COLORS['reset']}")
                        await asyncio.sleep(e.seconds + 5)
                    except Exception as e:
                        print(f"{COLORS['error']}Ошибка онлайна: {str(e)}{COLORS['reset']}")
                        await asyncio.sleep(60)

            async def spam_online_task():
                while state.spam_online and client.is_connected():
                    try:
                        if time.time() - state.last_user_activity < 60:
                            await asyncio.sleep(10)
                            continue
                        online = random.choice([True, False])
                        await client(UpdateStatusRequest(offline=not online))
                        await asyncio.sleep(1)
                    except FloodWaitError as e:
                        print(f"{COLORS['error']}FloodWait: {e.seconds} сек{COLORS['reset']}")
                        await asyncio.sleep(e.seconds + 5)
                    except Exception as e:
                        print(f"{COLORS['error']}Ошибка мигающего онлайна: {str(e)}{COLORS['reset']}")
                        await asyncio.sleep(10)

            # Словарь с описаниями команд
            command_info = {
                'help': {
                    'name': 'help',
                    'description': 'Показывает список всех команд или инструкцию по конкретной команде.',
                    'syntax': '`.help` [название команды]',
                    'example': '`.help sonl`'
                },
                'onl': {
                    'name': 'onl',
                    'description': 'Включает или выключает режим вечного онлайна (статус "онлайн" обновляется каждые 30–40 секунд).',
                    'syntax': '`.onl` [on/off]',
                    'example': '`.onl on`'
                },
                'sonl': {
                    'name': 'sonl',
                    'description': 'Включает или выключает мигающий онлайн (статус меняется каждую секунду). Не работает, если включён .onl.',
                    'syntax': '`.sonl` [on/off]',
                    'example': '`.sonl on`'
                },
                'save': {
                    'name': 'save',
                    'description': 'Сохраняет самоудаляющееся фото из личного чата в "Избранное".',
                    'syntax': '`.save` (в ответ на фото)',
                    'example': '`.save` (в ответ на фото)'
                },
                'clone': {
                    'name': 'clone',
                    'description': 'Клонирует пост из канала или чата в "Избранное" по ссылке.',
                    'syntax': '`.clone` [url]',
                    'example': '`.clone https://t.me/channel/123`'
                },
                'short': {
                    'name': 'short',
                    'description': 'Сокращает URL-адрес с помощью сервиса tinyurl.',
                    'syntax': '`.short` [url]',
                    'example': '`.short https://example.com`'
                },
                'delme': {
                    'name': 'delme',
                    'description': 'Удаляет всю переписку в текущем чате после подтверждения кодом.',
                    'syntax': '`.delme` [код]',
                    'example': '`.delme` 1234'
                },
                'ani': {
                    'name': 'ani',
                    'description': 'Включает или выключает анимацию набора текста (по одной букве каждые 0.05 сек).',
                    'syntax': '`.ani` [on/off]',
                    'example': '`.ani on`'
                },
                'sti': {
                    'name': 'sti',
                    'description': 'Отправляет указанное количество стикеров в ответ на стикер (до 50).',
                    'syntax': '`.sti` [число]',
                    'example': '`.sti 10` (в ответ на стикер)'
                },
                'tagall': {
                    'name': 'tagall',
                    'description': 'Упоминает всех участников чата через их @username.',
                    'syntax': '`.tagall`',
                    'example': '`.tagall`'
                },
                'iter': {
                    'name': 'iter',
                    'description': 'Экспортирует список участников чата в файл и отправляет в "Избранное" Если указан -n то только с номером телеофна.',
                    'syntax': '`.iter` [-n]',
                    'example': '`.iter -n`'
                },
                'up': {
                    'name': 'up',
                    'description': 'Выполняет многократные упоминания пользователя с удалением сообщений (до 50).',
                    'syntax': '`.up` [число]',
                    'example': '`.up 5` (в ответ на сообщение)'
                },
                'data': {
                    'name': 'data',
                    'description': 'Получает информацию о пользователе (ID, имя, телефон, статус, регистрация, описание).',
                    'syntax': '`.data` (в ответ на сообщение)',
                    'example': '`.data` (в ответ на сообщение)'
                },
                'osint': {
                    'name': 'osint',
                    'description': 'Проверка данных по IP/номеру/почте',
                    'syntax': '`.osint` [значение]',
                    'example': '`.osint 8.8.8.8` или `.osint example@mail.com` или `.osint +79991234567`'
                },
                'whois': {
                    'name': 'whois',
                    'description': 'Показывает информацию о домене (регистрация, владелец, DNS и т.д.)',
                    'syntax': '`.whois` [домен]',
                    'example': '`.whois google.com`'
                },
                }

            def get_usage_instructions(command_name, status=None):
                """Возвращает инструкцию по использованию команды."""
                info = command_info[command_name]
                text = f"✦ Указания по использованию\n" \
                       f"➤ Команда: `{info['name']}`\n"
                if status:
                    text += f"➤ Статус: {status}\n"
                text += f"➤ Описание: {info['description']}\n" \
                        f"➤ Синтаксис: {info['syntax']}\n" \
                        f"➤ Пример: {info['example']}\n" \
                        "\n" \
                        "**HURObot // @hurodev**"
                return text

            # 1. Автосохранение самоудаляющихся фото
            @client.on(events.NewMessage(func=lambda e: e.is_private))
            async def auto_save(event):
                await save_self_destruct_photo(client, event)

            # 2. .save - Ручное сохранение самоудаляющегося фото
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.save$'))
            async def manual_save(event):
                state.last_user_activity = time.time()
                if not event.is_reply:
                    await event.edit(get_usage_instructions('save'))
                    return
                reply = await event.get_reply_message()
                if not (hasattr(reply.media, 'photo') and (getattr(reply, 'ttl_seconds', None) or getattr(reply.media, 'ttl_seconds', None))):
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ Это не самоудаляющееся фото\n"
                                   f"➤ Формат: `.save` (в ответ на фото)\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                    return
                try:
                    media_bytes = await client.download_media(reply.media, file=bytes)
                    compressed_bytes = compress_image(media_bytes)
                    sender = await reply.get_sender()
                    username = sender.username or sender.first_name or "Неизвестный отправитель"
                    caption = (
                        f"✦ Сохранено самоудаляющееся фото\n"
                        f"➤ От: {username}\n"
                        f"➤ Время сохранения (МСК): {get_moscow_time()}\n"
                        f"➤ ID сообщения: {reply.id}\n"
                        "\n"
                        "**HURObot // @hurodev**"
                    )
                    await client.send_file(
                        'me',
                        compressed_bytes,
                        caption=caption,
                        force_document=False,
                        attributes=[DocumentAttributeFilename(file_name=f"self_destruct_{reply.id}.jpg")]
                    )
                    await event.delete()
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # 3. .onl - Вечный онлайн
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.onl(?:\s+(on|off))?$'))
            async def online_handler(event):
                state.last_user_activity = time.time()
                action = event.pattern_match.group(1)
                if not action:
                    status = "включён" if state.keep_online else "выключен"
                    await event.edit(get_usage_instructions('onl', status=status))
                    return
                try:
                    new_state = action.lower() == 'on'
                    if new_state == state.keep_online:
                        status = "включена" if state.keep_online else "выключена"
                        await event.edit(f"✦ Вечный онлайн уже {status}\n"
                                       f"➤ Подробно: `.help onl`\n"
                                       "\n"
                                       "**HURObot // @hurodev**")
                        return
                    state.keep_online = new_state
                    status = "включена" if state.keep_online else "выключена"
                    if state.keep_online and state.spam_online:
                        state.spam_online = False
                        if state.spam_online_task:
                            state.spam_online_task.cancel()
                            try:
                                await state.spam_online_task
                            except asyncio.CancelledError:
                                pass
                            state.spam_online_task = None
                    await event.edit(f"✦ Вечный онлайн {status}\n"
                                   f"➤ Подробно: `.help onl`\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                    if state.keep_online and client.is_connected():
                        if state.online_task:
                            state.online_task.cancel()
                            try:
                                await state.online_task
                            except asyncio.CancelledError:
                                pass
                        state.online_task = asyncio.create_task(keep_online_task())
                    elif state.online_task:
                        state.online_task.cancel()
                        try:
                            await state.online_task
                        except asyncio.CancelledError:
                            pass
                        state.online_task = None
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # 4. .sonl - Мигающий онлайн
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.sonl(?:\s+(on|off))?$'))
            async def sonl_handler(event):
                state.last_user_activity = time.time()
                action = event.pattern_match.group(1)
                if not action:
                    status = "включён" if state.spam_online else "выключен"
                    await event.edit(get_usage_instructions('sonl', status=status))
                    return
                try:
                    new_state = action.lower() == 'on'
                    if new_state == state.spam_online:
                        status = "включён" if state.spam_online else "выключен"
                        await event.edit(f"✦ Мигающий онлайн уже {status}\n"
                                       f"➤ Подробно: `.help sonl`\n"
                                       "\n"
                                       "**HURObot // @hurodev**")
                        return
                    if new_state and state.keep_online:
                        await event.edit(f"✦ Ошибка\n"
                                       f"➤ Выключите вечный онлайн (`.onl off`)\n"
                                       "\n"
                                       "**HURObot // @hurodev**")
                        return
                    state.spam_online = new_state
                    status = "включён" if state.spam_online else "выключен"
                    await event.edit(f"✦ Мигающий онлайн {status}\n"
                                   f"➤ Подробно: `.help sonl`\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                    if state.spam_online:
                        if state.spam_online_task:
                            state.spam_online_task.cancel()
                            try:
                                await state.spam_online_task
                            except asyncio.CancelledError:
                                pass
                        state.spam_online_task = asyncio.create_task(spam_online_task())
                    elif state.spam_online_task:
                        state.spam_online_task.cancel()
                        try:
                            await state.spam_online_task
                        except asyncio.CancelledError:
                            pass
                        state.spam_online_task = None
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # 5. .clone - Клонирование поста
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.clone(?:\s+(.+))?$'))
            async def clone_handler(event):
                state.last_user_activity = time.time()
                post_link = event.pattern_match.group(1)
                if not post_link:
                    await event.edit(get_usage_instructions('clone'))
                    return
                if not post_link.startswith('https://t.me/'):
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ Неверный формат ссылки\n"
                                   f"➤ Формат: `.clone https://t.me/канал/123`\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                    return
                try:
                    parts = post_link.split('/')
                    channel = parts[-2]
                    post_id = int(parts[-1])
                    entity = await client.get_entity(channel)
                    message = await client.get_messages(entity, ids=post_id)
                    if message.media:
                        await client.send_file('me', message.media, caption=message.text or '')
                    else:
                        await client.send_message('me', message.text or 'Пустой пост')
                    await event.edit(f"✦ Клонирование выполнено\n"
                                   f"➤ Сохранено в \"Избранное\"\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # 6. .short - Сокращение URL
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.short(?:\s+(.+))?$'))
            async def short_handler(event):
                state.last_user_activity = time.time()
                url = event.pattern_match.group(1)
                if not url:
                    await event.edit(get_usage_instructions('short'))
                    return
                if not url.startswith('http'):
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ Укажите действительный URL\n"
                                   f"➤ Формат: `.short https://example.com`\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                    return
                try:
                    short_url = await shorten_url(url)
                    await event.edit(f"✦ Сокращение выполнено\n"
                                   f"➤ Исходный URL: {url}\n"
                                   f"➤ Короткий URL: {short_url}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # 7. .delme - Удаление переписки
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.delme(?:\s+(\d+))?$'))
            async def delme_handler(event):
                state.last_user_activity = time.time()
                code = event.pattern_match.group(1)
                if not code:
                    confirm_code = ''.join(random.choices('0123456789', k=4))
                    state.pending_confirmation[event.chat_id] = confirm_code
                    await event.edit(f"✦ Требуется подтверждение\n"
                                   f"➤ Введите: `.delme {confirm_code}`\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                    return
                try:
                    if state.pending_confirmation.get(event.chat_id) == code:
                        await client(DeleteHistoryRequest(peer=event.chat_id, max_id=0, just_clear=True))
                        await event.edit(f"✦ Переписка удалена\n"
                                       f"➤ Чат очищен\n"
                                       "\n"
                                       "**HURObot // @hurodev**")
                    else:
                        await event.edit(get_usage_instructions('delme'))
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # 8. .ani - Анимация набора текста
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ani(?:\s+(on|off))?$'))
            async def ani_handler(event):
                state.last_user_activity = time.time()
                action = event.pattern_match.group(1)
                if not action:
                    status = "включена" if state.typing_animation else "выключена"
                    await event.edit(get_usage_instructions('ani', status=status))
                    return
                try:
                    new_state = action.lower() == 'on'
                    if new_state == state.typing_animation:
                        status = "включена" if state.typing_animation else "выключена"
                        await event.edit(f"✦ Анимация уже {status}\n"
                                       f"➤ Подробно: `.help ani`\n"
                                       "\n"
                                       "**HURObot // @hurodev**")
                        return
                    state.typing_animation = new_state
                    status = "включена" if state.typing_animation else "выключена"
                    await event.edit(f"✦ Анимация {status}\n"
                                   f"➤ Подробно: `.help ani`\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                    if not state.typing_animation:
                        await state.stop_animation()
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # Анимация для исходящих текстовых сообщений
            @client.on(events.NewMessage(outgoing=True))
            async def animate_message(event):
                state.last_user_activity = time.time()
                if not state.typing_animation or not event.text or event.text.startswith('.'):
                    return
                try:
                    await state.stop_animation()
                    current_text = ""
                    await asyncio.sleep(0.1)
                    for char in event.text:
                        if not state.typing_animation:
                            break
                        current_text += char
                        try:
                            await event.edit(current_text)
                            await asyncio.sleep(0.05)
                        except MessageNotModifiedError:
                            continue
                        except FloodWaitError as e:
                            await asyncio.sleep(e.seconds + 1)
                            break
                        except Exception as e:
                            await event.edit(f"✦ Ошибка\n"
                                           f"➤ {str(e)}\n"
                                           "\n"
                                           "**HURObot // @hurodev**")
                            break
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # 9. .sti - Спам стикерами
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.sti(?:\s+(\d+))?$'))
            async def sti_handler(event):
                state.last_user_activity = time.time()
                count = event.pattern_match.group(1)
                if not count or not event.is_reply:
                    await event.edit(get_usage_instructions('sti'))
                    return
                try:
                    count = int(count)
                    count = min(count, 50)
                    reply = await event.get_reply_message()
                    if not hasattr(reply, 'sticker'):
                        await event.edit(f"✦ Ошибка\n"
                                       f"➤ Ответьте на стикер\n"
                                       f"➤ Формат: `.sti 10`\n"
                                       "\n"
                                       "**HURObot // @hurodev**")
                        return
                    for _ in range(count):
                        await reply.reply(file=reply.sticker)
                    await event.delete()
                except ValueError:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ Укажите число\n"
                                   f"➤ Формат: `.sti 10`\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # 10. .tagall - Упоминание всех участников
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.tagall$'))
            async def tagall_handler(event):
                state.last_user_activity = time.time()
                try:
                    participants = await client.get_participants(event.chat_id)
                    mentions = " ".join([f'@{p.username}' for p in participants if p.username])
                    if not mentions:
                        await event.edit(f"✦ Ошибка\n"
                                       f"➤ Нет участников с username\n"
                                       "\n"
                                       "**HURObot // @hurodev**")
                        return
                    await event.edit(f"✦ Упоминание выполнено\n"
                                   f"➤ Упомянуты: {mentions}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # 11. .iter - Экспорт участников чата
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.iter(?:\s+(-n))?$'))
            async def iter_handler(event):
                state.last_user_activity = time.time()
                only_phone = event.pattern_match.group(1) == '-n'
                try:
                    chat = await event.get_chat()
                    chat_link = f"https://t.me/{chat.username}" if chat.username else "Чат без публичной ссылки"
                    participants = await client.get_participants(event.chat_id)
                    if not participants:
                        await event.edit(f"✦ Ошибка\n"
                                       f"➤ Нет участников в чате\n"
                                       "\n"
                                       "**HURObot // @hurodev**")
                        return
                    with open("members.txt", "w", encoding="utf-8") as f:
                        for p in participants:
                            if not only_phone or p.phone:
                                f.write(f"{p.id} | @{p.username} | {p.phone or 'нет'}\n")
                    caption = (
                        f"✦ Экспорт участников\n"
                        f"➤ Чат: {chat_link}\n"
                        f"➤ Время (МСК): {get_moscow_time()}\n"
                        "\n"
                        "**HURObot // @hurodev**"
                    )
                    await client.send_file('me', "members.txt", caption=caption)
                    os.remove("members.txt")
                    await event.edit(f"✦ Экспорт выполнен\n"
                                   f"➤ Сохранено в \"Избранное\"\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # 12. .up - Многократные упоминания
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.up(?:\s+(\d+))?$'))
            async def up_handler(event):
                state.last_user_activity = time.time()
                count = event.pattern_match.group(1)
                if not count or not event.is_reply:
                    await event.edit(get_usage_instructions('up'))
                    return
                try:
                    count = int(count)
                    count = min(count, 50)
                    reply = await event.get_reply_message()
                    user = await reply.get_sender()
                    if not user.username:
                        await event.edit(f"✦ Ошибка\n"
                                       f"➤ У пользователя нет username\n"
                                       f"➤ Формат: `.up 5`\n"
                                       "\n"
                                       "**HURObot // @hurodev**")
                        return
                    for _ in range(count):
                        msg = await client.send_message(event.chat_id, f"@{user.username}")
                        await msg.delete()
                    await event.edit(f"✦ Переупоминания выполнены\n"
                                   f"➤ Количество: {count} упоминаний\n"
                                   f"➤ Пользователь: @{user.username}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                except ValueError:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ Укажите число\n"
                                   f"➤ Формат: `.up 5`\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # 13. .data - Информация о пользователе
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.data$'))
            async def data_handler(event):
                state.last_user_activity = time.time()
                if not event.is_reply:
                    await event.edit(get_usage_instructions('data'))
                    return
                try:
                    reply = await event.get_reply_message()
                    user = await reply.get_sender()
                    full_user = await client(GetFullUserRequest(user))
                    user_info = f"ID: {user.id}\nИмя: {user.first_name}"
                    if hasattr(user, 'phone'):
                        user_info += f"\nТелефон: {user.phone or 'скрыт'}"
                    if hasattr(user, 'status'):
                        status = user.status
                        if hasattr(status, 'was_online'):
                            last_online = status.was_online.strftime('%Y-%m-%d %H:%M:%S')
                            user_info += f"\nПоследний онлайн: {last_online}"
                        if hasattr(status, 'created'):
                            reg_date = status.created.strftime('%Y-%m-%d %H:%M:%S')
                            user_info += f"\nДата регистрации: {reg_date}"
                        else:
                            user_info += "\nДата регистрации: Недоступно"
                    if hasattr(full_user, 'about'):
                        user_info += f"\nО себе: {full_user.about[:100] + '...' if full_user.about else 'нет информации'}"
                    await event.edit(f"✦ Данные пользователя\n"
                                   f"➤ {user_info.replace('\n', '\n➤ ')}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ {str(e)}\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.osint(?:\s+(.+))?$'))
            async def osint_handler(event):
                state.last_user_activity = time.time()
                args = event.text.split(' ', 1)
                if len(args) < 2:
                    await event.edit(
                        "<b>✦ Введите данные для проверки!\nПримеры:</b>\n"
                        "➤ <code>.osint 8.8.8.8</code>\n"
                        "➤ <code>.osint +79123456789</code>\n"
                        "➤ <code>.osint example@mail.com</code>",
                        parse_mode='html'
                    )
                    return
                
                target = args[1].strip()
                await event.edit(f"<b>✦ Начинаю анализ:</b> <code>{target}</code>", parse_mode='html')
                
                try:
                    # Определение типа данных
                    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target):
                        await ip_lookup(event, target)
                    elif '@' in target:
                        await mail_lookup(event, target)
                    elif re.match(r'^\+?[\d\s\-\(\)]{7,}$', target):
                        await phone_lookup(event, target)
                    else:
                        await event.edit("<b>✦ Неверный формат данных!</b>", parse_mode='html')
                        
                except Exception as e:
                    await event.edit(f"<b>✦ Ошибка:</b>\n➤ <code>{str(e)}</code>", parse_mode='html')

            async def ip_lookup(event, ip):
                """Обработка IP-адреса"""
                try:
                    data = requests.get(f"http://ipwho.is/{ip}").json()
                    if data['success']:
                        response = (
                            f"<b>✦ Результаты проверки IP:</b>\n"
                            f"➤ <b>Цель:</b> <code>{ip}</code>\n"
                            f"├ <b>Провайдер:</b> <code>{data['connection']['isp']}</code>\n"
                            f"├ <b>Страна:</b> {data['flag']['emoji']} <code>{data['country']}</code>\n"
                            f"├ <b>Город:</b> <code>{data['city']}</code>\n"
                            f"├ <b>Координаты:</b> <code>{data['latitude']}, {data['longitude']}</code>\n"
                            f"└ <b>Карта:</b> <a href='https://www.google.com/maps/@{data['latitude']},{data['longitude']},15z'>ссылка</a>\n"
                            "\n<b>HURObot // @hurodev</b>"
                        )
                    else:
                        response = "<b>✦ Не удалось получить данные по IP</b>"
                    await event.edit(response, parse_mode='html')
                except Exception as e:
                    await event.edit(f"<b>✦ Ошибка:</b>\n➤ <code>{str(e)}</code>", parse_mode='html')

            async def phone_lookup(event, phone):
                """Обработка номера телефона"""
                try:
                    response = requests.get(
                        f"https://htmlweb.ru/geo/api.php?json&telcod={phone}",
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
                    )
                    data = response.json()
                    
                    if 'limit' in data and data['limit'] == 0:
                        await event.edit("<b>✦ Лимит запросов!\n➤ Включите VPN</b>", parse_mode='html')
                        return

                    response_text = (
                        f"<b>✦ Результаты проверки номера:</b>\n"
                        f"➤ <b>Цель:</b> <code>{phone}</code>\n"
                        f"├ <b>Страна:</b> <code>{data.get('country', {}).get('name', 'N/A')}</code>\n"
                        f"├ <b>Оператор:</b> <code>{data.get('0', {}).get('oper', 'N/A')}</code>\n"
                        f"└ <b>Часовой пояс:</b> <code>{data.get('capital', {}).get('tz', 'N/A')}</code>\n"
                        "\n<b>HURObot // @hurodev</b>"
                    )
                    await event.edit(response_text, parse_mode='html')
                except Exception as e:
                    await event.edit(f"<b>✦ Ошибка:</b>\n➤ <code>{str(e)}</code>", parse_mode='html')

            async def mail_lookup(event, mail):
                """Проверка почты на утечки"""
                try:
                    result = subprocess.run(
                        f"holehe {mail}",
                        capture_output=True,
                        text=True,
                        shell=True,
                        check=True
                    )
                    output = "\n".join([
                        line.replace("[x]", "📛")
                            .replace("[-]", "❌")
                            .replace("[+]", "✅")
                            .replace("Email used", "<b>✔️ Зарегистрирована</b>")
                            .replace("Email not used", "<b>❌ Не зарегистрирована</b>")
                        for line in result.stdout.split('\n')[4:-4]
                    ])
                    await event.edit(
                        f"<b>✦ Результаты проверки почты {mail}:</b>\n{output}\n\n<b>HURObot // @hurodev</b>",
                        parse_mode='html'
                    )
                except Exception as e:
                    await event.edit(f"<b>✦ Ошибка:</b>\n➤<code>{str(e)}</code>", parse_mode='html')


            # 15. .whois - Информация о домене
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.whois(?:\s+(.+))?$'))
            async def whois_handler(event):
                state.last_user_activity = time.time()
                args = event.text.split(' ', 1)
                if len(args) < 2:
                    await event.edit(
                        "<b>✦ Укажите домен!\n➤ Пример:</b>\n➤ <code>.whois google.com</code>",
                        parse_mode='html'
                    )
                    return

                domain = args[1].strip()
                await event.edit(f"<b>✦ Проверяю WHOIS для:</b> <code>{domain}</code>", parse_mode='html')
                
                try:
                    domain_info = whois.whois(domain)
                    response = (
                        f"<b>✦ Результаты WHOIS:</b>\n"
                        f"➤ <b>Домен:</b> <code>{domain_info.domain_name}</code>\n"
                        f"├ <b>Создан:</b> <code>{domain_info.creation_date}</code>\n"
                        f"├ <b>Истекает:</b> <code>{domain_info.expiration_date}</code>\n"
                        f"├ <b>Регистратор:</b> <code>{domain_info.registrar}</code>\n"
                        f"├ <b>Владелец:</b> <code>{domain_info.registrant_name or 'N/A'}</code>\n"
                        f"└ <b>Серверы:</b> <code>{', '.join(domain_info.name_servers) if domain_info.name_servers else 'N/A'}</code>\n"
                        "\n<b>HURObot // @hurodev</b>"
                    )
                    await event.edit(response, parse_mode='html')
                except Exception as e:
                    await event.edit(f"<b>✦ Ошибка:</b>\n➤<code>{str(e)}</code>", parse_mode='html')

            # 14. .help - Справка по командам
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.help(?:\s+([a-zA-Z]+))?$'))
            async def help_handler(event):
                state.last_user_activity = time.time()
                command = event.pattern_match.group(1)
                if not command:
                    help_text = """
✦ Список команд:

➤ `.help` - Показать это меню
➤ `.onl` [on/off] - Вечный онлайн 
➤ `.sonl` [on/off] - Мигающий онлайн 
➤ `.save` - Сохранить самоудаляющееся фото
➤ `.clone` [url] - Клонировать пост 
➤ `.short` [url] - Сократить ссылку 
➤ `.delme` - Удалить переписку
➤ `.ani` [on/off] - Анимация набора 
➤ `.sti` [число] - Спам стикерами 
➤ `.tagall` - Упомянуть всех
➤ `.iter` [-n] - Экспорт участников 
➤ `.up` [число] - Переупоминания 
➤ `.data` - Инфо о пользователе
➤ `.osint` [телефон/ip/почта] - пробив
➤ `.whois` [домен] - Информация о домене
➤ Для справки: `.help [название команды]`

**HURObot // @hurodev**
                    """
                    await event.edit(help_text)
                    return
                command = command.lower()
                if command in command_info:
                    info = command_info[command]
                    help_text = f"✦ Команда: {info['name']}\n" \
                               f"\n" \
                               f"➤ Описание: {info['description']}\n" \
                               f"➤ Синтаксис: {info['syntax']}\n" \
                               f"➤ Пример: {info['example']}\n" \
                               "\n" \
                               "**HURObot // @hurodev**"
                    await event.edit(help_text)
                else:
                    await event.edit(f"✦ Ошибка\n"
                                   f"➤ Команда '{command}' не найдена\n"
                                   f"➤ Используйте: `.help` для списка команд\n"
                                   "\n"
                                   "**HURObot // @hurodev**")

            # Вывод в консоль после запуска
            clear_screen()
            show_banner()
            print(f"{COLORS['success']}Бот запущен!{COLORS['reset']}")
            print(f"{COLORS['prompt']}Аккаунт: {name} (+{phone}){COLORS['reset']}")
            print(f"{COLORS['header']}  .help -- список команд{COLORS['reset']}")
            print(f"{COLORS['header']}  .help [название команды] -- справка{COLORS['reset']}")
            print(f"{COLORS['accent2']}═{COLORS['reset']}" * 50)
            await client.run_until_disconnected()

    except Exception as e:
        print(f"{COLORS['error']}Ошибка: {str(e)}{COLORS['reset']}")
    finally:
        running = False
        input_task.cancel()

# -------------------------------
# ГЛАВНОЕ МЕНЮ
# -------------------------------
async def main_menu():
    """Основное меню для управления аккаунтами."""
    # Принудительное обновление при запуске
    try:
        clear_screen()
        show_banner()
        if await force_update():
            return
    except:
        pass

    while True:
        clear_screen()
        show_banner()
        await load_valid_accounts()
        accounts = sorted(ACCOUNT_DATA.keys())
        print(f"{COLORS['header']}Доступные аккаунты:{COLORS['reset']}")
        if accounts:
            for num in accounts:
                print(f"{COLORS['input']}{num}.{COLORS['reset']} {COLORS['info']}{ACCOUNT_DATA[num]['name']} (+{ACCOUNT_DATA[num]['phone']}){COLORS['reset']}")
        else:
            print(f"{COLORS['error']}Нет доступных аккаунтов{COLORS['reset']}")     
        print(f"\n")
        print(f"{COLORS['header']}0. Добавить новый аккаунт")
        print(f"-. Удалить все аккаунты")
        print(f"{COLORS['accent2']}═{COLORS['reset']}" * 50)
        
        choice = input(f"{COLORS['prompt']}Выберите действие: {COLORS['reset']}")
        
        if choice == "0":
            await create_account()
            input(f"{COLORS['input']}Нажмите Enter для продолжения...{COLORS['reset']}")
        elif choice == "-":
            await delete_all_accounts()
        elif choice.isdigit() and int(choice) in accounts:
            await run_account(int(choice))
        else:
            print(f"{COLORS['error']}Неверный выбор!{COLORS['reset']}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print(f"\n{COLORS['header']}Работа скрипта завершена{COLORS['reset']}")
        sys.exit(0)
    except Exception as e:
        print(f"{COLORS['error']}Фатальная ошибка: {str(e)}{COLORS['reset']}")
        sys.exit(1)
