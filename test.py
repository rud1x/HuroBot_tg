# HURObot - Полный исправленный код (17 Мая 2025) с расширенным функционалом
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
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import qrcode
from pyfiglet import Figlet
import yt_dlp
import socket
import whois
from googletrans import Translator
import math

# ======================
# КОНФИГУРАЦИЯ
# ======================
GITHUB_RAW_URL = "https://raw.githubusercontent.com/rud1x/HuroBot_tg/main/hurobot.py"
VERSION_PATTERN = r"# HURObot - Полный исправленный код \((\d{1,2} \w+ \d{4})\)"

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
    'reset': '\033[0m'                     # Сброс цвета
}

API_ID = 21551581  
API_HASH = '70d80bdf86811654363e45c01c349e98'  
SESSION_PREFIX = "account_"
TEMP_SESSION = "temp.session"
ACCOUNT_DATA = {}

# ======================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ======================
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

async def force_update():
    """Принудительное обновление скрипта."""
    try:
        print(f"\n{COLORS['header']}Проверка актуальности файлов...{COLORS['reset']}")
        with urllib.request.urlopen(GITHUB_RAW_URL) as response:
            remote_content = response.read().decode('utf-8')
            remote_version = re.search(VERSION_PATTERN, remote_content).group(1)
            
        with open(__file__, 'r', encoding='utf-8') as f:
            current_content = f.read()
            current_version = re.search(VERSION_PATTERN, current_content).group(1)
            
        if hashlib.md5(current_content.encode()).hexdigest() == hashlib.md5(remote_content.encode()).hexdigest():
            return False
            
        print(f"\n{COLORS['success']}Найдено обновление!{COLORS['reset']}")
        print(f"{COLORS['info']}Текущая версия: {current_version}{COLORS['reset']}")
        print(f"{COLORS['success']}Новая версия: {remote_version}{COLORS['reset']}")
        print(f"\n{COLORS['header']}Загружаю обновление...{COLORS['reset']}")
        
        temp_file = "hurobot_temp.py"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(remote_content)
            
        os.replace(temp_file, __file__)
        
        print(f"{COLORS['success']}✓ Обновление успешно загружено!{COLORS['reset']}")
        print(f"{COLORS['info']}Перезапускаю скрипт...{COLORS['reset']}")
        subprocess.Popen([sys.executable, __file__])
        sys.exit(0)
        
    except Exception as e:
        print(f"{COLORS['error']}❌ Ошибка при обновлении: {str(e)}{COLORS['reset']}")
        return False

def clear_screen():
    """Очищает экран консоли."""
    os.system('cls' if os.name == 'nt' else 'clear')

