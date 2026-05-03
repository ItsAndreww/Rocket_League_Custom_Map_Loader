# Rocket League Custom Map Loader
<p align="center">
  <img src="logo.png" alt="Logo" width="200">
</p>
<h1 align="center">RLCML</h1>

<p align="center">
  <a href="README_UA.md">Українська версія</a>
  <a href="https://donatello.to/itsandrewini">Support me</a>
</p>

A GUI-based utility for managing custom maps in Rocket League. This application automates the process of replacing standard game maps with custom ones while maintaining automatic backups, downloading new maps directly from BakkesMod, and launching the game directly.

## Usage

### Standalone Executable

If you do not have Python installed, you can download the latest standalone version from the **[Releases](https://github.com/ItsAndreww/Rocket_League_Custom_Map_Loader/releases)** section. No additional dependencies are required for the compiled version.

## Usage Example

### Replacing a Local Map

![Local Maps](Screenshots/Localmaps.png)

1. Open the **Local Maps** tab.  

2. Specify your **Custom maps folder** where you store downloaded map files.  

3. Click **Auto detect** to let the application find your Rocket League installation path.  

4. In the **Custom Maps** list, click on your desired map (e.g., Dribble_Challenge.upk). The button will turn blue to indicate selection.  

5. In the **Standard Maps** list, click on a target map to be replaced (e.g., labs_underpass_p). The button will turn orange.  

6. Click **Replace Map**. The application swaps the files and creates a backup of the original map automatically.  

7. Click **Launch Game** to start Rocket League with the new map installed, and start a freeplay map you replaced (e.g. Dribble_Challenge.upk -> Labs_Underpass_P.upk or in game Labs Underpass).

### Downloading and Installing a New Map

![Online Maps Downloading](Screenshots/Onlinemaps.png)

1. Navigate to the **Download Maps** tab.  

2. Enter a search term (e.g., "Rings") in the search bar and click **Search**.  

3. Find the map you want in the results and click **Download**.  

4. The application opens a background browser, bypasses Cloudflare, and downloads the file.  

5. If the map is in a **ZIP archive**, the application **automatically extracts** the correct map file to your designated custom maps folder.  

6. Return to the **Local Maps** tab and click Refresh Lists to see your new map.

## Core Features

**Map Replacement:** Swap standard Rocket League maps with custom files while maintaining automatic backups for easy restoration.

**Integrated Downloader:** Search and download maps directly from BakkesMod with integrated preview images.

**Automated Workflow:** Automatic ZIP extraction for downloaded archives and intelligent detection of the Rocket League installation path.

**Game Integration:** Launch Rocket League directly from the interface, with custom command-line arguments(this is broken, maybe i`ll add it when i figure it out).

**Modern UI:** Native Windows 11 styling support (Mica effect), dark/light mode toggle, and system tray minimization.

## Technical Implementation

**Cloudflare Bypass:** Utilizes Selenium to navigate BakkesPlugins.com and handle download triggers.

**Persistence:** User configurations, including language preferences and folder paths, are saved locally in config.json.

**Concurrency:** Implements threading to prevent UI freezes during network requests and file extraction.

**PyInstaller Optimization:** Includes a global patch for subprocess.Popen to ensure background browser processes do not trigger console windows when compiled with the --noconsole flag.

**Supported Formats:** Processes .upk, .udk, .pak, .udatasmith, and .rli files.

## Build Instructions

To create a standalone one-file executable with all necessary drivers and certificates, use the following command:
```bash
python -m PyInstaller --noconsole --onefile --icon=logo.png --add-data "logo.png;." --collect-all selenium --collect-data certifi map_loader.py
```

### Running from Source

To run the script directly, ensure you have **Python 3.9+** and a Chromium-based browser (Microsoft Edge or Google Chrome) installed.

**1.Install required dependencies:** 
```bash
pip install beautifulsoup4 pillow selenium webdriver-manager pystray sv_ttk pywinstyles
```

**2.Execute the script:**
python map_loader.py

## Troubleshooting

**Driver Initialization:** If the application fails to launch the browser, verify your internet connection. The application will attempt to use local drivers before downloading the latest versions via webdriver-manager.  

**Map Visibility:** Standard maps available for replacement are currently limited to specific Labs maps (e.g., Underpass, Basin) to ensure game stability.  

**Permissions:** Ensure the application has the necessary permissions to write to the Rocket League installation directory for map replacement.

## License

This project is provided for personal and educational use. Rocket League is a trademark of Psyonix.
Made by ItsAndreww.
Contact Me: andriy.novo05@gmail.com
