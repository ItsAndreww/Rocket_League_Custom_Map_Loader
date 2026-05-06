VERSION = "1.2.0"  # Поточна версія
GITHUB_REPO = "ItsAndreww/Rocket_League_Custom_Map_Loader" 

import os
import sys
import logging
import aiohttp
import threading 
import asyncio
import aiohttp
from logging.handlers import RotatingFileHandler
from urllib.error import URLError, HTTPError
from pathlib import Path


IMG_CACHE = {}
ASYNC_LOOP = asyncio.new_event_loop()

def _start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=_start_async_loop, args=(ASYNC_LOOP,), daemon=True).start()

# ── PyInstaller / --noconsole fixes ───────────────────────────
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')
if getattr(sys, 'frozen', False):
    _old_exe = sys.executable + '.old'
    if os.path.exists(_old_exe):
        try:
            os.remove(_old_exe)
        except Exception:
            pass

import subprocess
if sys.platform == 'win32':
    _orig_popen = subprocess.Popen
    def _patched_popen(*a, **kw):
        kw.setdefault('creationflags', 0x08000000)   # CREATE_NO_WINDOW
        return _orig_popen(*a, **kw)
    subprocess.Popen = _patched_popen
# ─────────────────────────────────────────────────────────────

def _base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _data_dir():
    return _base_dir()

def resource_path(relative_path):
    """ Отримує шлях до ресурсів, адаптований для PyInstaller """
    try:
        # PyInstaller створює тимчасову папку _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def setup_logger():
    # Файл логів буде зберігатися там само, де і exe / скрипт
    log_path = Path(_data_dir()) / 'rlcml.log'
    
    logging.basicConfig(
        level=logging.INFO, # Записуємо INFO, WARNING, ERROR та CRITICAL
        format='%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            RotatingFileHandler(log_path, maxBytes=2*1024*1024, backupCount=2, encoding='utf-8')
        ]
    )
    logging.info(f"=== Rocket League Custom Map Loader v{VERSION} Started ===")

import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import urllib.request
import shlex
from bs4 import BeautifulSoup
import threading
import zipfile
import tempfile
import time
import string

# ── Selenium & Webdriver Manager ──
os.environ['WDM_LOG']       = '0'
os.environ['WDM_LOG_LEVEL'] = '0'
os.environ['WDM_SSL_VERIFY']= '0'
logging.getLogger('WDM').setLevel(logging.ERROR)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from PIL import Image, ImageTk, ImageDraw

# ── Optional dependencies ──────────────────────────────────────
try:
    import pystray
    from pystray import MenuItem as item
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False

try:
    import sv_ttk
    HAS_SV_TTK = True
except ImportError:
    HAS_SV_TTK = False

try:
    import pywinstyles
    HAS_PYWINSTYLES = True
except ImportError:
    HAS_PYWINSTYLES = False
# ─────────────────────────────────────────────────────────────


# ════════════════════════════════════════════════════════════════
# CONSTANTS & LANGUAGES
# ════════════════════════════════════════════════════════════════

CUSTOM_MAP_EXTENSIONS = {'.upk', '.udk', '.pak', '.udatasmith', '.rli'}

CUSTOM_MAP_FOLDER_NAMES = [
    'TAGame\\CookedPCConsole',
    'TAGame\\CookedPC',
    'CustomMaps',
    'BakkesMod\\mods',
]

LANGUAGE_NAMES = {'uk': 'Українська', 'en': 'English'}
CURRENT_LANGUAGE = 'en'

LANGUAGES = {
    'uk': {
        'always_on_top': 'Завжди поверх інших вікон',
        'status_ready': 'Готово. Оберіть карти для заміни.',
        'tt_settings': 'Відкрити налаштування',
        'tt_theme': 'Змінити тему (Світла/Темна)',
        'tt_launch': 'Запустити гру',
        'tt_replace': 'Створити бекап і замінити обрану карту',
        'settings': 'Налаштування',
        'save': 'Зберегти',
        'cancel': 'Скасувати',
        'check_update': 'Перевірити оновлення',
        'no_updates': 'У вас встановлена остання версія програми!',
        'search': 'Пошук', 'page': 'Сторінка',
        'app_title': 'Rocket League Custom Map Loader made by ItsAndreww',
        'local_maps_tab': 'Локальні карти',
        'download_maps_tab': 'Завантажити карти',
        'custom_maps_folder': 'Папка з кастомними картами:',
        'rl_root': 'Корінь Rocket League:',
        'maps_folder': 'Папка з картами в RL:',
        'browse': 'Огляд...', 'auto_detect': 'Автодетект',
        'refresh': 'Оновити', 'refresh_lists': 'Оновити списки',
        'replace_map': 'Замінити карту',
        'custom_maps': 'Кастомні карти',
        'standard_maps': 'Стандартні карти для заміни',
        'selected_custom': 'Вибрана кастомна:',
        'selected_standard': 'Вибрана стандартна:',
        'status_default': 'Оберіть папку з кастомними картами та корінь Rocket League.',
        'download_list': 'Завантажити список карт з BakkesMod',
        'download': 'Завантажити', 'language': 'Мова:',
        'launch_game': 'Запустити гру',
        'close_behavior': 'Дія при закритті:',
        'restore_and_exit': 'Відновити і вийти',
        'minimize_to_tray': 'Сховати в трей',
        'tray_unavailable': 'Встановіть pystray для роботи трею.',
        'show_app': 'Відкрити програму',
        'exit_app': 'Відновити карти і Вийти',
        'error_no_custom_folder': 'Оберіть папку для кастомних карт спочатку.',
        'error_no_custom_selected': 'Оберіть кастомну карту та стандартну карту для заміни.',
        'error_custom_not_found': 'Кастомна карта не знайдена.',
        'error_standard_not_found': 'Стандартна карта не знайдена.',
        'backup_failed': 'Не вдалося створити бекап: {error}',
        'replace_failed': 'Не вдалося замінити карту: {error}',
        'replace_success': 'Карту "{custom}" встановлено замість "{standard}".\nБекап: {backup}',
        'replace_status': 'Карту успішно замінено.',
        'replacement_history': 'Поточні заміни',
        'undo': 'Відновити', 'delete': 'Видалити',
        'confirm_delete': 'Видалити карту "{name}"?',
        'delete_failed': 'Не вдалося видалити: {error}',
        'delete_success': 'Карту "{name}" видалено.',
        'error_download_failed': 'Не вдалося завантажити: {error}',
        'download_complete': 'Карта "{title}" успішно завантажена.',
        'error_no_rl_root': 'Не знайдено Rocket League.exe.',
        'launch_success': 'Гру запущено.',
        'launch_failed': 'Не вдалося запустити гру: {error}',
        'auto_detect_success': 'Автоматично знайдено Rocket League.',
        'auto_detect_fail': 'Не вдалося автоматично знайти Rocket League.',
        'maps_folder_not_found': 'Не знайдено папку з картами в Rocket League.',
        'error_load_maps': 'Не вдалося отримати список карт: {error}',
        'no_maps_found': 'Карт не знайдено.',
        'loading_maps': 'Завантаження списку карт...',
        'downloading_map': 'Завантаження "{title}"...',
        'maps_loaded': 'Завантажено {count} карт.',
        'unknown_map': 'Невідома карта',
        'error_title': 'Помилка', 'info_title': 'Інформація',
        'extracting_zip': 'Розпакування архіву...',
        'no_map_in_zip': 'У ZIP не знайдено файлів карт.',
        'browser_not_found': 'Браузер не знайдено. Встановіть Edge або Chrome.',
        'help_tab': 'Інструкція',
        'help_text': '''Як користуватись програмою:
        1. Налаштування:
        • Перейдіть у "⚙️ Налаштування" на верхній панелі.
        • Вкажіть шлях до гри Rocket League (натисніть "Автодетект").
        • Оберіть папку на комп'ютері для кастомних карт (на вкладці "Локальні карти").

        2. Встановлення карти у гру:
        • У вкладці "Локальні карти" оберіть кастомну карту зліва.
        • Оберіть стандартну карту (яку не шкода замінити, зазвичай це Underpass) справа.
        • Натисніть "Замінити карту". Програма автоматично зробить бекап оригінальної карти.
        • Натисніть "Запустити гру". У грі створіть приватний матч або тренування на тій стандартній карті, яку ви замінили.

        3. Завантаження нових карт:
        • Перейдіть у вкладку "Завантажити карти".
        • Знайдіть потрібну карту через пошук і натисніть "Завантажити". Вона автоматично розпакується у вашу папку кастомних карт.

        4. Відновлення оригінальних карт:
        • Щоб повернути стандартну карту, натисніть "Відновити" у списку "Поточні заміни".
        • Або просто закрийте програму (якщо в налаштуваннях обрано "Відновити і вийти"), і вона автоматично поверне всі карти на місце!
        ''',
    },
    'en': {
        'always_on_top': 'Always on top',
        'status_ready': 'Ready. Select maps to replace.',
        'tt_settings': 'Open settings',
        'tt_theme': 'Toggle theme (Light/Dark)',
        'tt_launch': 'Launch the game',
        'tt_replace': 'Backup and replace selected map',
        'settings': 'Settings',
        'save': 'Save',
        'cancel': 'Cancel',
        'check_update': 'Check for Updates',
        'no_updates': 'You have the latest version installed!',
        'search': 'Search', 'page': 'Page',
        'app_title': 'Rocket League Custom Map Loader made by ItsAndreww',
        'local_maps_tab': 'Local Maps',
        'download_maps_tab': 'Download Maps',
        'custom_maps_folder': 'Custom maps folder:',
        'rl_root': 'Rocket League root:',
        'maps_folder': 'RL maps folder:',
        'browse': 'Browse...', 'auto_detect': 'Auto detect',
        'refresh': 'Refresh', 'refresh_lists': 'Refresh Lists',
        'replace_map': 'Replace Map',
        'custom_maps': 'Custom Maps',
        'standard_maps': 'Standard Maps to Replace',
        'selected_custom': 'Selected Custom:',
        'selected_standard': 'Selected Standard:',
        'status_default': 'Choose a custom maps folder and Rocket League root.',
        'download_list': 'Load BakkesMod map list',
        'download': 'Download', 'language': 'Language:',
        'launch_game': 'Launch Game',
        'close_behavior': 'Close behavior:',
        'restore_and_exit': 'Restore and exit',
        'minimize_to_tray': 'Minimize to tray',
        'tray_unavailable': 'Install pystray for tray support.',
        'show_app': 'Show Application',
        'exit_app': 'Restore maps and Exit',
        'error_no_custom_folder': 'Choose a custom maps folder first.',
        'error_no_custom_selected': 'Choose a custom map and a standard map to replace.',
        'error_custom_not_found': 'Custom map not found.',
        'error_standard_not_found': 'Standard map not found.',
        'backup_failed': 'Failed to create backup: {error}',
        'replace_failed': 'Failed to replace map: {error}',
        'replace_success': 'Map "{custom}" installed instead of "{standard}".\nBackup: {backup}',
        'replace_status': 'Map replaced successfully.',
        'replacement_history': 'Current replacements',
        'undo': 'Undo', 'delete': 'Delete',
        'confirm_delete': 'Delete map "{name}"?',
        'delete_failed': 'Failed to delete: {error}',
        'delete_success': 'Map "{name}" deleted.',
        'error_download_failed': 'Failed to download: {error}',
        'download_complete': 'Map "{title}" downloaded successfully.',
        'error_no_rl_root': 'RocketLeague.exe not found. Select the game root.',
        'launch_success': 'Game launched.',
        'launch_failed': 'Failed to launch game: {error}',
        'auto_detect_success': 'Rocket League found automatically.',
        'auto_detect_fail': 'Could not auto-detect Rocket League. Please choose manually.',
        'maps_folder_not_found': 'Could not find the RL maps folder.',
        'error_load_maps': 'Could not load map list: {error}',
        'no_maps_found': 'No maps found.',
        'loading_maps': 'Loading map list...',
        'downloading_map': 'Downloading "{title}"...',
        'maps_loaded': 'Loaded {count} maps.',
        'unknown_map': 'Unknown Map',
        'error_title': 'Error', 'info_title': 'Info',
        'extracting_zip': 'Extracting ZIP archive...',
        'no_map_in_zip': 'No map files found in ZIP (.upk/.udk/.pak).',
        'browser_not_found': 'Browser not found. Please install Edge or Chrome.',
        'help_tab': 'Instructions',
        'help_text': '''How to use the application:
        1. Setup:
        • Go to "⚙️ Settings" on the top bar.
        • Provide your Rocket League installation path (click "Auto detect").
        • Choose a folder on your PC to store custom maps (in the "Local Maps" tab).

        2. Playing a Custom Map:
        • In the "Local Maps" tab, select a custom map from the left list.
        • Select a standard map to replace (usually Underpass) from the right list.
        • Click "Replace Map". The app will automatically backup the original map.
        • Click "Launch Game". In-game, start a private match or training on the standard map you replaced.

        3. Downloading New Maps:
        • Go to the "Download Maps" tab.
        • Search for a map and click "Download". It will automatically extract to your custom maps folder.

        4. Restoring Maps:
        • To restore an original map, click "Undo" in the replacement history list.
        • Or simply close the app (if "Restore and exit" is selected in settings), and it will restore everything automatically!
        ''',
    }
}


