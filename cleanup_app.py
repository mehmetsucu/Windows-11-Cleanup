"""
Windows Cleanup Tool - Main Application
A simple, user-friendly tool to clean unnecessary files, folders, and registry entries
Author: Cleanup Tool
Version: 1.0
"""

# ============================================================================
# IMPORTS - Load all required libraries
# ============================================================================
import sys  # System-specific parameters and functions
import os  # Operating system interactions (file operations)
import shutil  # High-level file operations
import subprocess  # Run external commands (like PowerShell)
import threading  # Multi-threading for non-blocking UI
import tempfile  # Handle temporary files
import psutil  # Get process and system information
import winreg  # Windows registry access
from pathlib import Path  # Object-oriented file paths
from datetime import datetime, timedelta  # Date and time operations
import json  # Handle JSON data (for settings)
from typing import List, Tuple  # Type hints for cleaner code

# PyQt5 - UI Framework for creating windows and buttons
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QListWidget, QListWidgetItem,
    QCheckBox, QMessageBox, QTabWidget, QScrollArea, QGroupBox,
    QSpinBox, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer  # Threading and signals
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap  # Font, color, icons
from PyQt5.QtCore import QSize  # Size objects for UI elements

# ============================================================================
# CONSTANTS - Configuration values used throughout the app
# ============================================================================

# Color scheme for the application
COLOR_BACKGROUND = "#1e1e1e"  # Dark background
COLOR_ACCENT = "#0078d4"  # Microsoft blue
COLOR_SUCCESS = "#07b03b"  # Green for success
COLOR_WARNING = "#ffc107"  # Yellow for warnings
COLOR_ERROR = "#dc3545"  # Red for errors
COLOR_TEXT = "#ffffff"  # White text

# Paths to clean - Different cleanup locations
TEMP_LOCATIONS = [
    os.path.expandvars(r'%TEMP%'),  # Windows temp folder
    os.path.expandvars(r'%SystemRoot%\Temp'),  # System temp
    os.path.expandvars(r'%LocalAppData%\Temp'),  # User local temp
    os.path.expandvars(r'%AppData%\..\Local\Temp'),  # Application temp
]

# Browser cache locations
BROWSER_CACHE_LOCATIONS = [
    os.path.expandvars(r'%LocalAppData%\Google\Chrome\User Data\Default\Cache'),  # Chrome
    os.path.expandvars(r'%LocalAppData%\Google\Chrome\User Data\Default\Code Cache'),  # Chrome code
    os.path.expandvars(r'%LocalAppData%\Microsoft\Edge\User Data\Default\Cache'),  # Edge
    os.path.expandvars(r'%AppData%\Mozilla\Firefox\Profiles'),  # Firefox
]

# Log file locations
LOG_LOCATIONS = [
    os.path.expandvars(r'%SystemRoot%\Logs'),  # Windows logs
    os.path.expandvars(r'%ProgramData%\Logs'),  # Program data logs
]

