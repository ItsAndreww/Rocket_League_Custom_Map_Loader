# Rocket League Custom Map Loader
<p align="center">
  <img src="logo.png" alt="Logo" width="200">
</p>
<h1 align="center">RLCML</h1>

<p align="center">
  <a href="README_UA.md">Українська інструкція </a> | 
  <a href="https://donatello.to/itsandrewini">Support me</a>
</p>

A high-performance, GUI-based utility for managing custom maps in Rocket League. This application automates the process of replacing standard game maps with custom ones while maintaining automatic backups, downloading new maps directly from BakkesMod, and launching the game directly.

## Usage

### Standalone Executable (.exe)

If you do not have Python installed, you can download the latest standalone version from the **[Releases](https://github.com/ItsAndreww/Rocket_League_Custom_Map_Loader/releases)** section. No additional dependencies are required for the compiled version.

## Usage Example

### Replacing a Local Map

![Local Maps](Screenshots/Localmaps.png)

1. Open the **Local Maps** tab.  
2. Specify your **Custom maps folder** where you store downloaded map files.  
3. Click **Auto detect** to let the application find your Rocket League installation path.  
4. In the **Custom Maps** list, click on your desired map (e.g., `Dribble_Challenge.upk`). The button will turn blue to indicate selection.  
5. In the **Standard Maps** list, click on a target map to be replaced (e.g., `labs_underpass_p`). The button will turn orange.  
6. Click **Replace Map**. The application swaps the files and creates a backup of the original map automatically.  
7. Click **Launch Game** to start Rocket League with the new map installed, and start a freeplay match on the map you replaced.

### Downloading and Installing a New Map

![Online Maps Downloading](Screenshots/Onlinemaps.png)

1. Navigate to the **Download Maps** tab.  
2. Enter a search term (e.g., "Rings") in the search bar and click **Search**.  
3. Find the map you want in the results and click **Download**.  
4. The application will instantly fetch the map via API or gracefully bypass Cloudflare if needed.  
5. If the map is in a **ZIP archive**, the application **automatically extracts** the correct map file to your designated custom maps folder.  
6. Return to the **Local Maps** tab and click Refresh Lists to see your new map.

## Core Features

* **Lightning-Fast Search & Previews:** Asynchronous image loading and API-first map fetching for a buttery-smooth interface.
* **Map Replacement:** Swap standard Rocket League maps with custom files while maintaining automatic backups for easy restoration.
* **Integrated Downloader:** Search and download maps directly from BakkesMod with integrated preview images.
* **Automated Workflow:** Automatic ZIP extraction for downloaded archives and intelligent detection of the Rocket League installation path.
* **Game Integration:** Launch Rocket League directly from the interface (Custom command-line arguments support is currently planned/WIP).
* **Modern UI:** Native Windows 11 styling support (Mica effect), dark/light mode toggle, and system tray minimization.
* **Auto-Updater:** Built-in update checker and installer to keep you on the latest version seamlessly.

## Technical Implementation

* **Hybrid Scraping Engine:** Attempts blazing-fast direct HTTP/API requests first, falling back to a Singleton Selenium WebDriver to handle Cloudflare protections only when necessary.
* **Asynchronous Architecture:** Utilizes `asyncio` and `aiohttp` to manage concurrent network requests and background tasks without blocking the Tkinter `mainloop`.
* **Optimized I/O:** Implements in-memory caching for metadata (`map_info.json`) to drastically reduce disk read/write operations.
* **Comprehensive Logging:** Utilizes Python's native `logging` module with a `RotatingFileHandler` to generate `rlcml.log` for reliable debugging in production (`--noconsole`) environments.
* **CI/CD Pipeline:** Fully automated build and release process via GitHub Actions.

## Build Instructions

### Automated Build (GitHub Actions)
The project is configured with a GitHub Actions workflow. Creating a new tag (e.g., `v1.2.0`) and pushing it to the repository will automatically trigger a clean build and publish the `.exe` to the Releases tab.

### Manual Build
To create a standalone one-file executable manually with all necessary drivers and certificates, use the following command:
```bash
python -m PyInstaller --noconsole --onefile --icon=logo.png --add-data "logo.png;." --collect-all selenium --collect-data certifi map_loader.py
```

### Running from Source

To run the script directly, ensure you have **Python 3.9+** and a Chromium-based browser (Microsoft Edge or Google Chrome) installed.

**1.Install required dependencies:** 
```bash
pip install beautifulsoup4 pillow selenium webdriver-manager pystray sv_ttk pywinstyles aiohttp
```

**2.Execute the script:**
python map_loader.py

## Troubleshooting

**Driver Initialization:** If the application fails to launch the browser, verify your internet connection. The application will attempt to use local drivers before downloading the latest versions via webdriver-manager.  

**Map Visibility:** Standard maps available for replacement are currently limited to specific Labs maps (e.g., Underpass, Basin) to ensure game stability. 

**Debugging:** If you experience crashes, check the rlcml.log file generated in the same directory as the executable.

**Permissions:** Ensure the application has the necessary permissions to write to the Rocket League installation directory for map replacement.

## License

This project is provided for personal and educational use. Rocket League is a trademark of Psyonix.
Made by **ItsAndreww.**
**Contact Me:** andriy.novo05@gmail.com