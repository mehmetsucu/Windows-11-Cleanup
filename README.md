# 🗑️ Windows Cleanup Tool

A simple, user-friendly application to clean unnecessary files, folders, and registry entries from Windows.

## Features

- **Scan System** - Find unnecessary files in multiple locations:
  - Temporary files
  - Browser cache (Chrome, Edge, Firefox)
  - Recycle bin
  - Log files
  - Old downloads (6+ months)
  - Startup applications
  - Windows Update cache

- **Clean Files** - Safely delete found items with confirmation

- **User-Friendly UI** - Simple dark theme interface

- **No Installation** - Single .exe file, ready to run

## Setup Instructions

### Step 1: Install Python (if not already installed)
Download Python 3.10 or later from https://www.python.org/
Make sure to check "Add Python to PATH" during installation

### Step 2: Install Dependencies
Open Command Prompt (cmd) and run:

```bash
pip install -r requirements.txt
```

This installs:
- PyQt5 (GUI framework)
- psutil (system information)
- pyinstaller (for creating .exe)

### Step 3: Run the Application

#### Option A: Run Python file directly
```bash
python cleanup_app.py
```

#### Option B: Run as Administrator (recommended for system cleanup)
```bash
python -m cleanup_app
```
or right-click cleanup_app.py → "Run as administrator"

## Building Standalone .EXE File

### Step 1: Create the .exe
Open Command Prompt in the project folder and run:

```bash
pyinstaller --onefile --windowed --icon=cleanup.ico cleanup_app.py
```

Parameters explained:
- `--onefile` = Creates single .exe file (not a folder)
- `--windowed` = No console window (clean GUI only)
- `--icon=cleanup.ico` = Use custom icon (optional)

### Step 2: Find Your .exe
The .exe file will be created in: `dist/cleanup_app.exe`

### Step 3: Run the .exe
Double-click `cleanup_app.exe` to run

The .exe is now standalone and needs NO Python installed to run!

## How to Use

1. **Click "Scan System"**
   - The app will scan all cleanup locations
   - Takes 10-30 seconds depending on system size

2. **Review Results**
   - Check each tab to see what will be cleaned
   - Uncheck items you don't want to delete

3. **Click "Clean Now"**
   - Confirm the cleanup
   - App will delete selected items
   - Shows progress during cleanup

4. **Done!**
   - Restart your computer for best results
   - Check Settings to run again anytime

## Important Notes

⚠️ **ALWAYS RUN AS ADMINISTRATOR**
- Right-click the .exe or .py file
- Select "Run as administrator"
- This allows access to all system areas

⚠️ **BACKUP IMPORTANT FILES**
- The app deletes files permanently
- While it targets unnecessary files, be cautious
- Recycle bin items are included in cleanup

## What Gets Cleaned

| Category | Location | Notes |
|----------|----------|-------|
| Temp Files | %TEMP%, Windows\Temp | Safe to delete |
| Browser Cache | Chrome, Edge, Firefox | Will log you out |
| Recycle Bin | $Recycle.Bin | Permanent deletion |
| Log Files | Windows\Logs | Old logs only |
| Old Downloads | Downloads folder | 6+ months old |
| Startup Apps | Registry | Disabled from startup |
| Windows Updates | SoftwareDistribution | Old update cache |

## Troubleshooting

**Error: "Permission Denied"**
- Run as Administrator
- Try cleaning one category at a time

**Error: "File is in use"**
- Close all programs and try again
- Restart computer and try again

**Nothing happens after clicking Scan**
- Check System Tray for the window
- It might have opened in background

## System Requirements

- Windows 10 or Windows 11
- 100 MB free disk space (for the app)
- Administrator access

## Disclaimer

This tool deletes files permanently. While it's designed to target unnecessary files, use it carefully. The author is not responsible for deleted files. Always backup important data before running cleanup tools.

## Development

All code is written in Python with detailed comments for easy understanding and modification.

To modify the app:
1. Edit `cleanup_app.py`
2. Run `python cleanup_app.py` to test
3. Build new .exe with pyinstaller

## License

Free to use and modify for personal use.

---

**Questions or issues?** Check the code comments in `cleanup_app.py` for detailed explanations of how everything works.
