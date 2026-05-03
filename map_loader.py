VERSION = "1.0.1"  # Поточна версія
GITHUB_REPO = "ItsAndreww/Rocket_League_Custom_Map_Loader" # Наприклад: ItsAndreww/RL-Map-Loader

import os
import sys


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

import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import urllib.request
import urllib.parse
import shlex
from bs4 import BeautifulSoup
import threading
import io
import zipfile
import tempfile
import time
import string
import logging

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
        1. Перше налаштування:
        • Створіть або оберіть папку на комп'ютері, де будуть зберігатись ваші кастомні карти (наприклад, "C:\\RL_Maps").
        • Натисніть "Автодетект" або вручну вкажіть шлях до папки з грою Rocket League (там, де лежить RocketLeague.exe).

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
        • Або просто закрийте програму (якщо на верхній панелі обрано "Відновити і вийти"), і вона автоматично поверне всі карти на місце!
        ''',
    },
    'en': {
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
        1. Initial Setup:
        • Choose or create a folder on your PC to store custom maps (e.g., "C:\\RL_Maps").
        • Click "Auto detect" or manually browse to your Rocket League installation folder.

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
        • Or simply close the app (if "Restore and exit" is selected at the top), and it will restore everything automatically!
        ''',
    }
}


def tr(key, **kwargs):
    return LANGUAGES.get(CURRENT_LANGUAGE, LANGUAGES['en']).get(key, key).format(**kwargs)


# ════════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════════