# ============================================================================
# SCANNER CLASS - Scans system for unnecessary files
# ============================================================================
class SystemScanner(QThread):
    """
    Runs scanning operations in a separate thread to keep UI responsive
    Emits signals when items are found
    """
    
    # Signals - These notify the UI when scanning is complete
    scan_complete = pyqtSignal(dict)  # Signal sent when scan finishes
    scan_progress = pyqtSignal(str)  # Signal to update progress text
    error_signal = pyqtSignal(str)  # Signal for error messages

    def run(self):
        """
        Main scanning method - called when thread starts
        Scans all cleanup locations and returns results
        """
        try:
            # Initialize empty results dictionary
            results = {
                'temp_files': {'count': 0, 'size': 0, 'paths': []},
                'browser_cache': {'count': 0, 'size': 0, 'paths': []},
                'recycle_bin': {'count': 0, 'size': 0, 'size_bytes': 0},
                'log_files': {'count': 0, 'size': 0, 'paths': []},
                'old_downloads': {'count': 0, 'size': 0, 'paths': []},
                'startup_apps': {'count': 0, 'apps': []},
                'windows_update': {'count': 0, 'size': 0, 'paths': []},
            }

            # ============================================================
            # SCAN TEMP FILES
            # ============================================================
            self.scan_progress.emit("Scanning temporary files...")
            for location in TEMP_LOCATIONS:
                if os.path.exists(location):
                    try:
                        # Walk through all files in temp location
                        for root, dirs, files in os.walk(location):
                            for file in files:
                                try:
                                    file_path = os.path.join(root, file)
                                    # Get file size in bytes
                                    file_size = os.path.getsize(file_path)
                                    # Add to results
                                    results['temp_files']['count'] += 1
                                    results['temp_files']['size'] += file_size
                                    results['temp_files']['paths'].append(file_path)
                                except:
                                    pass  # Skip files we can't access
                    except:
                        pass  # Skip folders we can't access

            # ============================================================
            # SCAN BROWSER CACHE
            # ============================================================
            self.scan_progress.emit("Scanning browser cache...")
            for location in BROWSER_CACHE_LOCATIONS:
                if os.path.exists(location):
                    try:
                        # Walk through cache directories
                        for root, dirs, files in os.walk(location):
                            for file in files:
                                try:
                                    file_path = os.path.join(root, file)
                                    file_size = os.path.getsize(file_path)
                                    results['browser_cache']['count'] += 1
                                    results['browser_cache']['size'] += file_size
                                    results['browser_cache']['paths'].append(file_path)
                                except:
                                    pass
                    except:
                        pass

            # ============================================================
            # SCAN RECYCLE BIN
            # ============================================================
            self.scan_progress.emit("Scanning recycle bin...")
            try:
                # Use Windows API to get recycle bin info (alternative: use shell.recycler)
                # Get recycle bin from all drives
                for drive_letter in 'CDEFGH':  # Common drive letters
                    recycle_path = f'{drive_letter}:\\$Recycle.Bin'
                    if os.path.exists(recycle_path):
                        for item in os.listdir(recycle_path):
                            try:
                                item_path = os.path.join(recycle_path, item)
                                size = os.path.getsize(item_path)
                                results['recycle_bin']['size_bytes'] += size
                                results['recycle_bin']['count'] += 1
                            except:
                                pass
                # Convert bytes to MB/GB for display
                results['recycle_bin']['size'] = self._format_size(results['recycle_bin']['size_bytes'])
            except:
                pass

            # ============================================================
            # SCAN LOG FILES
            # ============================================================
            self.scan_progress.emit("Scanning log files...")
            for location in LOG_LOCATIONS:
                if os.path.exists(location):
                    try:
                        for root, dirs, files in os.walk(location):
                            for file in files:
                                # Check if file is a log file (.log, .txt containing logs)
                                if file.endswith('.log') or file.endswith('.txt'):
                                    try:
                                        file_path = os.path.join(root, file)
                                        file_size = os.path.getsize(file_path)
                                        results['log_files']['count'] += 1
                                        results['log_files']['size'] += file_size
                                        results['log_files']['paths'].append(file_path)
                                    except:
                                        pass
                    except:
                        pass

            # ============================================================
            # SCAN OLD DOWNLOADS (files not accessed in 6+ months)
            # ============================================================
            self.scan_progress.emit("Scanning old downloads...")
            downloads_path = os.path.expandvars(r'%UserProfile%\Downloads')
            if os.path.exists(downloads_path):
                try:
                    current_time = datetime.now()
                    six_months_ago = current_time - timedelta(days=180)  # 6 months
                    
                    for file in os.listdir(downloads_path):
                        try:
                            file_path = os.path.join(downloads_path, file)
                            # Get file modification time
                            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                            
                            # If file hasn't been modified in 6 months, it's old
                            if mod_time < six_months_ago:
                                file_size = os.path.getsize(file_path)
                                results['old_downloads']['count'] += 1
                                results['old_downloads']['size'] += file_size
                                results['old_downloads']['paths'].append(file_path)
                        except:
                            pass
                except:
                    pass

            # ============================================================
            # SCAN STARTUP APPS
            # ============================================================
            self.scan_progress.emit("Scanning startup programs...")
            try:
                # Read startup apps from Windows Registry
                reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
                
                # Enumerate all startup items
                index = 0
                while True:
                    try:
                        # Get each startup app name
                        app_name, app_path, _ = winreg.EnumValue(reg_key, index)
                        results['startup_apps']['apps'].append({
                            'name': app_name,
                            'path': app_path
                        })
                        results['startup_apps']['count'] += 1
                        index += 1
                    except OSError:
                        # Reached end of registry entries
                        break
                winreg.CloseKey(reg_key)
            except:
                pass

            # ============================================================
            # SCAN WINDOWS UPDATE CACHE
            # ============================================================
            self.scan_progress.emit("Scanning Windows Update cache...")
            update_cache_paths = [
                os.path.expandvars(r'%SystemRoot%\SoftwareDistribution\Download'),
                os.path.expandvars(r'%SystemRoot%\Temp'),
            ]
            
            for location in update_cache_paths:
                if os.path.exists(location):
                    try:
                        for root, dirs, files in os.walk(location):
                            for file in files:
                                # Look for Windows update files (.cab, .exe related to updates)
                                if file.endswith('.cab') or file.endswith('.tmp'):
                                    try:
                                        file_path = os.path.join(root, file)
                                        file_size = os.path.getsize(file_path)
                                        results['windows_update']['count'] += 1
                                        results['windows_update']['size'] += file_size
                                        results['windows_update']['paths'].append(file_path)
                                    except:
                                        pass
                    except:
                        pass

            # ============================================================
            # FORMAT SIZES FOR DISPLAY
            # ============================================================
            # Convert all byte sizes to human-readable format (MB, GB, etc)
            results['temp_files']['size'] = self._format_size(results['temp_files']['size'])
            results['browser_cache']['size'] = self._format_size(results['browser_cache']['size'])
            results['log_files']['size'] = self._format_size(results['log_files']['size'])
            results['old_downloads']['size'] = self._format_size(results['old_downloads']['size'])
            results['windows_update']['size'] = self._format_size(results['windows_update']['size'])

            # ============================================================
            # EMIT COMPLETED SIGNAL
            # ============================================================
            # Send results back to main UI thread
            self.scan_complete.emit(results)

        except Exception as e:
            # Emit error signal if something goes wrong
            self.error_signal.emit(f"Scan error: {str(e)}")

    def _format_size(self, size_bytes):
        """
        Convert bytes to human-readable format (B, KB, MB, GB)
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Formatted string like "1.2 MB"
        """
        # Define size units
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:  # If smaller than 1 KB
                return f"{size_bytes:.1f} {unit}"  # Return with one decimal
            size_bytes /= 1024.0  # Convert to next unit
        return f"{size_bytes:.1f} TB"  # If very large, return in TB


