# 🗑️ Windows Cleanup Tool

A simple, user-friendly application to clean unnecessary files, folders, and registry entries from Windows.

---

## ⚡ QUICK START (5 Minutes)

### What You Need
- Windows 10 or Windows 11
- Python 3.10+ (download from https://www.python.org/)
  - ✅ Check "Add Python to PATH" during installation

### Step 1: Setup (First Time Only)
1. Right-click `setup.bat`
2. Select **"Run as administrator"**
3. Choose **option 1**: "Install dependencies"
4. Wait for completion

### Step 2: Run the App
1. Run `setup.bat` again (as administrator)
2. Choose **option 2**: "Run the cleanup app"
3. Click **"Scan System"** button
4. Wait for scan to complete (~10-30 seconds)

### Step 3: Review & Clean
1. Check each tab to see what will be cleaned
2. Items are **checked by default** (will be deleted)
3. **Uncheck** any items you want to keep
4. Click **"Clean Now"**
5. Confirm when asked
6. Watch the progress bar
7. Done! ✨

### Create Standalone .exe (Optional)
Want to share the app or run without Python?
1. Run `setup.bat` again
2. Choose **option 3**: "Build standalone .exe"
3. New file: `dist\cleanup_app.exe`
4. Now you can run it anywhere without Python!

---

## 📋 Features

- **Scan System** - Find unnecessary files in multiple locations:
  - Temporary files
  - Browser cache (Chrome, Edge, Firefox)
  - Recycle bin
  - Log files
  - Old downloads (6+ months)
  - Startup applications
  - Windows Update cache

- **Clean Files** - Safely delete found items with confirmation

- **User-Friendly UI** - Simple dark theme interface with tabs

- **No Installation** - Single .exe file option available

- **Fully Commented Code** - Every line explained for easy understanding

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