def load_config():
    path = os.path.join(_data_dir(), 'config.json')
    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
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
    BASE = 'https://bakkesplugins.com'
    driver = None
    try:
        driver = _get_driver()
        url = f"{BASE}/maps"
        params = []
        if search_query:
            params.append(f"search={urllib.parse.quote(search_query)}")
        if page > 1:
            params.append(f"page={page}")
        if params:
            url += "?" + "&".join(params)
        driver.get(url)
        _wait_cf(driver)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/maps/']"))
            )
        except Exception:
            pass
        html = driver.page_source
    except Exception as e:
        raise RuntimeError(str(e)) from e
    finally:
        if driver:
            try: driver.quit()
            except Exception: pass
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
        maps.append({
            'title':       title,
            'map_id':      mid,
            'page_url':    BASE + href,
            'preview_url': preview,
            'rating':      rating.strip() if rating else '',
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
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
        img = Image.open(io.BytesIO(data)).resize((160, 90), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def find_rocket_league_root():
    pf   = os.environ.get('PROGRAMFILES',      r'C:\Program Files')
    pf86 = os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)')
    common = [
        os.path.join(pf86, 'Steam', 'steamapps', 'common', 'rocketleague'),
        os.path.join(pf,   'Steam', 'steamapps', 'common', 'rocketleague'),
        os.path.join(pf,   'Epic Games', 'rocketleague'),
        os.path.join(pf86, 'Epic Games', 'rocketleague'),
    ]
    def _valid(p):
        return os.path.isdir(p) and (
            os.path.isdir(os.path.join(p, 'TAGame')) or
            os.path.isdir(os.path.join(p, 'Binaries'))
        )
    for p in common:
        if _valid(p): return p
    drives = [f'{d}:' for d in string.ascii_uppercase if os.path.exists(f'{d}:')]
    suffixes = [
        r'SteamLibrary\steamapps\common\rocketleague',
        r'Steam\steamapps\common\rocketleague',
        r'Epic Games\rocketleague',
        r'Games\rocketleague',
    ]
    for drv in drives:
        for sfx in suffixes:
            p = os.path.join(drv + '\\', sfx)
            if _valid(p): return p
    return None


def find_maps_folder(rl_root: str):
    if not rl_root: return None
    for sfx in CUSTOM_MAP_FOLDER_NAMES:
        p = os.path.join(rl_root, sfx)
        if os.path.isdir(p): return p
    return None


def find_rocket_league_executable(rl_root: str):
    if not rl_root: return None
    for rel in ('Binaries\\Win64\\RocketLeague.exe',
                'Binaries\\Win64\\RocketLeague-Win64-Shipping.exe',
                'RocketLeague.exe'):
        p = os.path.join(rl_root, rel)
        if os.path.isfile(p): return p
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
        self.auto_update_var = tk.BooleanVar(value=self._cfg.get('auto_update', True))

        self.custom_folder = tk.StringVar(value=self._cfg.get('custom_maps_folder', ''))
        self.rl_root_var   = tk.StringVar(value=self._cfg.get('rl_root', ''))
        self.maps_folder   = tk.StringVar(value=self._cfg.get('maps_folder', ''))
        self.sel_custom    = tk.StringVar()
        self.sel_standard  = tk.StringVar()
        self.status_var    = tk.StringVar(value=tr('status_default'))
        self.dl_status_var = tk.StringVar()
        self.replacements  = []
        self.bakkes_maps   = []
        self.current_page  = 1
        self.search_var    = tk.StringVar()

        if HAS_SV_TTK:
            sv_ttk.set_theme(self.theme_mode.get())

        self._build_ui()
        self._apply_win_style()
        self.protocol('WM_DELETE_WINDOW', self._on_close)
        self.auto_detect_rl()
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

        # ── НОВЕ: Вкладка "Інструкція" ──
        hf = ttk.Frame(self.notebook)
        self.notebook.add(hf, text=self._t('help_tab'))
        self._build_help_tab(hf)

    def _build_topbar(self):
        bar = ttk.Frame(self, padding=6)
        bar.pack(fill='x')

        logo_path = resource_path('logo.png')
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

        ttk.Label(bar, text=self._t('language')).pack(side='left')
        lang_cb = ttk.Combobox(bar, values=list(LANGUAGE_NAMES.values()),
                               textvariable=self.language_opt, state='readonly', width=12)
        lang_cb.pack(side='left', padx=4)
        lang_cb.bind('<<ComboboxSelected>>', self._on_lang_change)

        if HAS_SV_TTK:
            icon = '☀️' if self.theme_mode.get() == 'dark' else '🌙'
            self._theme_btn = ttk.Button(bar, text=icon, width=3, command=self._toggle_theme)
            self._theme_btn.pack(side='left', padx=(5, 20))

        ttk.Label(bar, text=self._t('close_behavior')).pack(side='left', padx=(0, 4))
        self._close_lbl = tk.StringVar(value=self._t(self.close_code.get()))
        close_cb = ttk.Combobox(bar, values=[self._t('restore_and_exit'), self._t('minimize_to_tray')],
                                textvariable=self._close_lbl, state='readonly', width=20)
        close_cb.pack(side='left', padx=4)
        close_cb.bind('<<ComboboxSelected>>', self._on_close_action_change)

        # ── НОВЕ: Галочка автооновлення на верхній панелі ──
        auto_update_text = "Автооновлення" if self.lang == 'uk' else "Auto-update"
        ttk.Checkbutton(
            bar, 
            text=auto_update_text, 
            variable=self.auto_update_var, 
            command=self._save_cfg
        ).pack(side='left', padx=(15, 4))

        # Кнопка запуску гри (праворуч)
        ttk.Button(bar, text=self._t('launch_game'),
                   command=self._launch_rl).pack(side='right', padx=4)

    def _build_bottom_logo(self):
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side='bottom', fill='x', padx=15, pady=(0, 5))
        
        logo_path = resource_path('logo.png')
        if os.path.isfile(logo_path):
            try:
                img = Image.open(logo_path)
                tiny = img.resize((20, 20), Image.Resampling.LANCZOS)
                self._bottom_logo_img = ImageTk.PhotoImage(tiny)
                ttk.Label(bottom_frame, image=self._bottom_logo_img).pack(side='left', padx=(0, 5))
            except Exception:
                pass
        
        ttk.Label(bottom_frame, text="made by ItsAndreww", font=('Arial', 8, 'italic'), foreground='gray').pack(side='left')

        # Залишаємо тільки версію справа
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
        def row(label_key, var, browse_cmd, extra_btn=None):
            r = ttk.Frame(f); r.pack(fill='x', pady=2)
            ttk.Label(r, text=self._t(label_key), width=25).pack(side='left')
            e = ttk.Entry(r, textvariable=var, width=50); e.pack(side='left', padx=8)
            ttk.Button(r, text=self._t('browse'), command=browse_cmd).pack(side='left')
            if extra_btn:
                ttk.Button(r, **extra_btn).pack(side='left', padx=4)
        row('custom_maps_folder', self.custom_folder, self._browse_custom)
        row('rl_root',            self.rl_root_var,   self._browse_rl,
            extra_btn={'text': self._t('auto_detect'), 'command': self.auto_detect_rl})
        row('maps_folder',        self.maps_folder,   self._update_maps_folder,
            extra_btn={'text': self._t('refresh'), 'command': self._update_maps_folder})
        cols = ttk.Frame(f); cols.pack(fill='both', expand=True, pady=8)
        def col(title_key):
            lf = ttk.LabelFrame(cols, text=self._t(title_key))
            lf.pack(side='left', fill='both', expand=True, padx=4)
            return self._make_scrollable(lf)
        _, self._custom_frame      = col('custom_maps')
        _, self._replace_frame     = col('replacement_history')
        _, self._standard_frame    = col('standard_maps')
        btns = ttk.Frame(f); btns.pack(fill='x', pady=8)
        rb = ttk.Button(btns, text=self._t('refresh_lists'), command=self._refresh_all)
        rb.pack(side='left', padx=10)
        rpb = ttk.Button(btns, text=self._t('replace_map'), command=self._do_replace, style='Accent.TButton')
        rpb.pack(side='right', padx=10)
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
        
        # Створюємо текстове поле, яке підтримує скролінг та форматування
        txt = tk.Text(f, wrap='word', font=('Arial', 11), relief='flat', padx=10, pady=10)
        txt.pack(side='left', fill='both', expand=True)
        
        # Додаємо скролбар
        sb = ttk.Scrollbar(f, orient='vertical', command=txt.yview)
        sb.pack(side='right', fill='y')
        txt.configure(yscrollcommand=sb.set)
        
        # Вставляємо текст інструкції
        txt.insert('1.0', self._t('help_text'))
        
        # Робимо текст доступним лише для читання
        txt.configure(state='disabled')
        
        # Налаштовуємо кольори залежно від теми (темна/світла)
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
        self._theme_btn.config(text='☀️' if new == 'dark' else '🌙')
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
        logo_path = resource_path('logo.png')
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

    def _refresh_all(self):
        self._refresh_custom(); self._refresh_standard(); self._render_replacements()

    def _refresh_custom(self):
        for w in self._custom_frame.winfo_children(): w.destroy()
        for m in list_custom_maps(self.custom_folder.get()):
            self._custom_tile(self._custom_frame, m)

    def _refresh_standard(self):
        for w in self._standard_frame.winfo_children(): w.destroy()
        for m in list_standard_maps(self.maps_folder.get()):
            self._std_tile(self._standard_frame, m)

    def _custom_tile(self, parent, name):
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=1, padx=2)
        btn_style = 'Accent.TButton' if self.sel_custom.get() == name else 'TButton'
        btn = ttk.Button(row, text=name, width=28, style=btn_style,
                         command=lambda n=name: self._select_map(n, True))
        btn.pack(side='left', fill='x', expand=True, padx=(0, 2))
        del_btn = ttk.Button(row, text='✕', width=3, command=lambda: self._delete_custom(name))
        del_btn.pack(side='right')

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
        img_lbl = ttk.Label(tile)
        img_lbl.pack(side='top', padx=5, pady=5)
        info = ttk.Frame(tile); info.pack(side='top', fill='both', expand=True, padx=5, pady=5)
        ttk.Label(info, text=m['title'], font=('Arial', 10, 'bold'),
                  wraplength=220, justify='center').pack(anchor='center', pady=(0, 4))
        if m.get('rating'):
            ttk.Label(info, text=m['rating'], foreground='#b8860b',
                      font=('Arial', 9, 'bold')).pack(anchor='center', pady=(0, 4))
        folder     = self.custom_folder.get().strip()
        safe_title = sanitize_filename(m['title'])
        downloaded = folder and any(
            os.path.isfile(os.path.join(folder, safe_title + ext))
            for ext in CUSTOM_MAP_EXTENSIONS
        )
        btn_text = ('✓ Завантажено' if CURRENT_LANGUAGE == 'uk' else '✓ Downloaded') \
                   if downloaded else self._t('download')
        ttk.Button(info, text=btn_text,
                   command=lambda mi=m: self._download_map(mi)).pack(anchor='center', side='bottom', pady=4)
        def _fetch_img():
            photo = download_image(m.get('preview_url'))
            if photo:
                self.after(0, lambda: (setattr(img_lbl, 'image', photo),
                                       img_lbl.config(image=photo)))
        threading.Thread(target=_fetch_img, daemon=True).start()

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
                    finally:
                        os.unlink(tfp)
                else:
                    ext  = os.path.splitext(fname)[1].lower()
                    if ext not in CUSTOM_MAP_EXTENSIONS: ext = '.upk'
                    dest = normalize_path(os.path.join(folder, sanitize_filename(title) + ext))
                    with open(dest, 'wb') as fh: fh.write(raw)
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
        """Перевіряє наявність оновлень на GitHub у фоновому потоці."""
        # ДОДАНО: Якщо галочка автооновлення знята - не перевіряємо
        if not self.auto_update_var.get():
            return

        def _task():
            # Використовуємо вашу константу GITHUB_REPO
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            try:
                req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                latest_tag = data.get('tag_name', '').lstrip('v').strip()
                current_tag = VERSION.lstrip('v').strip() 

                if not latest_tag:
                    return

                def parse_v(v): 
                    return tuple(int(x) for x in v.split(".") if x.isdigit())

                parsed_latest = parse_v(latest_tag)
                parsed_current = parse_v(current_tag)

                if parsed_latest and parsed_current and parsed_latest > parsed_current:
                    self.after(0, lambda: self._prompt_update(latest_tag, data))
            except Exception as e:
                print(f"Помилка перевірки оновлень: {e}")

        threading.Thread(target=_task, daemon=True).start()
    
    def _prompt_update(self, latest_tag, release_data):
        if messagebox.askyesno(self._t('info_title'), f"Знайдено нову версію програми: {latest_tag}.\nОновити зараз?"):
            self._download_and_apply_update(release_data)

    def _download_and_apply_update(self, release_data):
        assets = release_data.get('assets', [])
        # Шукаємо перший-ліпший .exe файл у релізі
        download_url = next((a['browser_download_url'] for a in assets if a['name'].endswith('.exe')), None)

        if not download_url:
            messagebox.showerror(self._t('error_title'), "Не знайдено .exe файлу в релізі GitHub.")
            return

        self._show_progress("Завантаження оновлення...")

        def _do_update():
            exe_path = sys.executable
            old_exe_path = exe_path + '.old'
            
            try:
                # Якщо програма запущена як .exe
                if getattr(sys, 'frozen', False):
                    # 1. Перейменовуємо поточний ексешнік
                    if os.path.exists(old_exe_path):
                        os.remove(old_exe_path)
                    os.rename(exe_path, old_exe_path)

                    # 2. Завантажуємо новий
                    req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=60) as response, open(exe_path, 'wb') as out_file:
                        shutil.copyfileobj(response, out_file)

                    self.after(0, self._hide_progress)
                    self.after(0, lambda: messagebox.showinfo(self._t('info_title'), "Оновлення завантажено! Програма зараз перезапуститься."))

                    # 3. Перезапускаємо новий ексешнік і вбиваємо поточний процес
                    subprocess.Popen([exe_path], close_fds=True)
                    
                    # М'яко закриваємо поточну програму, щоб PyInstaller встиг видалити сміття
                    self.after(0, self.destroy)
                    return
                else:
                    self.after(0, self._hide_progress)
                    self.after(0, lambda: messagebox.showinfo(self._t('info_title'), "Оновлення працює тільки для скомпільованого .exe файлу."))
            
            except Exception as e:
                self.after(0, self._hide_progress)
                self.after(0, lambda err=e: messagebox.showerror(self._t('error_title'), f"Не вдалося оновити: {err}"))
                
                # Відновлюємо оригінальну назву, якщо щось зламалося під час скачування
                if os.path.exists(old_exe_path) and not os.path.exists(exe_path):
                    os.rename(old_exe_path, exe_path)

        threading.Thread(target=_do_update, daemon=True).start()

if __name__ == '__main__':
    app = MapLoaderApp()
    app.mainloop()