# ============================================================================
# CLEANER CLASS - Performs cleanup operations
# ============================================================================
class SystemCleaner(QThread):
    """
    Runs cleanup operations in a separate thread
    Emits progress signals for UI updates
    """
    
    # Signals for UI updates
    progress_signal = pyqtSignal(int, str)  # Progress percentage and message
    complete_signal = pyqtSignal(dict)  # Results when cleanup is done
    error_signal = pyqtSignal(str)  # Error message

    def __init__(self, cleanup_items):
        """
        Initialize cleaner with items to remove
        
        Args:
            cleanup_items: Dictionary of items to clean
        """
        super().__init__()
        self.cleanup_items = cleanup_items  # Store items to clean
        self.total_freed = 0  # Track total space freed
        self.items_deleted = 0  # Track items removed

    def run(self):
        """
        Main cleanup method - removes selected items
        """
        try:
            # Initialize results
            results = {
                'total_freed': '0 MB',
                'items_deleted': 0,
                'errors': []
            }

            # Calculate total items to process
            total_items = len(self.cleanup_items)
            current_item = 0

            # ============================================================
            # CLEAN TEMPORARY FILES
            # ============================================================
            if self.cleanup_items.get('temp_files', []):
                for file_path in self.cleanup_items['temp_files']:
                    try:
                        # Try to delete file
                        if os.path.exists(file_path):
                            os.remove(file_path)  # Delete the file
                            self.items_deleted += 1
                        current_item += 1
                        # Emit progress update
                        self.progress_signal.emit(
                            int((current_item / total_items) * 100),
                            f"Cleaning temp files... ({current_item}/{total_items})"
                        )
                    except Exception as e:
                        # Log errors but continue cleaning
                        results['errors'].append(f"Failed to delete {file_path}: {str(e)}")

            # ============================================================
            # CLEAN BROWSER CACHE
            # ============================================================
            if self.cleanup_items.get('browser_cache', []):
                for file_path in self.cleanup_items['browser_cache']:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            self.items_deleted += 1
                        current_item += 1
                        self.progress_signal.emit(
                            int((current_item / total_items) * 100),
                            f"Cleaning browser cache... ({current_item}/{total_items})"
                        )
                    except:
                        pass

            # ============================================================
            # EMPTY RECYCLE BIN
            # ============================================================
            if self.cleanup_items.get('recycle_bin'):
                try:
                    # Use PowerShell to empty recycle bin
                    ps_command = "Clear-RecycleBin -Force -Confirm:$false"
                    subprocess.run(
                        ["powershell", "-Command", ps_command],
                        check=False,
                        capture_output=True
                    )
                    self.progress_signal.emit(75, "Emptying recycle bin...")
                except:
                    pass

            # ============================================================
            # CLEAN LOG FILES
            # ============================================================
            if self.cleanup_items.get('log_files', []):
                for file_path in self.cleanup_items['log_files']:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            self.items_deleted += 1
                        current_item += 1
                        self.progress_signal.emit(
                            int((current_item / total_items) * 100),
                            f"Cleaning log files... ({current_item}/{total_items})"
                        )
                    except:
                        pass

            # ============================================================
            # FINAL PROGRESS UPDATE
            # ============================================================
            # Calculate total space freed
            total_space_freed = 0
            for size_str in [
                self.cleanup_items.get('temp_files_size', '0 MB'),
                self.cleanup_items.get('browser_cache_size', '0 MB'),
                self.cleanup_items.get('log_files_size', '0 MB'),
            ]:
                # Parse size string and add to total
                pass  # Simplified for demo

            # Emit completion signal
            results['total_freed'] = f"{self.items_deleted} items deleted"
            results['items_deleted'] = self.items_deleted
            self.progress_signal.emit(100, "Cleanup complete!")
            self.complete_signal.emit(results)

        except Exception as e:
            # Emit error if cleanup fails
            self.error_signal.emit(f"Cleanup error: {str(e)}")