async def safe_delete(file_path):
    """Безопасно удаляет файл."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"{COLORS['error']}Ошибка удаления файла: {str(e)}{COLORS['reset']}")
    return False

async def load_valid_accounts():
    """Загружает все действительные аккаунты."""
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
    """Удаляет все аккаунты."""
    deleted = 0
    for account_num in list(ACCOUNT_DATA.keys()):
        session_file = ACCOUNT_DATA[account_num]['session']
        if await safe_delete(session_file):
            del ACCOUNT_DATA[account_num]
            deleted += 1
    print(f"{COLORS['success']}Удалено аккаунтов: {deleted}{COLORS['reset']}")
    await asyncio.sleep(1)

async def create_account():
    """Создает новый аккаунт."""
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
        import traceback
        traceback.print_exc()
    finally:
        if client and client.is_connected():
            await client.disconnect()
        await safe_delete(TEMP_SESSION)
    
    input(f"\n{COLORS['input']}Нажмите Enter для продолжения...{COLORS['reset']}")

def compress_image(image_bytes):
    """Сжимает изображение."""
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

def get_moscow_time():
    """Возвращает текущее время в Москве."""
    return datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')

async def save_self_destruct_photo(client, event):
    """Сохраняет самоудаляющееся фото."""
    try:
        if not event.is_private:
            return False

        ttl = getattr(event, 'ttl_seconds', None) or getattr(event.media, 'ttl_seconds', None)
        if not ttl or ttl <= 0:
            return False

        if not hasattr(event.media, 'photo'):
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

# ======================
# НОВЫЕ ФУНКЦИОНАЛЬНЫЕ МОДУЛИ
# ======================
async def translate_text(text, dest='ru'):
    """Перевод текста."""
    try:
        translator = Translator()
        return translator.translate(text, dest=dest).text
    except Exception as e:
        print(f"{COLORS['error']}Ошибка перевода: {str(e)}{COLORS['reset']}")
        return text

async def generate_qr_code(text):
    """Генерация QR-кода."""
    try:
        img = qrcode.make(text)
        img.save("qr_code.png")
        return True
    except Exception as e:
        print(f"{COLORS['error']}Ошибка генерации QR: {str(e)}{COLORS['reset']}")
        return False

async def text_to_ascii(text, font='slant'):
    """Преобразование в ASCII-арт."""
    try:
        fig = Figlet(font=font)
        return fig.renderText(text)
    except Exception as e:
        print(f"{COLORS['error']}Ошибка ASCII-арта: {str(e)}{COLORS['reset']}")
        return text

async def download_media(url):
    """Скачивание медиа."""
    try:
        ydl_opts = {'format': 'best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"{COLORS['error']}Ошибка загрузки: {str(e)}{COLORS['reset']}")
        return None

async def get_ip_info(ip):
    """Информация об IP."""
    try:
        info = {
            'IP': ip,
            'Hostname': socket.gethostbyaddr(ip)[0],
            'Country': requests.get(f"http://ip-api.com/json/{ip}").json().get('country', 'N/A')
        }
        return "\n".join([f"{k}: {v}" for k, v in info.items()])
    except Exception as e:
        print(f"{COLORS['error']}Ошибка IP-инфо: {str(e)}{COLORS['reset']}")
        return f"Ошибка получения данных для {ip}"

async def get_whois_info(domain):
    """WHOIS информация."""
    try:
        w = whois.whois(domain)
        return str(w)
    except Exception as e:
        print(f"{COLORS['error']}Ошибка WHOIS: {str(e)}{COLORS['reset']}")
        return f"Ошибка получения WHOIS для {domain}"

async def deanonymize(target):
    """Деанонимизация."""
    result = []
    
    # Проверка телефона
    if re.match(r'^[\d\+][\d\s\-\(\)]{7,}$', target):
        try:
            phone = phonenumbers.parse(target)
            result.append(f"📞 Телефон: {phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}")
            result.append(f"📡 Оператор: {carrier.name_for_number(phone, 'ru')}")
            result.append(f"🌍 Регион: {geocoder.description_for_number(phone, 'ru')}")
        except:
            result.append("⚠️ Номер не распознан")
    
    # Проверка email
    elif '@' in target:
        result.append(f"📧 Email: {target}")
        try:
            resp = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{target}", timeout=5)
            if resp.status_code == 200:
                breaches = [b['Name'] for b in resp.json()]
                result.append(f"⚠️ Найден в {len(breaches)} утечках: {', '.join(breaches)}")
        except:
            result.append("⚠️ Ошибка проверки утечек")
    
    # Поиск по username
    else:
        username = target.replace('@', '')
        result.append(f"👤 Никнейм: @{username}")
        result.append(f"🔗 Telegram: https://t.me/{username}")
        result.append(f"🔎 Google: https://www.google.com/search?q={username}")
        result.append(f"💻 GitHub: https://github.com/{username}")
        result.append(f"🔴 VK: https://vk.com/{username}")
    
    return "\n".join(result)

async def calculate_expression(expr):
    """Вычисление математического выражения."""
    try:
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expr):
            return None
        return str(eval(expr))
    except:
        return None

# ======================
# КЛАСС СОСТОЯНИЯ КЛИЕНТА
# ======================
class ClientState:
    """Хранит состояние клиента."""
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
        """Останавливает анимацию."""
        async with self.animation_lock:
            if self.active_animation:
                self.active_animation.cancel()
                try:
                    await self.active_animation
                except (asyncio.CancelledError, Exception):
                    pass
                self.active_animation = None
            self.current_message_id = None

# ======================
# ОСНОВНАЯ ЛОГИКА БОТА
# ======================
async def run_account(account_num):
    """Запускает аккаунт с обработкой команд."""
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

            # Команды бота (все 21 команд)
            @client.on(events.NewMessage(func=lambda e: e.is_private))
            async def auto_save(event):
                await save_self_destruct_photo(client, event)

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.save$'))
            async def manual_save(event):
                state.last_user_activity = time.time()
                if not event.is_reply:
                    await event.edit("✦ Ошибка\n➤ Ответьте на самоудаляющееся фото\n\n**HURObot // @hurodev**")
                    return
                reply = await event.get_reply_message()
                if not (hasattr(reply.media, 'photo') and (getattr(reply, 'ttl_seconds', None) or getattr(reply.media, 'ttl_seconds', None))):
                    await event.edit("✦ Ошибка\n➤ Это не самоудаляющееся фото\n\n**HURObot // @hurodev**")
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
                    await client.send_file('me', compressed_bytes, caption=caption, force_document=False)
                    await event.delete()
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.onl(?:\s+(on|off))?$'))
            async def online_handler(event):
                state.last_user_activity = time.time()
                action = event.pattern_match.group(1)
                if not action:
                    status = "включён" if state.keep_online else "выключен"
                    await event.edit(f"✦ Вечный онлайн: {status}\n➤ Используйте: .onl on/off\n\n**HURObot // @hurodev**")
                    return
                try:
                    new_state = action.lower() == 'on'
                    if new_state == state.keep_online:
                        status = "уже " + ("включён" if state.keep_online else "выключен")
                        await event.edit(f"✦ Вечный онлайн {status}\n\n**HURObot // @hurodev**")
                        return
                    state.keep_online = new_state
                    status = "включён" if state.keep_online else "выключен"
                    if state.keep_online and state.spam_online:
                        state.spam_online = False
                        if state.spam_online_task:
                            state.spam_online_task.cancel()
                            state.spam_online_task = None
                    await event.edit(f"✦ Вечный онлайн {status}\n\n**HURObot // @hurodev**")
                    if state.keep_online:
                        state.online_task = asyncio.create_task(keep_online_task())
                    elif state.online_task:
                        state.online_task.cancel()
                        state.online_task = None
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.sonl(?:\s+(on|off))?$'))
            async def sonl_handler(event):
                state.last_user_activity = time.time()
                action = event.pattern_match.group(1)
                if not action:
                    status = "включён" if state.spam_online else "выключен"
                    await event.edit(f"✦ Мигающий онлайн: {status}\n➤ Используйте: .sonl on/off\n\n**HURObot // @hurodev**")
                    return
                try:
                    new_state = action.lower() == 'on'
                    if new_state == state.spam_online:
                        status = "уже " + ("включён" if state.spam_online else "выключен")
                        await event.edit(f"✦ Мигающий онлайн {status}\n\n**HURObot // @hurodev**")
                        return
                    if new_state and state.keep_online:
                        await event.edit("✦ Ошибка\n➤ Сначала выключите вечный онлайн (.onl off)\n\n**HURObot // @hurodev**")
                        return
                    state.spam_online = new_state
                    status = "включён" if state.spam_online else "выключен"
                    await event.edit(f"✦ Мигающий онлайн {status}\n\n**HURObot // @hurodev**")
                    if state.spam_online:
                        state.spam_online_task = asyncio.create_task(spam_online_task())
                    elif state.spam_online_task:
                        state.spam_online_task.cancel()
                        state.spam_online_task = None
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.clone(?:\s+(.+))?$'))
            async def clone_handler(event):
                state.last_user_activity = time.time()
                post_link = event.pattern_match.group(1)
                if not post_link:
                    await event.edit("✦ Ошибка\n➤ Укажите ссылку на пост\n\n**HURObot // @hurodev**")
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
                    await event.edit("✦ Пост сохранён в \"Избранное\"\n\n**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.short(?:\s+(.+))?$'))
            async def short_handler(event):
                state.last_user_activity = time.time()
                url = event.pattern_match.group(1)
                if not url:
                    await event.edit("✦ Ошибка\n➤ Укажите URL для сокращения\n\n**HURObot // @hurodev**")
                    return
                try:
                    short_url = await shorten_url(url)
                    await event.edit(f"✦ Сокращённая ссылка:\n➤ {short_url}\n\n**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.delme(?:\s+(\d+))?$'))
            async def delme_handler(event):
                state.last_user_activity = time.time()
                code = event.pattern_match.group(1)
                if not code:
                    confirm_code = ''.join(random.choices('0123456789', k=4))
                    state.pending_confirmation[event.chat_id] = confirm_code
                    await event.edit(f"✦ Подтвердите удаление:\n➤ Введите: .delme {confirm_code}\n\n**HURObot // @hurodev**")
                    return
                try:
                    if state.pending_confirmation.get(event.chat_id) == code:
                        await client(DeleteHistoryRequest(peer=event.chat_id, max_id=0, just_clear=True))
                        await event.edit("✦ Переписка удалена\n\n**HURObot // @hurodev**")
                    else:
                        await event.edit("✦ Неверный код подтверждения\n\n**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ani(?:\s+(on|off))?$'))
            async def ani_handler(event):
                state.last_user_activity = time.time()
                action = event.pattern_match.group(1)
                if not action:
                    status = "включена" if state.typing_animation else "выключена"
                    await event.edit(f"✦ Анимация набора: {status}\n➤ Используйте: .ani on/off\n\n**HURObot // @hurodev**")
                    return
                try:
                    new_state = action.lower() == 'on'
                    if new_state == state.typing_animation:
                        status = "уже " + ("включена" if state.typing_animation else "выключена")
                        await event.edit(f"✦ Анимация {status}\n\n**HURObot // @hurodev**")
                        return
                    state.typing_animation = new_state
                    status = "включена" if state.typing_animation else "выключена"
                    await event.edit(f"✦ Анимация {status}\n\n**HURObot // @hurodev**")
                    if not state.typing_animation:
                        await state.stop_animation()
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True))
            async def animate_message(event):
                state.last_user_activity = time.time()
                if not state.typing_animation or not event.text or event.text.startswith('.'):
                    return
                try:
                    await state.stop_animation()
                    current_text = ""
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
                        except Exception:
                            break
                except Exception:
                    pass

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.sti(?:\s+(\d+))?$'))
            async def sti_handler(event):
                state.last_user_activity = time.time()
                count = event.pattern_match.group(1)
                if not count or not event.is_reply:
                    await event.edit("✦ Ошибка\n➤ Ответьте на стикер с числом\n\n**HURObot // @hurodev**")
                    return
                try:
                    count = min(int(count), 50)
                    reply = await event.get_reply_message()
                    if not hasattr(reply, 'sticker'):
                        await event.edit("✦ Ошибка\n➤ Ответьте на стикер\n\n**HURObot // @hurodev**")
                        return
                    for _ in range(count):
                        await reply.reply(file=reply.sticker)
                    await event.delete()
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.tagall$'))
            async def tagall_handler(event):
                state.last_user_activity = time.time()
                try:
                    participants = await client.get_participants(event.chat_id)
                    mentions = " ".join([f'@{p.username}' for p in participants if p.username])
                    if not mentions:
                        await event.edit("✦ Ошибка\n➤ Нет участников с username\n\n**HURObot // @hurodev**")
                        return
                    await event.edit(f"✦ Упомянуты:\n➤ {mentions}\n\n**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.iter(?:\s+(-n))?$'))
            async def iter_handler(event):
                state.last_user_activity = time.time()
                only_phone = event.pattern_match.group(1) == '-n'
                try:
                    participants = await client.get_participants(event.chat_id)
                    if not participants:
                        await event.edit("✦ Ошибка\n➤ Нет участников\n\n**HURObot // @hurodev**")
                        return
                    with open("members.txt", "w", encoding="utf-8") as f:
                        for p in participants:
                            if not only_phone or p.phone:
                                f.write(f"{p.id} | @{p.username} | {p.phone or 'нет'}\n")
                    await client.send_file('me', "members.txt", caption="✦ Список участников\n\n**HURObot // @hurodev**")
                    os.remove("members.txt")
                    await event.edit("✦ Список сохранён в \"Избранное\"\n\n**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.up(?:\s+(\d+))?$'))
            async def up_handler(event):
                state.last_user_activity = time.time()
                count = event.pattern_match.group(1)
                if not count or not event.is_reply:
                    await event.edit("✦ Ошибка\n➤ Ответьте на сообщение с числом\n\n**HURObot // @hurodev**")
                    return
                try:
                    count = min(int(count), 50)
                    reply = await event.get_reply_message()
                    user = await reply.get_sender()
                    if not user.username:
                        await event.edit("✦ Ошибка\n➤ У пользователя нет username\n\n**HURObot // @hurodev**")
                        return
                    for _ in range(count):
                        msg = await client.send_message(event.chat_id, f"@{user.username}")
                        await msg.delete()
                    await event.edit(f"✦ Упоминания выполнены: {count} раз\n\n**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.data$'))
            async def data_handler(event):
                state.last_user_activity = time.time()
                if not event.is_reply:
                    await event.edit("✦ Ошибка\n➤ Ответьте на сообщение\n\n**HURObot // @hurodev**")
                    return
                try:
                    reply = await event.get_reply_message()
                    user = await reply.get_sender()
                    full_user = await client(GetFullUserRequest(user))
                    info = f"ID: {user.id}\nИмя: {user.first_name}"
                    if hasattr(user, 'phone'):
                        info += f"\nТелефон: {user.phone or 'скрыт'}"
                    if hasattr(user, 'status'):
                        if hasattr(user.status, 'was_online'):
                            info += f"\nБыл онлайн: {user.status.was_online.strftime('%Y-%m-%d %H:%M:%S')}"
                    if hasattr(full_user, 'about'):
                        info += f"\nО себе: {full_user.about[:100] + '...' if full_user.about else 'нет'}"
                    await event.edit(f"✦ Информация:\n➤ {info.replace('\n', '\n➤ ')}\n\n**HURObot // @hurodev**")
                except Exception as e:
                    await event.edit(f"✦ Ошибка\n➤ {str(e)}\n\n**HURObot // @hurodev**")

            # Новые команды
            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.tr(?:\s+([a-z]{2}))?$'))
            async def translate_cmd(event):
                state.last_user_activity = time.time()
                lang = event.pattern_match.group(1) or 'ru'
                if not event.is_reply:
                    await event.edit("✦ Ошибка\n➤ Ответьте на сообщение\n\n**HURObot // @hurodev**")
                    return
                reply = await event.get_reply_message()
                translated = await translate_text(reply.text, dest=lang)
                await event.edit(f"✦ Перевод ({lang.upper()}):\n➤ {translated}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.qr(?:\s+(.+))?$'))
            async def qr_cmd(event):
                state.last_user_activity = time.time()
                text = event.pattern_match.group(1)
                if not text:
                    await event.edit("✦ Ошибка\n➤ Укажите текст\n\n**HURObot // @hurodev**")
                    return
                if await generate_qr_code(text):
                    await client.send_file(event.chat_id, "qr_code.png")
                    await event.delete()
                    os.remove("qr_code.png")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ascii(?:\s+(.+))?$'))
            async def ascii_cmd(event):
                state.last_user_activity = time.time()
                text = event.pattern_match.group(1)
                if not text:
                    await event.edit("✦ Ошибка\n➤ Укажите текст\n\n**HURObot // @hurodev**")
                    return
                ascii_art = await text_to_ascii(text)
                await event.edit(f"`{ascii_art}`", parse_mode='markdown')

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.dl(?:\s+(.+))?$'))
            async def download_cmd(event):
                state.last_user_activity = time.time()
                url = event.pattern_match.group(1)
                if not url:
                    await event.edit("✦ Ошибка\n➤ Укажите URL\n\n**HURObot // @hurodev**")
                    return
                filename = await download_media(url)
                if filename:
                    await client.send_file(event.chat_id, filename)
                    await event.delete()
                    os.remove(filename)

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ip(?:\s+(.+))?$'))
            async def ip_cmd(event):
                state.last_user_activity = time.time()
                ip = event.pattern_match.group(1)
                if not ip:
                    await event.edit("✦ Ошибка\n➤ Укажите IP\n\n**HURObot // @hurodev**")
                    return
                info = await get_ip_info(ip)
                await event.edit(f"✦ Информация об IP:\n➤ {info.replace('\n', '\n➤ ')}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.site(?:\s+(.+))?$'))
            async def site_cmd(event):
                state.last_user_activity = time.time()
                domain = event.pattern_match.group(1)
                if not domain:
                    await event.edit("✦ Ошибка\n➤ Укажите домен\n\n**HURObot // @hurodev**")
                    return
                info = await get_whois_info(domain)
                await event.edit(f"✦ WHOIS информация:\n➤ {info[:2000]}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.dean(?:\s+(.+))?$'))
            async def dean_cmd(event):
                state.last_user_activity = time.time()
                target = event.pattern_match.group(1)
                if not target:
                    await event.edit("✦ Ошибка\n➤ Укажите данные\n\n**HURObot // @hurodev**")
                    return
                info = await deanonymize(target)
                await event.edit(f"✦ Результаты:\n➤ {info.replace('\n', '\n➤ ')}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.calc(?:\s+(.+))?$'))
            async def calc_cmd(event):
                state.last_user_activity = time.time()
                expr = event.pattern_match.group(1)
                if not expr:
                    await event.edit("✦ Ошибка\n➤ Укажите выражение\n\n**HURObot // @hurodev**")
                    return
                result = await calculate_expression(expr)
                if result is None:
                    await event.edit("✦ Ошибка\n➤ Неверное выражение\n\n**HURObot // @hurodev**")
                else:
                    await event.edit(f"✦ Результат:\n➤ {result}\n\n**HURObot // @hurodev**")

            @client.on(events.NewMessage(outgoing=True, pattern=r'^\.help(?:\s+([a-zA-Z]+))?$'))
            async def help_handler(event):
                state.last_user_activity = time.time()
                command = event.pattern_match.group(1)
                if not command:
                    help_text = """