def tr(key, **kwargs):
    return LANGUAGES.get(CURRENT_LANGUAGE, LANGUAGES['en']).get(key, key).format(**kwargs)


# ════════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════════
import json

def load_config():
    path = Path(_data_dir()) / 'config.json'
    if path.is_file():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.warning("config.json пошкоджено. Завантажено дефолтні налаштування.")
        except PermissionError:
            logging.error("Немає прав доступу до config.json.")
        except OSError as e:
            logging.error(f"Системна помилка при читанні конфігурації: {e}", exc_info=True)
    return {}

def save_config(cfg):
    path = os.path.join(_data_dir(), 'config.json')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


# ════════════════════════════════════════════════════════════════
# BROWSER / WEBDRIVER 
# ════════════════════════════════════════════════════════════════

def _find_binary(browser: str):
    pf   = os.environ.get('PROGRAMFILES',      r'C:\Program Files')
    pf86 = os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)')
    lad  = os.environ.get('LOCALAPPDATA',      '')

    paths = {
        'edge':   [
            os.path.join(pf86, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
            os.path.join(pf,   'Microsoft', 'Edge', 'Application', 'msedge.exe'),
            os.path.join(lad,  'Microsoft', 'Edge', 'Application', 'msedge.exe'),
        ],
        'chrome': [
            os.path.join(pf,   'Google', 'Chrome', 'Application', 'chrome.exe'),
            os.path.join(pf86, 'Google', 'Chrome', 'Application', 'chrome.exe'),
            os.path.join(lad,  'Google', 'Chrome', 'Application', 'chrome.exe'),
        ],
    }
    for p in paths.get(browser, []):
        if os.path.isfile(p):
            return p
    return shutil.which({'edge': 'msedge', 'chrome': 'chrome'}.get(browser, ''))


def _find_driver(browser: str):
    name = {'edge': 'msedgedriver.exe', 'chrome': 'chromedriver.exe'}.get(browser)
    if not name:
        return None

    candidates = []
    browser_bin = _find_binary(browser)
    if browser_bin:
        candidates.append(os.path.join(os.path.dirname(browser_bin), name))

    pf   = os.environ.get('PROGRAMFILES',      r'C:\Program Files')
    pf86 = os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)')
    lad  = os.environ.get('LOCALAPPDATA',      '')
    if browser == 'edge':
        candidates += [
            os.path.join(pf,   'Microsoft', 'Edge', 'Application', name),
            os.path.join(pf86, 'Microsoft', 'Edge', 'Application', name),
            os.path.join(lad,  'Microsoft', 'Edge', 'Application', name),
            os.path.join(pf,   'Microsoft', 'EdgeWebDriver', name),
        ]
    elif browser == 'chrome':
        candidates += [
            os.path.join(pf,   'Google', 'Chrome', 'Application', name),
            os.path.join(pf86, 'Google', 'Chrome', 'Application', name),
            os.path.join(lad,  'Google', 'Chrome', 'Application', name),
        ]

    from_path = shutil.which(name)
    if from_path:
        candidates.append(from_path)

    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


def _chromium_options(browser: str, download_dir: str = None):
    opts = webdriver.EdgeOptions() if browser == 'edge' else webdriver.ChromeOptions()
    opts.add_argument('--window-position=-32000,-32000') 
    opts.add_argument('--window-size=1280,720')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--log-level=3')
    opts.add_argument('--disable-blink-features=AutomationControlled')

    try:
        opts.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        opts.add_experimental_option('useAutomationExtension', False)
    except Exception:
        pass

    prefs = {
        'safebrowsing.enabled': False,
        'profile.default_content_setting_values.popups': 2,
        'profile.default_content_setting_values.notifications': 2,
    }
    if download_dir:
        prefs['download.default_directory']  = download_dir
        prefs['download.prompt_for_download'] = False
        prefs['download.directory_upgrade']   = True
    try:
        opts.add_experimental_option('prefs', prefs)
    except Exception:
        pass

    binary = _find_binary(browser)
    if binary:
        opts.binary_location = binary

    return opts


def create_webdriver(browser: str, download_dir: str = None):
    opts = _chromium_options(browser, download_dir)

    def _try_service(service_obj):
        if browser == 'edge':
            d = webdriver.Edge(service=service_obj, options=opts)
        else:
            d = webdriver.Chrome(service=service_obj, options=opts)
        try:
            d.execute_cdp_cmd('Network.enable', {})
        except Exception:
            pass
        return d

    last_error = None
    local = _find_driver(browser)
    if local:
        try:
            svc = EdgeService(local) if browser == 'edge' else ChromeService(local)
            return _try_service(svc)
        except Exception as e:
            last_error = e

    try:
        svc = EdgeService() if browser == 'edge' else ChromeService()
        return _try_service(svc)
    except Exception as e:
        last_error = e

    try:
        if browser == 'edge':
            svc = EdgeService(EdgeChromiumDriverManager().install())
        else:
            svc = ChromeService(ChromeDriverManager().install())
        return _try_service(svc)
    except Exception as e:
        last_error = e

    if last_error:
        raise last_error
    return None


def _get_driver(download_dir: str = None):
    err_msgs = []
    for browser in ('chrome', 'edge'):
        if _find_binary(browser): 
            try:
                d = create_webdriver(browser, download_dir)
                if d is not None:
                    return d
            except Exception as e:
                err_msgs.append(f"{browser.upper()}: {str(e)}")
    if err_msgs:
        raise RuntimeError("Помилка ініціалізації драйверів:\n\n" + "\n".join(err_msgs))
    raise RuntimeError(tr('browser_not_found'))