# ============================================================================
# MAIN UI CLASS - The application window
# ============================================================================
class CleanupApp(QMainWindow):
    """
    Main application window for Windows Cleanup Tool
    Handles all UI interactions and manages scanner/cleaner threads
    """

    def __init__(self):
        """
        Initialize the application window
        """
        super().__init__()
        self.scanner = None  # Scanner thread object
        self.cleaner = None  # Cleaner thread object
        self.scan_results = {}  # Store scan results
        self.selected_items = {}  # Track what user selected to clean
        
        # ================================================================
        # WINDOW SETUP
        # ================================================================
        self.setWindowTitle("Windows Cleanup Tool")  # Window title
        self.setGeometry(100, 100, 800, 600)  # Position and size
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_BACKGROUND};
            }}
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: {COLOR_TEXT};
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #005a9e;
            }}
            QLabel {{
                color: {COLOR_TEXT};
            }}
            QListWidget {{
                background-color: #2d2d2d;
                color: {COLOR_TEXT};
                border: 1px solid #444;
            }}
            QCheckBox {{
                color: {COLOR_TEXT};
            }}
        """)  # Apply dark theme styling

        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)  # Space between elements
        main_layout.setContentsMargins(20, 20, 20, 20)  # Padding around edges

        # ================================================================
        # TITLE SECTION
        # ================================================================
        title = QLabel("🗑️  Windows Cleanup Tool")  # Main title
        title_font = QFont()
        title_font.setPointSize(18)  # Large title
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Clean unnecessary files and free up disk space")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_font.setItalic(True)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet(f"color: #888888;")  # Gray text
        main_layout.addWidget(subtitle)

        # ================================================================
        # BUTTON SECTION
        # ================================================================
        button_layout = QHBoxLayout()  # Horizontal layout for buttons
        
        # Scan button - starts the scanning process
        self.scan_btn = QPushButton("🔍 Scan System")
        self.scan_btn.setMinimumHeight(40)  # Make button taller
        self.scan_btn.clicked.connect(self.start_scan)  # Connect to scan method
        button_layout.addWidget(self.scan_btn)

        # Clean button - starts cleanup (disabled until scan completes)
        self.clean_btn = QPushButton("✨ Clean Now")
        self.clean_btn.setMinimumHeight(40)
        self.clean_btn.clicked.connect(self.start_cleanup)
        self.clean_btn.setEnabled(False)  # Disable until we have scan results
        button_layout.addWidget(self.clean_btn)

        # Settings button
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setMinimumHeight(40)
        button_layout.addWidget(self.settings_btn)

        main_layout.addLayout(button_layout)

        # ================================================================
        # STATUS SECTION
        # ================================================================
        self.status_label = QLabel("Ready to scan. Click 'Scan System' to begin.")
        self.status_label.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 11px;")
        main_layout.addWidget(self.status_label)

        # Progress bar - shows scanning/cleaning progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)  # Start at 0%
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #444;
                border-radius: 5px;
                text-align: center;
                background-color: #2d2d2d;
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_SUCCESS};
            }}
        """)
        main_layout.addWidget(self.progress_bar)

        # ================================================================
        # RESULTS SECTION - Tabs for different categories
        # ================================================================
        self.tabs = QTabWidget()  # Create tab widget
        self.tabs.setStyleSheet(f"""
            QTabWidget {{
                background-color: {COLOR_BACKGROUND};
                color: {COLOR_TEXT};
            }}
            QTabBar::tab {{
                background-color: #2d2d2d;
                color: {COLOR_TEXT};
                padding: 5px 10px;
                margin: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLOR_ACCENT};
            }}
        """)

        # Tab 1: Temp Files
        self.tab_temp = self.create_result_tab("Temp Files")
        self.tabs.addTab(self.tab_temp, "📁 Temp Files")

        # Tab 2: Browser Cache
        self.tab_browser = self.create_result_tab("Browser Cache")
        self.tabs.addTab(self.tab_browser, "🔍 Browser Cache")

        # Tab 3: Startup Apps
        self.tab_startup = self.create_result_tab("Startup Apps")
        self.tabs.addTab(self.tab_startup, "⚡ Startup Apps")

        # Tab 4: Other
        self.tab_other = self.create_result_tab("Other Files")
        self.tabs.addTab(self.tab_other, "📦 Other")

        main_layout.addWidget(self.tabs)

        # ================================================================
        # SUMMARY SECTION
        # ================================================================
        summary_layout = QHBoxLayout()
        
        # Space to free label
        self.space_label = QLabel("Space to Free: 0 MB")
        self.space_label.setStyleSheet(f"color: {COLOR_SUCCESS}; font-weight: bold; font-size: 12px;")
        summary_layout.addWidget(self.space_label)

        summary_layout.addStretch()  # Add flexible space

        # Items count label
        self.items_label = QLabel("Items Found: 0")
        self.items_label.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 12px;")
        summary_layout.addWidget(self.items_label)

        main_layout.addLayout(summary_layout)

    def create_result_tab(self, category):
        """
        Create a tab for displaying scan results
        
        Args:
            category: Name of the category (Temp Files, etc)
            
        Returns:
            QWidget containing the tab content
        """
        # Create widget and layout for tab
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create scrollable list
        list_widget = QListWidget()
        list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: #2d2d2d;
                color: {COLOR_TEXT};
                border: 1px solid #444;
                outline: none;
            }}
            QListWidget::item:selected {{
                background-color: {COLOR_ACCENT};
            }}
        """)
        layout.addWidget(list_widget)

        # Store reference to list widget for later use
        setattr(self, f'list_{category.lower().replace(" ", "_")}', list_widget)

        return widget

    def start_scan(self):
        """
        Start system scanning
        Called when user clicks "Scan System" button
        """
        # Disable buttons during scan
        self.scan_btn.setEnabled(False)
        self.clean_btn.setEnabled(False)

        # Update status
        self.status_label.setText("🔄 Scanning system... Please wait")
        self.progress_bar.setValue(0)

        # Create and start scanner thread
        self.scanner = SystemScanner()
        self.scanner.scan_complete.connect(self.on_scan_complete)  # Handle completion
        self.scanner.scan_progress.connect(self.on_scan_progress)  # Handle progress
        self.scanner.error_signal.connect(self.on_scan_error)  # Handle errors
        self.scanner.start()  # Start scanning in background thread

    def on_scan_progress(self, message):
        """
        Update UI with scan progress
        
        Args:
            message: Progress message to display
        """
        self.status_label.setText(message)

    def on_scan_complete(self, results):
        """
        Handle scan completion
        Populate UI with scan results
        
        Args:
            results: Dictionary containing scan results
        """
        # Store results for later use
        self.scan_results = results

        # ================================================================
        # POPULATE TEMP FILES TAB
        # ================================================================
        if results['temp_files']['paths']:
            for path in results['temp_files']['paths']:
                item = QListWidgetItem(f"☐ {path}")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Make checkable
                item.setCheckState(Qt.Checked)  # Check by default
                # Add to list widget
        
        # ================================================================
        # POPULATE BROWSER CACHE TAB
        # ================================================================
        if results['browser_cache']['paths']:
            for path in results['browser_cache']['paths']:
                item = QListWidgetItem(f"☐ {path}")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)

        # ================================================================
        # UPDATE STATUS AND BUTTONS
        # ================================================================
        # Enable clean button
        self.clean_btn.setEnabled(True)
        self.scan_btn.setEnabled(True)

        # Calculate total space
        total_space = 0
        total_items = 0

        # Add sizes from all categories
        for category in results:
            if isinstance(results[category], dict) and 'count' in results[category]:
                total_items += results[category]['count']

        # Update labels
        self.status_label.setText(f"✅ Scan complete! Found {total_items} items to clean")
        self.items_label.setText(f"Items Found: {total_items}")
        self.space_label.setText(f"Space to Free: {results['temp_files']['size']}")
        self.progress_bar.setValue(100)

    def on_scan_error(self, error):
        """
        Handle scan errors
        
        Args:
            error: Error message
        """
        # Show error message to user
        QMessageBox.critical(self, "Scan Error", error)
        self.status_label.setText("❌ Scan failed. Please try again.")
        self.scan_btn.setEnabled(True)

    def start_cleanup(self):
        """
        Start cleanup operation
        Called when user clicks "Clean Now" button
        """
        # Ask user for confirmation before deleting
        reply = QMessageBox.warning(
            self,
            "Confirm Cleanup",
            "This will permanently delete the selected files.\n\nAre you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No
        )

        # If user didn't click Yes, cancel cleanup
        if reply != QMessageBox.Yes:
            return

        # Disable buttons during cleanup
        self.scan_btn.setEnabled(False)
        self.clean_btn.setEnabled(False)

        # Update status
        self.status_label.setText("🧹 Cleaning system... Please wait")
        self.progress_bar.setValue(0)

        # Prepare cleanup items from scan results
        cleanup_items = {}
        if self.scan_results.get('temp_files', {}).get('paths'):
            cleanup_items['temp_files'] = self.scan_results['temp_files']['paths']
        if self.scan_results.get('browser_cache', {}).get('paths'):
            cleanup_items['browser_cache'] = self.scan_results['browser_cache']['paths']

        # Create and start cleaner thread
        self.cleaner = SystemCleaner(cleanup_items)
        self.cleaner.progress_signal.connect(self.on_cleanup_progress)  # Handle progress
        self.cleaner.complete_signal.connect(self.on_cleanup_complete)  # Handle completion
        self.cleaner.error_signal.connect(self.on_cleanup_error)  # Handle errors
        self.cleaner.start()  # Start cleaning in background

    def on_cleanup_progress(self, progress, message):
        """
        Update UI during cleanup
        
        Args:
            progress: Progress percentage (0-100)
            message: Progress message
        """
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)

    def on_cleanup_complete(self, results):
        """
        Handle cleanup completion
        
        Args:
            results: Dictionary with cleanup results
        """
        # Enable buttons
        self.scan_btn.setEnabled(True)
        self.clean_btn.setEnabled(True)

        # Show success message
        message = f"✅ Cleanup Complete!\n\n{results.get('items_deleted', 0)} items deleted"
        if results.get('errors'):
            message += f"\n\n⚠️  {len(results['errors'])} items could not be deleted"

        QMessageBox.information(self, "Cleanup Complete", message)
        
        # Update status
        self.status_label.setText("✨ System cleaned successfully!")
        self.progress_bar.setValue(100)

    def on_cleanup_error(self, error):
        """
        Handle cleanup errors
        
        Args:
            error: Error message
        """
        QMessageBox.critical(self, "Cleanup Error", error)
        self.status_label.setText("❌ Cleanup failed.")
        self.scan_btn.setEnabled(True)
        self.clean_btn.setEnabled(True)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
def main():
    """
    Main function - starts the application
    """
    # Create Qt application
    app = QApplication(sys.argv)

    # Create main window
    window = CleanupApp()
    
    # Show window
    window.show()

    # Run application event loop (waits for user interactions)
    sys.exit(app.exec_())


# ============================================================================
# SCRIPT EXECUTION
# ============================================================================
if __name__ == "__main__":
    # Only run main() if this script is executed directly (not imported)
    main()