✦ Список команд:

Основные:
➤ .help - Справка по командам
➤ .onl [on/off] - Вечный онлайн
➤ .sonl [on/off] - Мигающий онлайн
➤ .save - Сохранить самоудаляющееся фото
➤ .clone [url] - Клонировать пост
➤ .short [url] - Сократить ссылку
➤ .delme [код] - Удалить переписку
➤ .ani [on/off] - Анимация набора
➤ .sti [n] - Спам стикерами
➤ .tagall - Упомянуть всех
➤ .iter [-n] - Экспорт участников
➤ .up [n] - Переупоминания
➤ .data - Инфо о пользователе

Новые:
➤ .tr [язык] - Переводчик
➤ .qr [текст] - QR-код
➤ .ascii [текст] - ASCII-арт
➤ .dl [url] - Скачать видео
➤ .ip [адрес] - Инфо об IP
➤ .site [домен] - WHOIS
➤ .dean [данные] - Деанон
➤ .calc [выражение] - Калькулятор

**HURObot // @hurodev**
                    """
                    await event.edit(help_text)
                else:
                    await event.edit(f"✦ Помощь по команде {command}\n➤ Введите команду без параметров для справки\n\n**HURObot // @hurodev**")

            # Запуск клиента
            clear_screen()
            show_banner()
            print(f"{COLORS['success']}Бот запущен!{COLORS['reset']}")
            print(f"{COLORS['prompt']}Аккаунт: {name} (+{phone}){COLORS['reset']}")
            print(f"{COLORS['header']}  .help -- список команд{COLORS['reset']}")
            print(f"{COLORS['header']}  .help [команда] -- справка{COLORS['reset']}")
            print(f"{COLORS['accent2']}═{COLORS['reset']}" * 50)
            await client.run_until_disconnected()

    except Exception as e:
        print(f"{COLORS['error']}Ошибка: {str(e)}{COLORS['reset']}")
    finally:
        running = False
        input_task.cancel()

# ======================
# ГЛАВНОЕ МЕНЮ
# ======================
async def main_menu():
    """Основное меню управления."""
    clear_screen()
    show_banner()
    if await force_update():
        return

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
        
        print(f"\n{COLORS['header']}0. Добавить новый аккаунт")
        print(f"-. Удалить все аккаунты")
        print(f"{COLORS['accent2']}═{COLORS['reset']}" * 50)
        
        choice = input(f"{COLORS['prompt']}Выберите действие: {COLORS['reset']}")
        
        if choice == "0":
            await create_account()
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
        print(f"\n{COLORS['header']}Работа завершена{COLORS['reset']}")
        sys.exit(0)
    except Exception as e:
        print(f"{COLORS['error']}Фатальная ошибка: {str(e)}{COLORS['reset']}")
        sys.exit(1)