def _wait_cf(driver, timeout: int = 15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        t = driver.title.lower()
        if 'moment' not in t and 'cloudflare' not in t and 'just a sec' not in t:
            return
        time.sleep(0.5)


# ════════════════════════════════════════════════════════════════
# BAKKESPLUGINS SCRAPER
# ════════════════════════════════════════════════════════════════

def get_bakkes_maps(page: int = 1, search_query: str = '') -> list:
    import re as _re
    import urllib.request
    import urllib.parse
    from bs4 import BeautifulSoup

    BASE = 'https://bakkesplugins.com'
    url = f"{BASE}/maps"
    params = []
    
    if search_query:
        params.append(f"search={urllib.parse.quote(search_query)}")
    if page > 1:
        params.append(f"page={page}")
    if params:
        url += "?" + "&".join(params)

    html = ""
    
    # ── 1. СПРОБА ШВИДКОГО HTTP-ЗАПИТУ (Обхід Selenium) ──
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8')
            
    except Exception as e:
        # ── 2. ФОЛБЕК НА SELENIUM (Якщо Cloudflare заблокував) ──
        # Якщо спіймали 403 або іншу помилку, падаємо на наш оптимізований Singleton-драйвер
        try:
            driver = _get_driver() # Викликаємо драйвер з Кроку 1
            driver.get(url)
            _wait_cf(driver)
            
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/maps/']"))
                )
            except Exception:
                pass
                
            html = driver.page_source
        except Exception as driver_e:
            raise RuntimeError(f"Помилка завантаження сторінки: {driver_e}") from driver_e

    # ── 3. ПАРСИНГ HTML (Твоя логіка залишається без змін) ──
    soup = BeautifulSoup(html, 'html.parser')
    maps = []
    seen = set()
    
    for a in soup.find_all('a', href=_re.compile(r'^/maps/\d+$')):
        href = a.get('href', '')
        mid  = _re.search(r'/maps/(\d+)$', href)
        if not mid: continue
        mid  = mid.group(1)
        if mid in seen: continue
        seen.add(mid)
        
        text   = a.get_text(separator=' ', strip=True)
        rm     = _re.search(r'(⭐\s*\d+(?:\.\d+)?(?:\s*\(\d+\))?)', text)
        rating = rm.group(1) if rm else ''
        
        title_el = a.find(['h3', 'h2', 'h1', 'strong'])
        if title_el:
            title = title_el.get_text(strip=True)
        else:
            title = text.split('View Details')[0].strip()
            title = _re.sub(r'⭐\s*\d+(?:\.\d+)?(?:\s*\(\d+\))?\s*', '', title)
            title = _re.sub(r'^v\d+\.\d+\S*\s+', '', title).strip()[:80]
        title = title or tr('unknown_map')
        
        img     = a.find('img')
        preview = None
        if img:
            s = img.get('src') or img.get('data-src', '')
            if s and s.startswith('http'): preview = s

        # Розумний пошук автора
        author = ""
        author_span = a.find('span', class_=lambda c: c and 'truncate' in c and 'text-sm' in c)
        
        if not author_span:
            parent = a.parent
            for _ in range(4): 
                if not parent or parent.name == 'body':
                    break
            
                links = parent.find_all('a', href=_re.compile(r'^/maps/\d+$'))
                mids = set()
                for l in links:
                    m = _re.search(r'/maps/(\d+)', l.get('href', ''))
                    if m: mids.add(m.group(1))
                    
                if len(mids) > 1:
                    break
                    
                author_span = parent.find('span', class_=lambda c: c and 'truncate' in c and 'text-sm' in c)
                if author_span:
                    break
                parent = parent.parent

        if author_span and author_span.get('title'):
            author = "By " + author_span.get('title')
        elif author_span:
            author = "By " + author_span.get_text(strip=True)

        maps.append({
            'title':       title,
            'map_id':      mid,
            'page_url':    BASE + href,
            'preview_url': preview,
            'rating':      rating.strip() if rating else '',
            'author':      author,
        })
        
    return maps

def download_map_natively(map_info: dict) -> tuple:
    import time
    page_url = map_info.get('page_url', '')
    if not page_url:
        raise Exception("Не знайдено посилання на сторінку карти.")
    temp_dl_dir = os.path.abspath(tempfile.mkdtemp())
    driver      = None
    try:
        driver = _get_driver(download_dir=temp_dl_dir)
        try:
            driver.execute_cdp_cmd('Page.setDownloadBehavior', {
                'behavior':     'allow',
                'downloadPath': temp_dl_dir,
            })
        except Exception:
            pass
        driver.get(page_url)
        _wait_cf(driver, timeout=20)
        time.sleep(3) 
        try:
            script_click_arrow = """
            var btns = Array.from(document.querySelectorAll('button'));
            var installBtn = btns.find(b => b.innerText.includes('Install'));
            if (installBtn && installBtn.nextElementSibling && installBtn.nextElementSibling.tagName === 'BUTTON') {
                installBtn.nextElementSibling.scrollIntoView({block: 'center'});
                installBtn.nextElementSibling.click();
                return true;
            }
            return false;
            """
            if not driver.execute_script(script_click_arrow):
                install_btn = driver.find_element(By.XPATH, "//button[contains(., 'Install')]")
                arrow_btn = install_btn.find_element(By.XPATH, "following-sibling::button")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", arrow_btn)
                arrow_btn.click()
        except Exception:
            pass
        time.sleep(1.5)
        clicked = False
        try:
            script_click_zip = """
            var els = Array.from(document.querySelectorAll('a, button, div[role="menuitem"], span, p'));
            var visibleEls = els.filter(el => el.offsetWidth > 0 && el.offsetHeight > 0);
            for (var i = 0; i < visibleEls.length; i++) {
                var text = (visibleEls[i].innerText || '').toLowerCase().trim();
                if (text.includes('zip') && text.length < 30) {
                    var target = visibleEls[i].closest('a') || visibleEls[i].closest('button') || visibleEls[i];
                    target.scrollIntoView({block: 'center'});
                    if (target.tagName === 'A' && target.href) {
                        window.location.href = target.href;
                    } else {
                        target.click();
                    }
                    return true;
                }
            }
            return false;
            """
            if driver.execute_script(script_click_zip):
                clicked = True
            else:
                zip_els = driver.find_elements(By.XPATH, "//*[contains(translate(., 'ZIP', 'zip'), 'zip')]")
                for el in zip_els:
                    if el.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                        time.sleep(0.5)
                        try:
                            el.click()
                        except:
                            driver.execute_script("arguments[0].click();", el)
                        clicked = True
                        break
        except Exception:
            pass
        if not clicked:
            fallback_script = """
            var mapId = window.location.pathname.split('/').filter(Boolean).pop();
            var html  = document.documentElement.innerHTML;
            var vId = null;
            var m = html.match(/"versions":\\s*\\[\\s*\\{\\s*"id":\\s*(\\d+)/);
            if (m) vId = m[1];
            if (vId && mapId) {
                var url = 'https://bakkesplugins.com/api/rocket-league-maps/' + mapId + '/download/' + vId;
                fetch(url, { method: 'POST', headers: { accept: 'application/json' } })
                .then(r => r.json())
                .then(data => {
                    if (data && (data.url || data.downloadUrl)) {
                        window.location.href = data.url || data.downloadUrl;
                    }
                }).catch(e => console.log(e));
            }
            """
            driver.execute_script(fallback_script)
        timeout     = 180  
        start       = time.time()
        dl_file     = None
        started     = False
        while time.time() - start < timeout:
            files = os.listdir(temp_dl_dir)
            if files:
                started = True
            done = [f for f in files if not f.endswith('.crdownload') and not f.endswith('.tmp')]
            if done:
                path = os.path.join(temp_dl_dir, done[0])
                s1   = os.path.getsize(path)
                time.sleep(2.0)
                if os.path.exists(path) and os.path.getsize(path) == s1 and s1 > 0:
                    dl_file = path
                    break
            else:
                if not started and time.time() - start > 35:
                    raise RuntimeError('Завантаження не почалося.')
            time.sleep(1)
        if not dl_file:
            raise RuntimeError('Час очікування завантаження вийшов.')
        with open(dl_file, 'rb') as f:
            data = f.read()
        name = os.path.basename(dl_file)
        driver.quit(); driver = None
        shutil.rmtree(temp_dl_dir, ignore_errors=True)
        return data, name
    except Exception as e:
        if driver:
            try: driver.quit()
            except Exception: pass
        shutil.rmtree(temp_dl_dir, ignore_errors=True)
        raise e


def extract_map_from_zip(zip_path: str, dest_folder: str):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        entries = [
            i for i in zf.infolist()
            if os.path.splitext(i.filename)[1].lower() in CUSTOM_MAP_EXTENSIONS
            and not i.filename.startswith('__MACOSX')
            and i.file_size > 0
        ]
        if not entries:
            return None, None
        best = max(entries, key=lambda i: i.file_size)
        with tempfile.TemporaryDirectory() as tmp:
            zf.extract(best, tmp)
            src  = os.path.join(tmp, best.filename)
            name = os.path.basename(best.filename)
            dest = os.path.join(dest_folder, name)
            shutil.move(src, dest)
    return name, dest


def sanitize_filename(name: str, default: str = 'map', max_len: int = 120) -> str:
    bad  = '<>:"/\\|?*'
    out  = ''.join('_' if c in bad or ord(c) < 32 else c for c in name)
    out  = out.replace(' ', '_').strip(' ._')
    out  = out[:max_len].rstrip('._') if len(out) > max_len else out
    return out or default


def normalize_path(path: str) -> str:
    if os.name == 'nt':
        p = os.path.abspath(path)
        if len(p) >= 260 and not p.startswith('\\\\?\\'):
            return '\\\\?\\' + p
        return p
    return path


def download_image(url: str):
    if not url:
        return None
    try:
        # Тут використовуємо url, а не api_url
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
            
        import io
        img = Image.open(io.BytesIO(data)).resize((160, 90), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
        
    except HTTPError as e:
        logging.warning(f"Сервер відхилив запит зображення. Код: {e.code} для URL: {url}")
    except URLError as e:
        logging.error(f"Помилка мережі при завантаженні зображення: {e.reason}")
    except Exception as e:
        logging.error(f"Помилка обробки зображення: {e}", exc_info=True)
        
    return None


def find_rocket_league_root():
    pf = Path(os.environ.get('PROGRAMFILES', r'C:\Program Files'))
    pf86 = Path(os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)'))
    
    common = [
        pf86 / 'Steam' / 'steamapps' / 'common' / 'rocketleague',
        pf / 'Steam' / 'steamapps' / 'common' / 'rocketleague',
        pf / 'Epic Games' / 'rocketleague',
        pf86 / 'Epic Games' / 'rocketleague',
    ]
    
    def _valid(p: Path):
        return p.is_dir() and ((p / 'TAGame').is_dir() or (p / 'Binaries').is_dir())
    
    for p in common:
        if _valid(p): return str(p)
        
    # Пошук по всіх дисках
    drives = [Path(f'{d}:\\') for d in string.ascii_uppercase if Path(f'{d}:\\').exists()]
    suffixes = [
        Path('SteamLibrary/steamapps/common/rocketleague'),
        Path('Steam/steamapps/common/rocketleague'),
        Path('Epic Games/rocketleague'),
        Path('Games/rocketleague'),
    ]
    
    for drv in drives:
        for sfx in suffixes:
            p = drv / sfx
            if _valid(p): return str(p)
            
    return None


def find_maps_folder(rl_root: str):
    if not rl_root: return None
    root = Path(rl_root)
    
    for sfx in CUSTOM_MAP_FOLDER_NAMES:
        # pathlib автоматично розбере подвійні бекслеші з твого списку CUSTOM_MAP_FOLDER_NAMES
        p = root / sfx
        if p.is_dir(): return str(p)
        
    return None


def find_rocket_league_executable(rl_root: str):
    if not rl_root: return None
    root = Path(rl_root)
    
    for rel in ('Binaries/Win64/RocketLeague.exe',
                'Binaries/Win64/RocketLeague-Win64-Shipping.exe',
                'RocketLeague.exe'):
        p = root / rel
        if p.is_file(): return str(p)
        
    return None


def launch_rocket_league(rl_root: str, extra_args: str = ''):
    exe = find_rocket_league_executable(rl_root)
    if not exe:
        raise FileNotFoundError('RocketLeague.exe not found')
    args = [exe] + (shlex.split(extra_args) if extra_args else [])
    subprocess.Popen(args, cwd=os.path.dirname(exe))


def is_custom_map_file(path: str) -> bool:
    return os.path.isfile(path) and os.path.splitext(path)[1].lower() in CUSTOM_MAP_EXTENSIONS


def list_custom_maps(folder: str) -> list:
    if not folder or not os.path.isdir(folder): return []
    return sorted(f for f in os.listdir(folder)
                  if is_custom_map_file(os.path.join(folder, f)))


def list_standard_maps(maps_folder: str) -> list:
    if not maps_folder or not os.path.isdir(maps_folder): return []
    allowed = {'labs_underpass_p', 'labs_basin_p', 'labs_utopia_p',
               'labs_corridor_p', 'labs_cosmic_p'}
    out = []
    for f in os.listdir(maps_folder):
        if not os.path.isfile(os.path.join(maps_folder, f)): continue
        if os.path.splitext(f)[1].lower() not in CUSTOM_MAP_EXTENSIONS: continue
        if os.path.splitext(f)[0].lower() in allowed:
            out.append(f)
    return sorted(out)


class Tooltip:
    def __init__(self, widget, text):
        self.widget  = widget
        self.text    = text
        self.tip_win = None
        widget.bind('<Enter>', self._show)
        widget.bind('<Leave>', self._hide)
    def _show(self, _event):
        if self.tip_win: return
        try:
            x, y, *_ = self.widget.bbox('insert')
        except Exception:
            x = y = 0
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f'+{x}+{y}')
        dark = HAS_SV_TTK and sv_ttk.get_theme() == 'dark'
        tk.Label(tw, text=self.text,
                 bg='#333' if dark else '#ffffcc',
                 fg='#fff' if dark else '#000',
                 relief='solid', borderwidth=1, padx=5, pady=2).pack()
    def _hide(self, _event):
        if self.tip_win:
            self.tip_win.destroy()
            self.tip_win = None


# ════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ════════════════════════════════════════════════════════════════

class MapLoaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(tr('app_title'))
        self.geometry('1280x660')
        self.resizable(False, False)

        self._cfg          = load_config()
        self.lang          = self._cfg.get('language', 'en')
        self._set_lang(self.lang)

        self.theme_mode    = tk.StringVar(value=self._cfg.get('theme', 'dark'))
        self.language_opt  = tk.StringVar(value=LANGUAGE_NAMES.get(self.lang, 'English'))
        self.close_code    = tk.StringVar(value=self._cfg.get('close_action', 'restore_and_exit'))
        self._close_lbl    = tk.StringVar(value=self._t(self.close_code.get()))
        self.auto_update_var = tk.BooleanVar(value=self._cfg.get('auto_update', True))
        
        self.always_on_top_var = tk.BooleanVar(value=self._cfg.get('always_on_top', False))
        self.attributes('-topmost', self.always_on_top_var.get())

        self.custom_folder = tk.StringVar(value=self._cfg.get('custom_maps_folder', ''))
        self.rl_root_var   = tk.StringVar(value=self._cfg.get('rl_root', ''))
        self.maps_folder   = tk.StringVar(value=self._cfg.get('maps_folder', ''))
        self.sel_custom    = tk.StringVar()
        self.sel_standard  = tk.StringVar()
        self.status_var    = tk.StringVar(value=tr('status_default'))
        self.dl_status_var = tk.StringVar()
        self.replacements  = []
        self.bakkes_maps   = []
        self.map_info_db   = {}
        self.current_page  = 1
        self.search_var    = tk.StringVar()

        if HAS_SV_TTK:
            sv_ttk.set_theme(self.theme_mode.get())

        self._build_ui()
        self._apply_win_style()
        self.protocol('WM_DELETE_WINDOW', self._on_close)
        
        # Перевірка наявності шляхів при старті та автозавантаження списків
        if not self.rl_root_var.get():
            self.auto_detect_rl()
        elif not self.maps_folder.get():
            self._update_maps_folder()
            
        self._refresh_all() # Відновлюємо завантаження локальних карт при старті
            
        self.after(1000, lambda: self.load_bakkes_maps(reset=True))
        self.after(3000, self.check_for_updates)

    def _set_lang(self, code):
        global CURRENT_LANGUAGE
        self.lang = code
        CURRENT_LANGUAGE = code

    def _t(self, key, **kw):
        return tr(key, **kw)

    def _save_cfg(self):
        self._cfg.update({
            'language':          self.lang,
            'theme':             self.theme_mode.get(),
            'close_action':      self.close_code.get(),
            'custom_maps_folder': self.custom_folder.get(),
            'rl_root':           self.rl_root_var.get(),
            'maps_folder':       self.maps_folder.get(),
            'auto_update':       self.auto_update_var.get(),
            'always_on_top':     self.always_on_top_var.get(), # <-- ДОДАТИ ЦЕЙ РЯДОК
        })
        save_config(self._cfg)

    def _apply_win_style(self):
        if HAS_PYWINSTYLES:
            try:
                pywinstyles.apply_style(self, 'dark' if self.theme_mode.get() == 'dark' else 'light')
                pywinstyles.apply_style(self, 'mica')
            except Exception:
                pass

    def _make_scrollable(self, parent):
        canvas = tk.Canvas(parent, highlightthickness=0)
        sb     = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        inner  = ttk.Frame(canvas)
        inner.bind('<Configure>', lambda _: canvas.configure(scrollregion=canvas.bbox('all')))
        win = canvas.create_window((0, 0), window=inner, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(win, width=e.width))
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        def _scroll(event):
            try:
                if not canvas.winfo_exists(): return
                rx, ry = canvas.winfo_rootx(), canvas.winfo_rooty()
                mx, my = canvas.winfo_pointerxy()
                if rx <= mx <= rx + canvas.winfo_width() and ry <= my <= ry + canvas.winfo_height():
                    canvas.yview_scroll(int(-1 * event.delta / 120), 'units')
            except Exception:
                pass
        self.bind('<MouseWheel>', _scroll, add='+')
        return canvas, inner

    def _show_progress(self, msg=''):
        self.dl_status_var.set(msg)
        self._progress.start(10)
        self._progress_frame.pack(fill='x', pady=(0, 4))

    def _hide_progress(self, msg=''):
        self._progress.stop()
        self.dl_status_var.set(msg)
        self._progress_frame.pack_forget()

    def _build_ui(self):
        self.title(self._t('app_title'))
        
        self._build_topbar()
        self._build_bottom_logo()
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        lf = ttk.Frame(self.notebook)
        self.notebook.add(lf, text=self._t('local_maps_tab'))
        self._build_local_tab(lf)

        df = ttk.Frame(self.notebook)
        self.notebook.add(df, text=self._t('download_maps_tab'))
        self._build_download_tab(df)

        hf = ttk.Frame(self.notebook)
        self.notebook.add(hf, text=self._t('help_tab'))
        self._build_help_tab(hf)

    def _build_topbar(self):
        bar = ttk.Frame(self, padding=6)
        bar.pack(fill='x')

        logo_path = resource_path('logo.ico')
        if os.path.isfile(logo_path):
            try:
                img = Image.open(logo_path)
                self.app_icon = ImageTk.PhotoImage(img)
                self.iconphoto(True, self.app_icon)
                small = img.resize((36, 36), Image.Resampling.LANCZOS)
                self._logo_img = ImageTk.PhotoImage(small)
                ttk.Label(bar, image=self._logo_img).pack(side='left', padx=(4, 10))
            except Exception:
                pass

        # ── Кнопка Налаштування ──
        btn_settings = ttk.Button(bar, text="🔧 " + self._t('settings'), command=self._open_settings)
        btn_settings.pack(side='right', padx=4)
        Tooltip(btn_settings, self._t('tt_settings'))  # <--- Додано Tooltip

        if HAS_SV_TTK:
            icon = '🔆' if self.theme_mode.get() == 'dark' else '🌙'
            self._theme_btn = ttk.Button(bar, text=icon, width=3, command=self._toggle_theme)
            self._theme_btn.pack(side='right', padx=(5, 5))
            Tooltip(self._theme_btn, self._t('tt_theme')) # <--- Додано Tooltip

        # Галочка автооновлення на верхній панелі
        auto_update_text = "Автооновлення" if self.lang == 'uk' else "Auto-update"
        ttk.Checkbutton(
            bar, 
            text=auto_update_text, 
            variable=self.auto_update_var, 
            command=self._save_cfg
        ).pack(side='left', padx=(15, 4))

        # Кнопка ручної перевірки оновлень
        ttk.Button(bar, text=self._t('check_update'), command=self.manual_check_for_updates).pack(side='left', padx=4)

        # ── Кнопка запуску гри (найправіша) ──
        btn_launch = ttk.Button(bar, text=self._t('launch_game'), command=self._launch_rl)
        btn_launch.pack(side='right', padx=4)
        Tooltip(btn_launch, self._t('tt_launch')) # <--- Додано Tooltip


    def _open_settings(self):
        win = tk.Toplevel(self)
        win.title(self._t('settings'))
        win.geometry('650x350') # Збільшено висоту вікна
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        temp_lang = tk.StringVar(value=self.language_opt.get())
        temp_close = tk.StringVar(value=self._close_lbl.get())
        temp_root = tk.StringVar(value=self.rl_root_var.get())
        temp_maps = tk.StringVar(value=self.maps_folder.get())
        temp_topmost = tk.BooleanVar(value=self.always_on_top_var.get())

        f = ttk.Frame(win, padding=15)
        f.pack(fill='both', expand=True)

        # Мова
        ttk.Label(f, text=self._t('language')).grid(row=0, column=0, sticky='w', pady=8)
        lang_cb = ttk.Combobox(f, values=list(LANGUAGE_NAMES.values()), textvariable=temp_lang, state='readonly', width=25)
        lang_cb.grid(row=0, column=1, sticky='w', pady=8, padx=10)

        # Поведінка при закритті
        ttk.Label(f, text=self._t('close_behavior')).grid(row=1, column=0, sticky='w', pady=8)
        close_cb = ttk.Combobox(f, values=[self._t('restore_and_exit'), self._t('minimize_to_tray')], textvariable=temp_close, state='readonly', width=25)
        close_cb.grid(row=1, column=1, sticky='w', pady=8, padx=10)

        # Корінь гри
        ttk.Label(f, text=self._t('rl_root')).grid(row=2, column=0, sticky='w', pady=8)
        rf = ttk.Frame(f)
        rf.grid(row=2, column=1, sticky='w', pady=8, padx=10)
        ttk.Entry(rf, textvariable=temp_root, width=40).pack(side='left')
        
        def browse_rl():
            p = filedialog.askdirectory()
            if p: temp_root.set(p)
            
        def auto_detect():
            root = find_rocket_league_root()
            if root: 
                temp_root.set(root)
                mf_found = find_maps_folder(root)
                if mf_found: temp_maps.set(mf_found)
                
        ttk.Button(rf, text=self._t('browse'), command=browse_rl).pack(side='left', padx=4)
        ttk.Button(rf, text=self._t('auto_detect'), command=auto_detect).pack(side='left', padx=4)

        # Папка з картами в грі
        ttk.Label(f, text=self._t('maps_folder')).grid(row=3, column=0, sticky='w', pady=8)
        mf = ttk.Frame(f)
        mf.grid(row=3, column=1, sticky='w', pady=8, padx=10)
        ttk.Entry(mf, textvariable=temp_maps, width=40).pack(side='left')
        
        def refresh_mf():
            mf_found = find_maps_folder(temp_root.get().strip())
            if mf_found: temp_maps.set(mf_found)
            
        ttk.Button(mf, text=self._t('refresh'), command=refresh_mf).pack(side='left', padx=4)

        ttk.Checkbutton(f, text=self._t('always_on_top'), variable=temp_topmost).grid(row=4, column=0, columnspan=2, sticky='w', pady=(8, 0))

        bf = ttk.Frame(win, padding=10)
        bf.pack(side='bottom', fill='x')

        def save():
            lang_changed = (self.language_opt.get() != temp_lang.get())
            
            self.language_opt.set(temp_lang.get())
            self._close_lbl.set(temp_close.get())
            self.rl_root_var.set(temp_root.get())
            self.maps_folder.set(temp_maps.get())

            self.always_on_top_var.set(temp_topmost.get())
            self.attributes('-topmost', self.always_on_top_var.get())
            
            self._on_close_action_change()
            self._save_cfg()
            self._refresh_standard()
            
            win.destroy()
            
            if lang_changed:
                self._on_lang_change()

        # Додано width=15 та збільшено відступи, щоб текст 100% влазив
        ttk.Button(bf, text=self._t('save'), width=15, command=save, style='Accent.TButton').pack(side='right', padx=5, pady=(0, 5))
        ttk.Button(bf, text=self._t('cancel'), width=15, command=win.destroy).pack(side='right', padx=5, pady=(0, 5))


    def _build_bottom_logo(self):
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side='bottom', fill='x', padx=15, pady=(0, 5))
        
        logo_path = resource_path('logo.ico')
        if os.path.isfile(logo_path):
            try:
                img = Image.open(logo_path)
                tiny = img.resize((20, 20), Image.Resampling.LANCZOS)
                self._bottom_logo_img = ImageTk.PhotoImage(tiny)
                ttk.Label(bottom_frame, image=self._bottom_logo_img).pack(side='left', padx=(0, 5))
            except Exception:
                pass
        
        ttk.Label(bottom_frame, text="made by ItsAndreww", font=('Arial', 8, 'italic'), foreground='gray').pack(side='left')

        ttk.Label(
            bottom_frame, 
            text=f"v{VERSION}", 
            font=('Arial', 8, 'bold'), 
            foreground='gray'
        ).pack(side='right')

    def _build_local_tab(self, parent):
        f = ttk.Frame(parent, padding=12)
        f.pack(fill='both', expand=True)
        sel = ttk.Frame(f)
        sel.pack(fill='x', pady=(0, 10))
        ttk.Label(sel, text=self._t('selected_custom')).pack(side='left')
        ttk.Label(sel, textvariable=self.sel_custom, foreground='#0078d4', font=('Arial', 10, 'bold')).pack(side='left', padx=8)
        ttk.Label(sel, text=self._t('selected_standard')).pack(side='left', padx=(20, 0))
        ttk.Label(sel, textvariable=self.sel_standard, foreground='#d83b01', font=('Arial', 10, 'bold')).pack(side='left', padx=8)
        
        r = ttk.Frame(f)
        r.pack(fill='x', pady=2)
        ttk.Label(r, text=self._t('custom_maps_folder'), width=25).pack(side='left')
        ttk.Entry(r, textvariable=self.custom_folder, width=50).pack(side='left', padx=8)
        ttk.Button(r, text=self._t('browse'), command=self._browse_custom).pack(side='left')

        cols = ttk.Frame(f); cols.pack(fill='both', expand=True, pady=8)
        def col(title_key):
            lf = ttk.LabelFrame(cols, text=self._t(title_key))
            lf.pack(side='left', fill='both', expand=True, padx=4)
            return self._make_scrollable(lf)
        _, self._custom_frame      = col('custom_maps')
        _, self._replace_frame     = col('replacement_history')
        _, self._standard_frame    = col('standard_maps')
        btns = ttk.Frame(f); btns.pack(fill='x', pady=8)
        btns = ttk.Frame(f); btns.pack(fill='x', pady=8)
        rb = ttk.Button(btns, text=self._t('refresh_lists'), command=self._refresh_all)
        rb.pack(side='left', padx=10)
        
        rpb = ttk.Button(btns, text=self._t('replace_map'), command=self._do_replace, style='Accent.TButton')
        rpb.pack(side='right', padx=10)
        Tooltip(rpb, self._t('tt_replace')) # <--- Додано Tooltip
        
        ttk.Label(f, textvariable=self.status_var, foreground='blue').pack(anchor='w')

    def _build_download_tab(self, parent):
        f = ttk.Frame(parent, padding=12)
        f.pack(fill='both', expand=True)
        top = ttk.Frame(f); top.pack(fill='x', pady=6)
        ttk.Entry(top, textvariable=self.search_var, width=30).pack(side='left', padx=(0, 5))
        ttk.Button(top, text=self._t('search'),
                   command=lambda: self.load_bakkes_maps(reset=True)).pack(side='left')
        self._btn_prev = ttk.Button(top, text='◄', width=3, command=self._prev_page, state='disabled')
        self._btn_prev.pack(side='left', padx=(30, 5))
        self._page_lbl = tk.StringVar(value=f"{self._t('page')} 1")
        ttk.Label(top, textvariable=self._page_lbl, font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self._btn_next = ttk.Button(top, text='►', width=3, command=self._next_page, state='disabled')
        self._btn_next.pack(side='left', padx=5)
        self._progress_frame = ttk.Frame(f)
        self._progress_frame.pack(fill='x', pady=(0, 4))
        self._progress = ttk.Progressbar(self._progress_frame, mode='indeterminate')
        self._progress.pack(fill='x', expand=True)
        ttk.Label(self._progress_frame, textvariable=self.dl_status_var).pack(anchor='w', pady=(2, 0))
        self._progress_frame.pack_forget()
        lf = ttk.Frame(f); lf.pack(fill='both', expand=True)
        _, self._dl_frame = self._make_scrollable(lf)

    def _build_help_tab(self, parent):
        f = ttk.Frame(parent, padding=20)
        f.pack(fill='both', expand=True)
        
        txt = tk.Text(f, wrap='word', font=('Arial', 11), relief='flat', padx=10, pady=10)
        txt.pack(side='left', fill='both', expand=True)
        
        sb = ttk.Scrollbar(f, orient='vertical', command=txt.yview)
        sb.pack(side='right', fill='y')
        txt.configure(yscrollcommand=sb.set)
        
        txt.insert('1.0', self._t('help_text'))
        txt.configure(state='disabled')
        
        if HAS_SV_TTK and sv_ttk.get_theme() == 'dark':
            txt.configure(bg='#1e1e1e', fg='#ffffff', insertbackground='#ffffff')
        else:
            txt.configure(bg='#f3f3f3', fg='#000000', insertbackground='#000000')

    def _on_lang_change(self, _=None):
        disp = self.language_opt.get()
        for code, label in LANGUAGE_NAMES.items():
            if label == disp:
                self._set_lang(code); break
        self._save_cfg()
        self._rebuild()

    def _toggle_theme(self):
        new = 'light' if self.theme_mode.get() == 'dark' else 'dark'
        self.theme_mode.set(new)
        if HAS_SV_TTK: sv_ttk.set_theme(new)
        self._apply_win_style()
        self._theme_btn.config(text='🔆' if new == 'dark' else '🌙')
        self._save_cfg()

    def _on_close_action_change(self, _=None):
        self.close_code.set(
            'minimize_to_tray' if self._close_lbl.get() == self._t('minimize_to_tray')
            else 'restore_and_exit'
        )
        self._save_cfg()

    def _launch_rl(self):
        root = self.rl_root_var.get().strip()
        if not root:
            messagebox.showerror(self._t('error_title'), self._t('error_no_rl_root'))
            return
        try:
            launch_rocket_league(root)
            messagebox.showinfo(self._t('info_title'), self._t('launch_success'))
        except Exception as e:
            messagebox.showerror(self._t('error_title'), self._t('launch_failed', error=e))

    def _tray_icon_image(self):
        logo_path = resource_path('logo.ico')
        if os.path.isfile(logo_path):
            try:
                return Image.open(logo_path).convert('RGBA').resize((64, 64), Image.Resampling.LANCZOS)
            except Exception:
                pass
        
        img  = Image.new('RGB', (64, 64), (0, 102, 204))
        draw = ImageDraw.Draw(img)
        draw.rectangle((16, 16, 48, 48), fill=(255, 255, 255))
        return img

    def _on_close(self):
        if self.close_code.get() == 'minimize_to_tray':
            if HAS_PYSTRAY:
                self.withdraw()
                menu = (item(self._t('show_app'), lambda ic, _: (ic.stop(), self.after(0, self.deiconify))),
                        item(self._t('exit_app'),  lambda ic, _: (ic.stop(), self.after(0, self._restore_exit))))
                threading.Thread(
                    target=pystray.Icon('RL', self._tray_icon_image(), 'RL Map Loader', menu).run,
                    daemon=True).start()
                return
            else:
                messagebox.showwarning(self._t('info_title'), self._t('tray_unavailable'))
        self._restore_exit()

    def _restore_exit(self):
        for e in list(self.replacements):
            try:
                if os.path.isfile(e['backup_path']):
                    os.replace(e['backup_path'], e['standard_path'])
            except Exception:
                pass
        self.destroy()

    def _rebuild(self):
        for c in self.winfo_children(): c.destroy()
        self._build_ui()
        self._refresh_all()

    def _browse_custom(self):
        p = filedialog.askdirectory()
        if p:
            self.custom_folder.set(p); self._save_cfg(); self._refresh_custom()

    def _browse_rl(self):
        p = filedialog.askdirectory()
        if p:
            self.rl_root_var.set(p); self._save_cfg(); self._update_maps_folder()

    def auto_detect_rl(self):
        root = find_rocket_league_root()
        if root:
            self.rl_root_var.set(root); self._save_cfg()
            self._update_maps_folder()
            self.status_var.set(self._t('auto_detect_success'))
        else:
            self.status_var.set(self._t('auto_detect_fail'))

    def _update_maps_folder(self):
        mf = find_maps_folder(self.rl_root_var.get().strip())
        if mf:
            self.maps_folder.set(mf); self._save_cfg(); self._refresh_standard()
        else:
            self.maps_folder.set(''); self.status_var.set(self._t('maps_folder_not_found'))

    def _load_map_info(self):
        folder = self.custom_folder.get().strip()
        self.map_info_db = {}
        if folder and os.path.isdir(folder):
            info_file = os.path.join(folder, 'map_info.json')
            if os.path.isfile(info_file):
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        self.map_info_db = json.load(f)
                except Exception:
                    pass

    def _save_map_info(self):
        folder = self.custom_folder.get().strip()
        if folder and os.path.isdir(folder) and self.map_info_db:
            info_file = os.path.join(folder, 'map_info.json')
            try:
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(self.map_info_db, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logging.error(f"Failed to save map info: {e}", exc_info=True)

    def _refresh_all(self):
        self._load_map_info()
        self._refresh_custom()
        self._refresh_standard()
        self._render_replacements()
        
        # Перевіряємо, чи вказані папки. Якщо так - міняємо дефолтний статус
        if self.custom_folder.get().strip() and self.rl_root_var.get().strip():
            if self.status_var.get() == self._t('status_default'):
                self.status_var.set(self._t('status_ready'))
        else:
            self.status_var.set(self._t('status_default'))

    def _refresh_custom(self):
        for w in self._custom_frame.winfo_children(): w.destroy()
        
        folder = self.custom_folder.get().strip()
        if not folder or not os.path.isdir(folder):
            return
            
        maps = list_custom_maps(folder)
        
        # Просто беремо інфо з кешу в пам'яті
        for m in maps:
            self._custom_tile(self._custom_frame, m, self.map_info_db.get(m, {}))

    def _refresh_standard(self):
        for w in self._standard_frame.winfo_children(): w.destroy()
        for m in list_standard_maps(self.maps_folder.get()):
            self._std_tile(self._standard_frame, m)

    def _custom_tile(self, parent, filename, info):
        tile = ttk.Frame(parent, relief='raised', borderwidth=1)
        tile.pack(fill='x', pady=3, padx=3)

        # ── Зображення ──
        img_lbl = ttk.Label(tile)
        img_lbl.pack(side='left', padx=5, pady=5)
        img_lbl.size = (144, 81)  # Зберігаємо розмір для подальшого використання при відсутності прев'ю

        # ── Блок інформації ──
        info_frame = ttk.Frame(tile)
        info_frame.pack(side='left', fill='both', expand=True, pady=5, padx=5)

        title = info.get('title')
        if not title:
            # Якщо метаданих немає, робимо чисту назву з файлу (без .upk і підкреслень)
            title = os.path.splitext(filename)[0].replace('_', ' ')

        title_lbl = ttk.Label(info_frame, text=title, font=('Arial', 10, 'bold'), wraplength=200, justify='left')
        title_lbl.pack(anchor='nw')

        author = info.get('author', '')
        if author:
            ttk.Label(info_frame, text=author, font=('Arial', 8), foreground='gray').pack(anchor='nw', pady=(2, 0))

        # ── Кнопки (Обрати / Видалити) ──
        bot_frame = ttk.Frame(info_frame)
        bot_frame.pack(side='bottom', fill='x', expand=True)

        is_selected = (self.sel_custom.get() == filename)
        btn_style = 'Accent.TButton' if is_selected else 'TButton'
        
        if is_selected:
            sel_text = '✓ Обрано' if self.lang == 'uk' else '✓ Selected'
        else:
            sel_text = 'Обрати' if self.lang == 'uk' else 'Select'
            
        sel_btn = ttk.Button(bot_frame, text=sel_text, style=btn_style,
                             command=lambda n=filename: self._select_map(n, True))
        sel_btn.pack(side='left')

        del_btn = ttk.Button(bot_frame, text='✕', width=3, command=lambda: self._delete_custom(filename))
        del_btn.pack(side='right')

       # ── Асинхронне завантаження картинки ──
        async def async_fetch_img():
            url = info.get('preview_url')  # <-- ТУТ ВИПРАВЛЕНО m на info
            img_width, img_height = 144, 81  # <-- ТУТ ПРАВИЛЬНІ РОЗМІРИ
            cache_key = f"{url}_{img_width}x{img_height}"
            
            # Якщо вже є в кеші — миттєво ставимо через Tkinter
            if url and cache_key in IMG_CACHE:
                self.after(0, lambda: img_lbl.config(image=IMG_CACHE[cache_key]))
                return

            pil_img = None
            if url:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, timeout=5) as r:
                            if r.status == 200:
                                data = await r.read()
                                import io
                                pil_img = Image.open(io.BytesIO(data)).resize((img_width, img_height), Image.Resampling.BILINEAR)
                except Exception as e:
                    logging.warning(f"Не вдалося завантажити картинку {url}: {e}")

            def apply_image():
                try:
                    if pil_img:
                        photo = ImageTk.PhotoImage(pil_img)
                        IMG_CACHE[cache_key] = photo
                    else:
                        img = Image.new('RGB', (img_width, img_height), '#333333' if self.theme_mode.get() == 'dark' else '#cccccc')
                        draw = ImageDraw.Draw(img)
                        draw.text((img_width//2, img_height//2), "No Image", fill="white", anchor="mm")
                        photo = ImageTk.PhotoImage(img)

                    img_lbl.image = photo 
                    img_lbl.config(image=photo)
                except Exception:
                    pass

            self.after(0, apply_image)

        asyncio.run_coroutine_threadsafe(async_fetch_img(), ASYNC_LOOP)

    def _std_tile(self, parent, name):
        btn_style = 'Accent.TButton' if self.sel_standard.get() == name else 'TButton'
        ttk.Button(parent, text=name, width=28, style=btn_style,
                   command=lambda n=name: self._select_map(n, False)).pack(pady=1, padx=4, fill='x')
        
    def _select_map(self, name, is_custom):
        if is_custom:
            self.sel_custom.set(name)
            self._refresh_custom()
        else:
            self.sel_standard.set(name)
            self._refresh_standard()

    def _delete_custom(self, name):
        if not messagebox.askyesno(self._t('info_title'), self._t('confirm_delete', name=name)):
            return
        p = os.path.join(self.custom_folder.get(), name)
        try:
            os.remove(p)
            
            # Видаляємо інфо з кешу, щоб файл не розростався сміттям
            if name in self.map_info_db:
                del self.map_info_db[name]
                self._save_map_info()
                
            if self.sel_custom.get() == name: self.sel_custom.set('')
            self.status_var.set(self._t('delete_success', name=name))
            self._refresh_custom()
        except Exception as e:
            messagebox.showerror(self._t('error_title'), self._t('delete_failed', error=e))

    def _render_replacements(self):
        for w in self._replace_frame.winfo_children(): w.destroy()
        for e in self.replacements:
            row = ttk.Frame(self._replace_frame, relief='raised', borderwidth=1)
            row.pack(fill='x', pady=3, padx=3)
            ttk.Label(row, text=f"{e['standard_map']} → {e['custom_map']}", font=('Arial', 9)
                      ).pack(side='left', padx=6, pady=4)
            ttk.Button(row, text=self._t('undo'), width=8,
                       command=lambda en=e: self._undo(en)).pack(side='right', padx=4, pady=4)

    def _undo(self, entry):
        if not os.path.isfile(entry['backup_path']):
            messagebox.showerror(self._t('error_title'), self._t('error_custom_not_found'))
            return
        try:
            os.replace(entry['backup_path'], entry['standard_path'])
            self.replacements.remove(entry)
            self._refresh_standard(); self._render_replacements()
        except Exception as e:
            messagebox.showerror(self._t('error_title'), self._t('replace_failed', error=e))

    def _do_replace(self):
        cm = self.sel_custom.get().strip()
        sm = self.sel_standard.get().strip()
        cf = self.custom_folder.get().strip()
        mf = self.maps_folder.get().strip()
        if not cm or not sm:
            messagebox.showerror(self._t('error_title'), self._t('error_no_custom_selected')); return
        cp = os.path.join(cf, cm)
        sp = os.path.join(mf, sm)
        if not os.path.isfile(cp):
            messagebox.showerror(self._t('error_title'), self._t('error_custom_not_found')); return
        if not os.path.isfile(sp):
            messagebox.showerror(self._t('error_title'), self._t('error_standard_not_found')); return
        base, ext  = os.path.splitext(sm)
        bak_name   = base + '_backup' + ext
        bak_path   = os.path.join(mf, bak_name)
        if not os.path.isfile(bak_path):
            try: shutil.copy2(sp, bak_path)
            except Exception as e:
                messagebox.showerror(self._t('error_title'), self._t('backup_failed', error=e)); return
        try:
            tmp = os.path.join(mf, 'temp_map.tmp')
            shutil.copy2(cp, tmp); os.replace(tmp, sp)
            existing = next((x for x in self.replacements if x['standard_map'] == sm), None)
            if existing: existing['custom_map'] = cm
            else: self.replacements.append({'custom_map': cm, 'standard_map': sm,
                                            'backup_path': bak_path, 'standard_path': sp})
            self._render_replacements()
            messagebox.showinfo(self._t('info_title'),
                                self._t('replace_success', custom=cm, standard=sm, backup=bak_name))
            self.status_var.set(self._t('replace_status'))
        except Exception as e:
            messagebox.showerror(self._t('error_title'), self._t('replace_failed', error=e))
            try:
                if os.path.isfile(bak_path): os.replace(bak_path, sp)
            except Exception: pass

    def _update_page_ui(self):
        self._page_lbl.set(f"{self._t('page')} {self.current_page}")
        self._btn_prev.config(state='disabled' if self.current_page <= 1 else 'normal')

    def _next_page(self):
        self.current_page += 1; self._update_page_ui(); self.load_bakkes_maps()

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1; self._update_page_ui(); self.load_bakkes_maps()

    def load_bakkes_maps(self, reset=False):
        if reset:
            self.current_page = 1
            self._update_page_ui()
        self._show_progress(self._t('loading_maps'))
        p, q = self.current_page, self.search_var.get().strip()
        def _fetch():
            try:
                maps = get_bakkes_maps(page=p, search_query=q)
                self.after(0, lambda: self._show_map_list(maps))
            except Exception as e:
                err = str(e)
                self.after(0, self._hide_progress)
                self.after(0, lambda msg=err: messagebox.showerror(
                    self._t('error_title'), self._t('error_load_maps', error=msg)))
        threading.Thread(target=_fetch, daemon=True).start()

    def _show_map_list(self, maps):
        self.bakkes_maps = maps
        for w in self._dl_frame.winfo_children(): w.destroy()
        self._hide_progress()
        if not maps:
            ttk.Label(self._dl_frame, text=self._t('no_maps_found')).pack(pady=10)
            self._btn_next.config(state='normal' if len(maps) >= 10 else 'disabled')
            return
        self._btn_next.config(state='normal' if len(maps) >= 10 else 'disabled')
        COLS = 4
        for i in range(COLS):
            self._dl_frame.columnconfigure(i, weight=1, pad=10)
        for idx, m in enumerate(maps):
            r, c = divmod(idx, COLS)
            tile = ttk.Frame(self._dl_frame, relief='raised', borderwidth=2)
            tile.grid(row=r, column=c, sticky='nsew', padx=8, pady=8)
            self._build_dl_tile(tile, m)

    def _build_dl_tile(self, tile, m):
        container = ttk.Frame(tile)
        container.pack(fill='both', expand=True)

        img_lbl = ttk.Label(container)
        img_lbl.pack(side='top', fill='x')

        info_frame = ttk.Frame(container)
        info_frame.pack(fill='both', expand=True, padx=10, pady=10)

        title_lbl = ttk.Label(info_frame, text=m['title'], font=('Arial', 10, 'bold', 'italic'), 
                              wraplength=220, justify='left')
        title_lbl.pack(side='top', anchor='w', fill='x')

        author_text = m.get('author', '')
        if author_text:
            ttk.Label(info_frame, text=author_text, foreground='gray', 
                      font=('Arial', 9)).pack(side='top', anchor='w', fill='x', pady=(2, 0))

        bot_frame = ttk.Frame(info_frame)
        bot_frame.pack(side='bottom', fill='x', expand=True, pady=(8, 0))

        rating_text = m.get('rating', '')
        if rating_text:
            ttk.Label(bot_frame, text=rating_text, foreground='#b8860b', 
                      font=('Arial', 9, 'bold')).pack(side='left', anchor='sw')

        folder     = self.custom_folder.get().strip()
        safe_title = sanitize_filename(m['title'])
        downloaded = folder and any(
            os.path.isfile(os.path.join(folder, safe_title + ext))
            for ext in CUSTOM_MAP_EXTENSIONS
        )
        
        btn_text = ('✓ Завантажено' if self.lang == 'uk' else '✓ Downloaded') if downloaded else self._t('download')
        btn_style = 'TButton' if downloaded else 'Accent.TButton'

        ttk.Button(bot_frame, text=btn_text, style=btn_style,
                   command=lambda mi=m: self._download_map(mi)).pack(side='right', anchor='se')

        # ── Асинхронне завантаження картинки ──
        async def async_fetch_img():
            url = m.get('preview_url')
            img_width, img_height = 288, 162  
            cache_key = f"{url}_{img_width}x{img_height}"
            
            # Якщо вже є в кеші — миттєво ставимо через Tkinter
            if url and cache_key in IMG_CACHE:
                self.after(0, lambda: img_lbl.config(image=IMG_CACHE[cache_key]))
                return

            pil_img = None
            if url:
                try:
                    # Асинхронний запит (не блокує інтерфейс!)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, timeout=5) as r:
                            if r.status == 200:
                                data = await r.read()
                                import io
                                # Обробка картинки (розмір)
                                pil_img = Image.open(io.BytesIO(data)).resize((img_width, img_height), Image.Resampling.BILINEAR)
                except Exception as e:
                    logging.warning(f"Не вдалося завантажити картинку {url}: {e}")

            # Функція, яка виконається в головному потоці Tkinter для оновлення UI
            def apply_image():
                try:
                    if pil_img:
                        photo = ImageTk.PhotoImage(pil_img)
                        IMG_CACHE[cache_key] = photo
                    else:
                        # Дефолтна заглушка, якщо картинки немає
                        img = Image.new('RGB', (img_width, img_height), '#333333' if self.theme_mode.get() == 'dark' else '#cccccc')
                        draw = ImageDraw.Draw(img)
                        draw.text((img_width//2, img_height//2), "No Image", fill="white", anchor="mm")
                        photo = ImageTk.PhotoImage(img)

                    # Захист від garbage collector
                    img_lbl.image = photo 
                    img_lbl.config(image=photo)
                except Exception:
                    pass

            # Відправляємо оновлення картинки назад у Tkinter
            self.after(0, apply_image)

        # Безпечно передаємо нашу асинхронну задачу у фоновий цикл подій
        asyncio.run_coroutine_threadsafe(async_fetch_img(), ASYNC_LOOP)


    def _download_map(self, m):
        folder = self.custom_folder.get().strip()
        if not folder:
            messagebox.showerror(self._t('error_title'), self._t('error_no_custom_folder')); return
        title = m.get('title', 'map').strip()
        self._show_progress(self._t('downloading_map', title=title))
        def _do():
            try:
                raw, fname = download_map_natively(m)
                is_zip = fname.lower().endswith('.zip') or raw[:2] == b'PK'
                final_filename = None
                
                if is_zip:
                    self.after(0, lambda: self.dl_status_var.set(self._t('extracting_zip')))
                    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tf:
                        tf.write(raw); tfp = tf.name
                    try:
                        name, _ = extract_map_from_zip(tfp, folder)
                        if not name:
                            self.after(0, self._hide_progress)
                            self.after(0, lambda: messagebox.showerror(
                                self._t('error_title'), self._t('no_map_in_zip'))); return
                        final_filename = name
                    finally:
                        os.unlink(tfp)
                else:
                    ext  = os.path.splitext(fname)[1].lower()
                    if ext not in CUSTOM_MAP_EXTENSIONS: ext = '.upk'
                    final_filename = sanitize_filename(title) + ext
                    dest = normalize_path(os.path.join(folder, final_filename))
                    with open(dest, 'wb') as fh: fh.write(raw)

                # ЗБЕРЕЖЕННЯ ІНФОРМАЦІЇ ПРО КАРТУ (ДЛЯ ПРЕВ'Ю В ЛОКАЛЬНИХ КАРТАХ)
                if final_filename:
                    self.map_info_db[final_filename] = {
                        'title': title,
                        'author': m.get('author', ''),
                        'preview_url': m.get('preview_url', '')
                    }
                    self.after(0, self._save_map_info) # Одразу зберігаємо на диск

                self.after(0, self._hide_progress)
                self.after(0, lambda: messagebox.showinfo(
                    self._t('info_title'), self._t('download_complete', title=title)))
                self.after(0, self._refresh_custom)
            except Exception as e:
                err = str(e)
                self.after(0, self._hide_progress)
                self.after(0, lambda msg=err: messagebox.showerror(
                    self._t('error_title'), self._t('error_download_failed', error=msg)))
        threading.Thread(target=_do, daemon=True).start()

    # ════════════════════════════════════════════════════════════════
    # AUTO-UPDATE SYSTEM
    # ════════════════════════════════════════════════════════════════

    def check_for_updates(self):
        if not self.auto_update_var.get():
            return

        def _task():
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            try:
                req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
            except HTTPError as e:
                logging.error(f"Сервер відхилив запит перевірки оновлень. Код: {e.code}")
            except URLError as e:
                logging.error(f"Помилка мережі при перевірці оновлень: {e.reason}")
            except json.JSONDecodeError:
                logging.error("API GitHub повернуло невалідний JSON.")
            except Exception as e:
                logging.error(f"Непередбачена помилка в check_for_updates: {e}", exc_info=True)

        threading.Thread(target=_task, daemon=True).start()

    def manual_check_for_updates(self):
        self._show_progress(self._t('check_update') + "...")
        
        def _task():
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            try:
                req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                latest_tag = data.get('tag_name', '').lstrip('v').strip()
                current_tag = VERSION.lstrip('v').strip() 

                self.after(0, self._hide_progress)

                if not latest_tag:
                    self.after(0, lambda: messagebox.showinfo(self._t('info_title'), "Релізів на GitHub ще немає."))
                    return

                def parse_v(v): 
                    return tuple(int(x) for x in v.split(".") if x.isdigit())

                parsed_latest = parse_v(latest_tag)
                parsed_current = parse_v(current_tag)

                if parsed_latest and parsed_current and parsed_latest > parsed_current:
                    self.after(0, lambda: self._prompt_update(latest_tag, data))
                else:
                    self.after(0, lambda: messagebox.showinfo(self._t('info_title'), self._t('no_updates')))
            except Exception as e:
                self.after(0, self._hide_progress)
                self.after(0, lambda err=e: messagebox.showerror(self._t('error_title'), f"Помилка підключення до GitHub:\n{err}"))

        threading.Thread(target=_task, daemon=True).start()

    
    def _prompt_update(self, latest_tag, release_data):
        if messagebox.askyesno(self._t('info_title'), f"Знайдено нову версію програми: {latest_tag}.\nОновити зараз?"):
            self._download_and_apply_update(release_data)

    def _download_and_apply_update(self, release_data):
        assets = release_data.get('assets', [])
        download_url = next((a['browser_download_url'] for a in assets if a['name'].endswith('.exe')), None)

        if not download_url:
            messagebox.showerror(self._t('error_title'), "Не знайдено .exe файлу в релізі GitHub.")
            return

        self._show_progress("Завантаження оновлення...")

        def _do_update():
            exe_path = sys.executable
            new_exe_path = exe_path + '.new'
            old_exe_path = exe_path + '.old'
            
            try:
                if getattr(sys, 'frozen', False):
                    req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=60) as response, open(new_exe_path, 'wb') as out_file:
                        shutil.copyfileobj(response, out_file)

                    self.after(0, self._hide_progress)
                    self.after(0, lambda: messagebox.showinfo(self._t('info_title'), "Оновлення завантажено! Програма зараз перезапуститься."))

                    import tempfile
                    bat_path = os.path.join(tempfile.gettempdir(), "rl_updater.bat")
                    with open(bat_path, "w", encoding="utf-8") as f:
                        f.write('@echo off\n')
                        f.write('chcp 65001 > nul\n')
                        f.write('ping 127.0.0.1 -n 3 > nul\n')
                        f.write(f'if exist "{old_exe_path}" del "{old_exe_path}" > nul 2>&1\n')
                        f.write(f'rename "{exe_path}" "{os.path.basename(old_exe_path)}"\n')
                        f.write(f'rename "{new_exe_path}" "{os.path.basename(exe_path)}"\n')
                        f.write(f'start "" "{exe_path}"\n')
                        f.write('del "%~f0"\n')

                    clean_env = {}
                    for k, v in os.environ.items():
                        k_up = k.upper()
                        if 'MEI' not in k_up and 'TCL_' not in k_up and 'TK_' not in k_up and '_PYI' not in k_up:
                            clean_env[k] = v

                    subprocess.Popen(['cmd.exe', '/c', bat_path], env=clean_env, creationflags=0x08000000)

                    self.after(0, self.destroy)
                else:
                    self.after(0, self._hide_progress)
                    self.after(0, lambda: messagebox.showinfo(self._t('info_title'), "Оновлення працює тільки для скомпільованого .exe файлу."))
            
            except Exception as e:
                self.after(0, self._hide_progress)
                self.after(0, lambda err=e: messagebox.showerror(self._t('error_title'), f"Не вдалося оновити: {err}"))
                if os.path.exists(new_exe_path):
                    try: os.remove(new_exe_path)
                    except: pass

        threading.Thread(target=_do_update, daemon=True).start()

if __name__ == '__main__':
    setup_logger()
    app = MapLoaderApp()
    app.mainloop()