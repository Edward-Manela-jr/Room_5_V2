#!/usr/bin/env python3
"""
Image Organizer App - Windows GUI Application
A comprehensive tool for organizing and fixing image collections
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk, ExifTags
from pathlib import Path
import datetime
import calendar
import re

# Import our existing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Station codes for dropdown
STATION_CODES = [
    "CHIPAT01", "CHINSA01", "CHIPEPO01", "CHOMA001", "ISOKA001",
    "KABOMP01", "KABWE001", "KABWE002", "KAFIRO01", "KAFUE001",
    "KALABO01", "KAOMA001", "KASAMA01", "KASEMP01", "KAWAMB01",
    "LIVING01", "LUNDAZ01", "LUSAKA01", "LUSAKA02", "MAGOYE01",
    "MANSA001", "MANSA002", "MBALA001", "MFUWE001", "MISAMFO1",
    "MKUSHI01", "MONGU002", "MPIKA001", "MSEKER01", "MTMAKU01",
    "MUMBWA01", "MPULUNGU", "MWINIL01", "NDOLA001", "PETAUK01",
    "SAMFYA001", "SENANG01", "SERENJO1", "SIMON001", "SESHEK01",
    "SOLWEZ01", "ZAMBEZ01"
]

# Station code aliases for dropdown
STATION_CODE_ALIASES = [
    "MOZ304A", "MOZ305A", "MOZ306A", "MOZ307A", "MOZ308A",
    "MOZ309A", "MOZ310A", "MOZ311A", "MOZ312A", "MOZ313A",
    "MOZ314A", "MOZ315A", "MOZ316A", "MOZ317A", "MOZ318A",
    "MOZ319A", "MOZ320A", "MOZ321A", "MOZ322A", "MOZ323A",
    "MOZ324A", "MOZ325A", "MOZ326A", "MOZ327A", "MOZ328A",
    "MOZ329A", "MOZ330A", "MOZ331A", "MOZ332A", "MOZ333A",
    "MOZ334A", "MOZ335A", "MOZ336A", "MOZ337A", "MOZ338A",
    "MOZ339A", "MOZ340A", "MOZ341A", "MOZ342A", "MOZ343A",
    "MOZ344A", "MOZ345A"
]

# Years for dropdown (1970-2026)
YEARS = list(range(1970, 2027))

# Observation times for dropdown
OBSERVATION_TIMES = ["06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18"]

class ImageOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Organizer Pro")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Variables
        self.source_folder = ""
        self.is_processing = False
        self.audio_orderer = None
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """Modern styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
    
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame that works on small screens"""
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return scrollable_frame
        
    def setup_ui(self):
        """Main UI setup"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Folder Organization
        self.org_tab = ttk.Frame(notebook)
        notebook.add(self.org_tab, text='📁 Folder Organization')
        self.setup_org_tab()
        
        # Tab 2: Image Rotation
        self.rotate_tab = ttk.Frame(notebook)
        notebook.add(self.rotate_tab, text='🔄 Image Rotation')
        self.setup_rotate_tab()
        
        # Tab 3: Station Alias
        self.alias_tab = ttk.Frame(notebook)
        notebook.add(self.alias_tab, text='🏷️ Station Alias')
        self.setup_alias_tab()
        
        # Tab 4: Interactive Fix
        self.interactive_tab = ttk.Frame(notebook)
        notebook.add(self.interactive_tab, text='👁️ Interactive Fix')
        self.setup_interactive_tab()
        
        # Tab 5: Audio Ordering
        self.audio_tab = ttk.Frame(notebook)
        notebook.add(self.audio_tab, text='🎤 Audio Ordering')
        self.setup_audio_tab()
        
        # Tab 6: Visual Number Ordering
        self.visual_tab = ttk.Frame(notebook)
        notebook.add(self.visual_tab, text='🔢 Visual Ordering')
        self.setup_visual_tab()
        
        # Tab 7: Simple 1-12 Renaming
        self.simple_rename_tab = ttk.Frame(notebook)
        notebook.add(self.simple_rename_tab, text='🔢 1-12 Rename')
        self.setup_simple_rename_tab()
        
        # Tab 8: Month Selector with Cropped Previews
        self.month_selector_tab = ttk.Frame(notebook)
        notebook.add(self.month_selector_tab, text='🖼️ Month Selector')
        self.setup_month_selector_tab()
        
        # Tab 9: Settings
        self.settings_tab = ttk.Frame(notebook)
        notebook.add(self.settings_tab, text='⚙️ Settings')
        self.setup_settings_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_org_tab(self):
        """Folder organization tab"""
        # Main frame
        main_frame = ttk.Frame(self.org_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="📁 Folder Organization", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame, text="Select Folder", padding="10")
        folder_frame.pack(fill='x', pady=(0, 20))
        
        self.folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=70)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side='right')
        
        # Operations
        ops_frame = ttk.LabelFrame(main_frame, text="Operations", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        btn_frame = ttk.Frame(ops_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="📂 Organize Images", command=self.organize_images).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="↩️ Undo Organization", command=self.undo_organization).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🧹 Clean Empty Folders", command=self.clean_folders).pack(side='left', padx=5)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.pack(fill='both', expand=True)
        
        info_text = """
📂 Organize Images: Sort images into town/year folders
   - Images: Town/Year/ structure
   - Documents: Extension/Town/ structure

↩️ Undo Organization: Move all files back to main folder

🧹 Clean Empty Folders: Remove all empty directories
        """
        
        info_label = ttk.Label(info_frame, text=info_text.strip(), justify='left')
        info_label.pack()
        
    def setup_rotate_tab(self):
        """Image rotation tab"""
        main_frame = ttk.Frame(self.rotate_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="🔄 Image Rotation", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame, text="Select Folder", padding="10")
        folder_frame.pack(fill='x', pady=(0, 20))
        
        self.rotate_folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.rotate_folder_var, width=70)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_rotate_folder)
        browse_btn.pack(side='right')
        
        # Operations
        ops_frame = ttk.LabelFrame(main_frame, text="Rotation Options", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        btn_frame = ttk.Frame(ops_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="🔧 Fix EXIF Orientation", command=self.fix_exif_rotation).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📐 Fix All Rotations", command=self.fix_all_rotations).pack(side='left', padx=5)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.pack(fill='both', expand=True)
        
        info_text = """
🔧 Fix EXIF Orientation: Fix images based on EXIF data
   - Only fixes images with EXIF orientation tags
   - Preserves image quality
   - Handles common orientation values (1-8)

📐 Fix All Rotations: Convert all portrait to landscape
   - Rotates portrait images to landscape orientation
   - Useful for bulk orientation correction
   - May need manual review for perfect results
        """
        
        info_label = ttk.Label(info_frame, text=info_text.strip(), justify='left')
        info_label.pack()
        
    def setup_interactive_tab(self):
        """Interactive fix tab"""
        main_frame = ttk.Frame(self.interactive_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="👁️ Interactive Fix", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame, text="Select Folder", padding="10")
        folder_frame.pack(fill='x', pady=(0, 20))
        
        self.interactive_folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.interactive_folder_var, width=70)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_interactive_folder)
        browse_btn.pack(side='right')
        
        # Operations
        ops_frame = ttk.LabelFrame(main_frame, text="Interactive Review", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(ops_frame, text="👁️ Start Interactive Review", command=self.start_interactive_review).pack()
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.pack(fill='both', expand=True)
        
        info_text = """
👁️ Start Interactive Review: Manual image rotation review
   - Opens each portrait image in default viewer
   - You choose the correct rotation direction
   - Options: 0°, 90°, 180°, 270°, skip, or quit
   - Perfect for precise orientation control

⚠️  Note: This process opens your default image viewer
   You'll need to switch between the app and viewer
        """
        
        info_label = ttk.Label(info_frame, text=info_text.strip(), justify='left')
        info_label.pack()
        
    def setup_alias_tab(self):
        """Station alias tab"""
        main_frame = self.create_scrollable_frame(self.alias_tab)
        main_frame_padding = ttk.Frame(main_frame, padding="10")
        main_frame_padding.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame_padding, text="🏷️ Station Alias", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame_padding, text="Select Folder", padding="10")
        folder_frame.pack(fill='x', pady=(0, 20))
        
        self.alias_folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.alias_folder_var, width=70)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_alias_folder)
        browse_btn.pack(side='right')
        
        # Configuration
        config_frame = ttk.LabelFrame(main_frame_padding, text="Station Configuration", padding="10")
        config_frame.pack(fill='x', pady=(0, 20))
        
        # Station dropdown
        station_frame = ttk.Frame(config_frame)
        station_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(station_frame, text="Station Name:").pack(side='left', padx=(0, 10))
        self.station_var = tk.StringVar()
        station_combo = ttk.Combobox(station_frame, textvariable=self.station_var, values=STATION_CODES, width=20)
        station_combo.pack(side='left', padx=(0, 10))
        if STATION_CODES:
            station_combo.current(0)
        
        # Station code dropdown
        code_frame = ttk.Frame(config_frame)
        code_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(code_frame, text="Station Code:").pack(side='left', padx=(0, 10))
        self.station_code_var = tk.StringVar()
        code_combo = ttk.Combobox(code_frame, textvariable=self.station_code_var, values=STATION_CODE_ALIASES, width=20)
        code_combo.pack(side='left', padx=(0, 10))
        if STATION_CODE_ALIASES:
            code_combo.current(0)
        ttk.Label(code_frame, text="(e.g., MOZ304A)", font=('Arial', 8), foreground='gray').pack(side='left')
        
        # Year dropdown
        year_frame = ttk.Frame(config_frame)
        year_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(year_frame, text="Year:").pack(side='left', padx=(0, 10))
        self.year_var = tk.StringVar()
        year_combo = ttk.Combobox(year_frame, textvariable=self.year_var, values=YEARS, width=10)
        year_combo.pack(side='left', padx=(0, 10))
        # Set current year as default
        current_year = datetime.datetime.now().year
        if current_year in YEARS:
            year_combo.set(str(current_year))
        
        # Observation time dropdown
        time_frame = ttk.Frame(config_frame)
        time_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(time_frame, text="Observation Time:").pack(side='left', padx=(0, 10))
        self.obs_time_var = tk.StringVar()
        time_combo = ttk.Combobox(time_frame, textvariable=self.obs_time_var, values=OBSERVATION_TIMES, width=8)
        time_combo.pack(side='left', padx=(0, 10))
        time_combo.set("06")
        
        # Operations
        ops_frame = ttk.LabelFrame(main_frame_padding, text="Operations", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        btn_frame = ttk.Frame(ops_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="🏷️ Create Station Aliases", command=self.create_station_aliases).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔍 Preview Changes", command=self.preview_alias_changes).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="↩️ Restore Original Names", command=self.restore_original_names).pack(side='left', padx=5)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame_padding, text="Information", padding="10")
        info_frame.pack(fill='both', expand=True)
        
        info_text = """
🏷️ Create Station Aliases: Rename images to station format
   - Format: STATION-YEARMONTHDAYTIME.extension
   - Handles missing months automatically
   - Example: CHIPEPO01-2006013106.jpg

🔍 Preview Changes: See what will be renamed before executing
   - Shows file-to-month mapping
   - Detects missing months from folder name
   - Safe preview without making changes

↩️ Restore Original Names: Undo alias changes
   - Restores 1.jpg, 2.jpg, etc. naming
   - Works on previously processed folders
   - Safe undo functionality

📋 Supported Features:
   - Missing months detection (e.g., "Missing 01,07,11")
   - Automatic month extraction from filenames
   - All station codes from your network
   - Years 1970-2026
   - Multiple observation times
        """
        
        info_text_widget = scrolledtext.ScrolledText(info_frame, height=15, width=80, wrap=tk.WORD, state='disabled')
        info_text_widget.pack(fill='both', expand=True)
        info_text_widget.config(state='normal')
        info_text_widget.insert('1.0', info_text.strip())
        info_text_widget.config(state='disabled')
        
    def setup_audio_tab(self):
        """Audio ordering tab"""
        main_frame = self.create_scrollable_frame(self.audio_tab)
        main_frame_padding = ttk.Frame(main_frame, padding="10")
        main_frame_padding.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame_padding, text="🎤 Audio Ordering", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame_padding, text="Select Folder", padding="10")
        folder_frame.pack(fill='x', pady=(0, 20))
        
        self.audio_folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.audio_folder_var, width=70)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_audio_folder)
        browse_btn.pack(side='right')
        
        # Configuration
        config_frame = ttk.LabelFrame(main_frame_padding, text="Station Configuration", padding="10")
        config_frame.pack(fill='x', pady=(0, 20))
        
        # Station dropdown
        station_frame = ttk.Frame(config_frame)
        station_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(station_frame, text="Station Name:").pack(side='left', padx=(0, 10))
        self.audio_station_var = tk.StringVar()
        station_combo = ttk.Combobox(station_frame, textvariable=self.audio_station_var, values=STATION_CODES, width=20)
        station_combo.pack(side='left', padx=(0, 10))
        if STATION_CODES:
            station_combo.current(0)
        
        # Station code dropdown
        code_frame = ttk.Frame(config_frame)
        code_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(code_frame, text="Station Code:").pack(side='left', padx=(0, 10))
        self.audio_station_code_var = tk.StringVar()
        code_combo = ttk.Combobox(code_frame, textvariable=self.audio_station_code_var, values=STATION_CODE_ALIASES, width=20)
        code_combo.pack(side='left', padx=(0, 10))
        if STATION_CODE_ALIASES:
            code_combo.current(0)
        ttk.Label(code_frame, text="(e.g., MOZ304A)", font=('Arial', 8), foreground='gray').pack(side='left')
        
        # Year dropdown
        year_frame = ttk.Frame(config_frame)
        year_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(year_frame, text="Year:").pack(side='left', padx=(0, 10))
        self.audio_year_var = tk.StringVar()
        year_combo = ttk.Combobox(year_frame, textvariable=self.audio_year_var, values=YEARS, width=10)
        year_combo.pack(side='left', padx=(0, 10))
        current_year = datetime.datetime.now().year
        if current_year in YEARS:
            year_combo.set(str(current_year))
        
        # Observation time dropdown
        time_frame = ttk.Frame(config_frame)
        time_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(time_frame, text="Observation Time:").pack(side='left', padx=(0, 10))
        self.audio_obs_time_var = tk.StringVar()
        time_combo = ttk.Combobox(time_frame, textvariable=self.audio_obs_time_var, values=OBSERVATION_TIMES, width=8)
        time_combo.pack(side='left', padx=(0, 10))
        time_combo.set("06")
        
        # Audio controls
        audio_frame = ttk.LabelFrame(main_frame_padding, text="Audio Recording", padding="10")
        audio_frame.pack(fill='x', pady=(0, 20))
        
        # Recording status
        self.audio_status_var = tk.StringVar(value="Ready to record")
        status_label = ttk.Label(audio_frame, textvariable=self.audio_status_var, font=('Arial', 10, 'bold'))
        status_label.pack(pady=(0, 10))
        
        # Control buttons
        btn_frame = ttk.Frame(audio_frame)
        btn_frame.pack()
        
        self.record_btn = ttk.Button(btn_frame, text="🎤 Start Recording", command=self.start_audio_recording)
        self.record_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹️ Stop Recording", command=self.stop_audio_recording, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🔧 Install Speech Recognition", command=self.install_speech_recognition).pack(side='left', padx=5)
        
        # Detected numbers display
        detected_frame = ttk.LabelFrame(main_frame_padding, text="Detected Month Numbers", padding="10")
        detected_frame.pack(fill='x', pady=(0, 20))
        
        self.detected_numbers_var = tk.StringVar(value="No numbers detected yet")
        detected_label = ttk.Label(detected_frame, textvariable=self.detected_numbers_var, font=('Arial', 12))
        detected_label.pack()
        
        # Operations
        ops_frame = ttk.LabelFrame(main_frame_padding, text="Operations", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        ops_btn_frame = ttk.Frame(ops_frame)
        ops_btn_frame.pack()
        
        ttk.Button(ops_btn_frame, text="🏷️ Apply Audio Ordering", command=self.apply_audio_ordering).pack(side='left', padx=5)
        ttk.Button(ops_btn_frame, text="🔄 Clear Detection", command=self.clear_audio_detection).pack(side='left', padx=5)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame_padding, text="Instructions", padding="10")
        info_frame.pack(fill='both', expand=True)
        
        info_text = """
🎤 Audio Ordering Instructions:

1. Select folder with jumbled images
2. Configure station, year, and time
3. Click "Start Recording"
4. Open your image viewer
5. Swipe through images in correct order
6. Say month numbers as you view each image:
   - Say "one", "two", "three" OR "1", "2", "3"
   - Only numbers 1-12 are recognized
7. Click "Stop Recording" when done
8. Review detected numbers
9. Click "Apply Audio Ordering" to rename files

💡 Tips:
- Speak clearly and pause between numbers
- Works with both word and digit numbers
- Duplicate numbers are automatically ignored
- Install Speech Recognition if needed

📋 Example workflow:
- View image #1 → Say "one"
- View image #2 → Say "two" 
- View image #3 → Say "four" (if month 3 is missing)
- Continue through all images
- Apply ordering to rename correctly
        """
        
        info_text_widget = scrolledtext.ScrolledText(info_frame, height=15, width=80, wrap=tk.WORD, state='disabled')
        info_text_widget.pack(fill='both', expand=True)
        info_text_widget.config(state='normal')
        info_text_widget.insert('1.0', info_text.strip())
        info_text_widget.config(state='disabled')
        
    def setup_visual_tab(self):
        """Visual number ordering tab"""
        main_frame = self.create_scrollable_frame(self.visual_tab)
        main_frame_padding = ttk.Frame(main_frame, padding="10")
        main_frame_padding.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame_padding, text="🔢 Visual Number Ordering", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame_padding, text="Select Folder", padding="10")
        folder_frame.pack(fill='x', pady=(0, 20))
        
        self.visual_folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.visual_folder_var, width=70)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_visual_folder)
        browse_btn.pack(side='right')
        
        # Configuration
        config_frame = ttk.LabelFrame(main_frame_padding, text="Station Configuration", padding="10")
        config_frame.pack(fill='x', pady=(0, 20))
        
        # Station dropdown
        station_frame = ttk.Frame(config_frame)
        station_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(station_frame, text="Station Name:").pack(side='left', padx=(0, 10))
        self.visual_station_var = tk.StringVar()
        station_combo = ttk.Combobox(station_frame, textvariable=self.visual_station_var, values=STATION_CODES, width=20)
        station_combo.pack(side='left', padx=(0, 10))
        if STATION_CODES:
            station_combo.current(0)
        
        # Station code dropdown
        code_frame = ttk.Frame(config_frame)
        code_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(code_frame, text="Station Code:").pack(side='left', padx=(0, 10))
        self.visual_station_code_var = tk.StringVar()
        code_combo = ttk.Combobox(code_frame, textvariable=self.visual_station_code_var, values=STATION_CODE_ALIASES, width=20)
        code_combo.pack(side='left', padx=(0, 10))
        if STATION_CODE_ALIASES:
            code_combo.current(0)
        ttk.Label(code_frame, text="(e.g., MOZ304A)", font=('Arial', 8), foreground='gray').pack(side='left')
        
        # Year dropdown
        year_frame = ttk.Frame(config_frame)
        year_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(year_frame, text="Year:").pack(side='left', padx=(0, 10))
        self.visual_year_var = tk.StringVar()
        year_combo = ttk.Combobox(year_frame, textvariable=self.visual_year_var, values=YEARS, width=10)
        year_combo.pack(side='left', padx=(0, 10))
        current_year = datetime.datetime.now().year
        if current_year in YEARS:
            year_combo.set(str(current_year))
        
        # Observation time dropdown
        time_frame = ttk.Frame(config_frame)
        time_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(time_frame, text="Observation Time:").pack(side='left', padx=(0, 10))
        self.visual_obs_time_var = tk.StringVar()
        time_combo = ttk.Combobox(time_frame, textvariable=self.visual_obs_time_var, values=OBSERVATION_TIMES, width=8)
        time_combo.pack(side='left', padx=(0, 10))
        time_combo.set("06")
        
        # Operations
        ops_frame = ttk.LabelFrame(main_frame_padding, text="Operations", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(ops_frame, text="🔢 Open Visual Selector", command=self.open_visual_selector).pack(pady=10)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame_padding, text="Instructions", padding="10")
        info_frame.pack(fill='both', expand=True)
        
        info_text = """
🔢 Visual Number Ordering Instructions:

1. Select folder with jumbled images
2. Configure station, year, and time
3. Click "Open Visual Selector"
4. A new window will open with numbers 1-12
5. Open your image viewer with the selected folder
6. Look at each image in order
7. Click the corresponding month number for each image:
   - First image → Click its month number
   - Second image → Click its month number
   - Continue through all images
8. Numbers will highlight as you select them
9. Click "Apply Ordering" when done
10. Files will be renamed based on your selection order

💡 Features:
- Visual 3x4 grid of number buttons (1-12)
- Color-coded highlighting for selection order
- Clear selection option to start over
- Real-time order display
- Validation against image count

📋 Example Workflow:
- Image #1 shows January → Click "1"
- Image #2 shows March → Click "3" 
- Image #3 shows May → Click "5"
- Continue through all images
- Apply ordering → Files renamed correctly

🎯 Perfect for:
- When you can see the months in images
- When audio recognition isn't suitable
- Quick visual verification
- Precise manual control
        """
        
        info_text_widget = scrolledtext.ScrolledText(info_frame, height=15, width=80, wrap=tk.WORD, state='disabled')
        info_text_widget.pack(fill='both', expand=True)
        info_text_widget.config(state='normal')
        info_text_widget.insert('1.0', info_text.strip())
        info_text_widget.config(state='disabled')
    
    def setup_simple_rename_tab(self):
        """Simple 1-12 renaming tab"""
        main_frame = self.create_scrollable_frame(self.simple_rename_tab)
        main_frame_padding = ttk.Frame(main_frame, padding="10")
        main_frame_padding.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame_padding, text="🔢 Simple 1-12 Rename", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame_padding, text="Select Folder", padding="10")
        folder_frame.pack(fill='x', pady=(0, 20))
        
        self.simple_folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.simple_folder_var, width=70)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_simple_folder)
        browse_btn.pack(side='right')
        
        # Operations
        ops_frame = ttk.LabelFrame(main_frame_padding, text="Operations", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(ops_frame, text="🔢 Rename to 1-12", command=self.simple_rename_images).pack(pady=10)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame_padding, text="Instructions", padding="10")
        info_frame.pack(fill='both', expand=True)
        
        info_text = """
🔢 Simple 1-12 Rename Instructions:

1. Select a folder containing images
2. Click "Rename to 1-12"
3. Images will be renamed sequentially:
   - First image → 1.jpg (or 1.png, etc.)
   - Second image → 2.jpg
   - Third image → 3.jpg
   - And so on...

💡 Features:
- Renames images in alphabetical order
- Preserves original file extensions
- Works with any number of images (1-12 or more)
- Simple and fast

📋 Example:
Before:
  - IMG_001.jpg
  - IMG_002.jpg
  - IMG_003.jpg

After:
  - 1.jpg
  - 2.jpg
  - 3.jpg

🎯 Perfect for:
- Preparing images for the Station Alias feature
- Quick sequential numbering
- Organizing images by month order
        """
        
        info_text_widget = scrolledtext.ScrolledText(info_frame, height=15, width=80, wrap=tk.WORD, state='disabled')
        info_text_widget.pack(fill='both', expand=True)
        info_text_widget.config(state='normal')
        info_text_widget.insert('1.0', info_text.strip())
        info_text_widget.config(state='disabled')
        
    def setup_month_selector_tab(self):
        """Month selector tab with cropped previews"""
        main_frame = self.create_scrollable_frame(self.month_selector_tab)
        main_frame_padding = ttk.Frame(main_frame, padding="10")
        main_frame_padding.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame_padding, text="🖼️ Month Selector with Cropped Previews", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Description
        desc_frame = ttk.LabelFrame(main_frame_padding, text="About", padding="10")
        desc_frame.pack(fill='x', pady=(0, 20))
        
        desc_text = """
 🖼️ Browse folder, view cropped previews (top-left half), and select month numbers to rename files.
 
 Features:
 • Browse and select a folder with images
 • View cropped previews (top-left half) of each image
 • Scroll through images within the app
 • Click month buttons (1-12) to select the month for each image
 • Rename files based on selected months
        """
        
        desc_label = ttk.Label(desc_frame, text=desc_text.strip(), justify='left')
        desc_label.pack()
        
        # Open button
        ops_frame = ttk.LabelFrame(main_frame_padding, text="Open Month Selector", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(ops_frame, text="🖼️ Open Month Selector", 
                 command=self.open_month_selector).pack(pady=10)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame_padding, text="Instructions", padding="10")
        info_frame.pack(fill='both', expand=True)
        
        info_text = """
 🖼️ Month Selector Instructions:
 
 1. Click "Open Month Selector" to launch the tool
 2. Browse and select a folder with images
 3. Use Previous/Next buttons or scroll to navigate images
 4. The app shows cropped previews (top-left half) of each image
 5. Click the month number (1-12) that matches the image:
    - 1 = January, 2 = February, 3 = March
    - 4 = April, 5 = May, 6 = June
    - 7 = July, 8 = August, 9 = September
    - 10 = October, 11 = November, 12 = December
 6. You can jump to a specific image number
 7. Click "Apply & Rename" to rename files
 
 💡 Tips:
 - Use the scrollbar to navigate through images
 - Selected months are shown in red, unselected in green
 - The counter shows how many images you've assigned months to
 - Files are renamed to their month number (e.g., 01.jpg, 02.jpg)
 
 🎯 Perfect for:
 - When you can visually identify months in images
 - Previewing the top-left portion where dates often appear
 - Quick month-based organization
        """
        
        info_text_widget = scrolledtext.ScrolledText(info_frame, height=20, width=80, wrap=tk.WORD, state='disabled')
        info_text_widget.pack(fill='both', expand=True)
        info_text_widget.config(state='normal')
        info_text_widget.insert('1.0', info_text.strip())
        info_text_widget.config(state='disabled')
        
    def setup_settings_tab(self):
        """Settings tab"""
        main_frame = ttk.Frame(self.settings_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="⚙️ Settings", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="About", padding="10")
        info_frame.pack(fill='x', pady=(0, 20))
        
        about_text = """
Image Organizer Pro v1.0

A comprehensive tool for organizing and fixing image collections.

Features:
• Automatic folder organization by town and year
• EXIF-based orientation correction
• Bulk portrait-to-landscape conversion
• Interactive manual review
• Support for multiple image formats

Created by: Edward Manela Jr
GitHub: https://github.com/Edward-Manela-jr/Room_5
        """
        
        about_label = ttk.Label(info_frame, text=about_text.strip(), justify='left')
        about_label.pack()
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill='both', expand=True)
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Log", command=self.clear_log).pack(pady=(10, 0))
        
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        
    def browse_folder(self):
        """Browse for folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
            
    def browse_rotate_folder(self):
        """Browse for rotation folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.rotate_folder_var.set(folder)
            
    def browse_interactive_folder(self):
        """Browse for interactive folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.interactive_folder_var.set(folder)
            
    def browse_alias_folder(self):
        """Browse for alias folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.alias_folder_var.set(folder)
            
    def organize_images(self):
        """Run folder organization"""
        folder = self.folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Organizing images...")
        
        def run_org():
            try:
                # Import and run folder sorter
                import folder_sorter
                self.log_message(f"Starting organization of: {folder}")
                folder_sorter.sort_images_by_name(folder)
                self.log_message("Organization complete!")
                messagebox.showinfo("Success", "Image organization completed!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Organization failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_org, daemon=True).start()
        
    def undo_organization(self):
        """Run undo organization"""
        folder = self.folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Undoing organization...")
        
        def run_undo():
            try:
                import undo_sort
                self.log_message(f"Starting undo of: {folder}")
                undo_sort.undo_sort(folder)
                self.log_message("Undo complete!")
                messagebox.showinfo("Success", "Undo completed!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Undo failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_undo, daemon=True).start()
        
    def clean_folders(self):
        """Clean empty folders"""
        folder = self.folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Cleaning empty folders...")
        
        def run_clean():
            try:
                import clean_empty_folders
                self.log_message(f"Cleaning empty folders in: {folder}")
                clean_empty_folders.remove_empty_folders(folder)
                self.log_message("Cleanup complete!")
                messagebox.showinfo("Success", "Empty folders cleaned!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Cleanup failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_clean, daemon=True).start()
        
    def fix_exif_rotation(self):
        """Fix EXIF rotation"""
        folder = self.rotate_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Fixing EXIF orientation...")
        
        def run_fix():
            try:
                import fix_image_orientation
                self.log_message(f"Fixing EXIF orientation in: {folder}")
                fix_image_orientation.fix_image_orientation(folder)
                self.log_message("EXIF fix complete!")
                messagebox.showinfo("Success", "EXIF orientation fixed!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"EXIF fix failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_fix, daemon=True).start()
        
    def fix_all_rotations(self):
        """Fix all rotations"""
        folder = self.rotate_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Fixing all rotations...")
        
        def run_fix():
            try:
                import fix_all_rotations
                self.log_message(f"Fixing all rotations in: {folder}")
                fix_all_rotations.detect_and_fix_rotation(folder, auto_fix=True)
                self.log_message("All rotations fixed!")
                messagebox.showinfo("Success", "All rotations fixed!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Rotation fix failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_fix, daemon=True).start()
        
    def start_interactive_review(self):
        """Start interactive review"""
        folder = self.interactive_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
            
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
            
        self.is_processing = True
        self.status_var.set("Starting interactive review...")
        
        def run_interactive():
            try:
                import interactive_rotation_cli
                self.log_message(f"Starting interactive review in: {folder}")
                messagebox.showinfo("Info", "Interactive review will start in a new window.\nFollow the instructions in the terminal.")
                interactive_rotation_cli.interactive_rotation_fix(folder)
                self.log_message("Interactive review complete!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Interactive review failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
                
        threading.Thread(target=run_interactive, daemon=True).start()
        
    def parse_missing_months(self, folder_name):
        """Extract missing months from folder name"""
        match = re.search(r"Missing (.*)", folder_name)
        if not match:
            return []
        
        nums = match.group(1).split(",")
        months = []
        for m in nums:
            m = m.strip()
            if m.isdigit():
                months.append(int(m))
        return months
    
    def preview_alias_changes(self):
        """Preview what will be renamed"""
        folder = self.alias_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
        
        station = self.station_var.get()
        station_code = self.station_code_var.get()
        year = int(self.year_var.get())
        obs_time = self.obs_time_var.get()
        
        if not station_code:
            messagebox.showerror("Error", "Please enter a station code (e.g., MOZ304A)")
            return
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview Station Aliases")
        preview_window.geometry("600x400")
        
        # Preview text
        preview_text = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD, width=70, height=20)
        preview_text.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Generate preview
        folder_path = Path(folder)
        missing_months = self.parse_missing_months(folder_path.name)
        
        preview_text.insert(tk.END, f"📁 Folder: {folder_path.name}\n")
        preview_text.insert(tk.END, f"🏢 Station: {station}\n")
        preview_text.insert(tk.END, f"🔖 Code: {station_code}\n")
        preview_text.insert(tk.END, f" Year: {year}\n")
        preview_text.insert(tk.END, f"⏰ Time: {obs_time}\n")
        
        if missing_months:
            preview_text.insert(tk.END, f"🚫 Missing months: {missing_months}\n")
        
        preview_text.insert(tk.END, f"\n📋 File-to-month mapping:\n")
        preview_text.insert(tk.END, "-" * 50 + "\n")
        
        # Get files and show mapping
        images = sorted(folder_path.glob("*.*"), key=lambda x: x.name.lower())
        file_to_month = {}
        
        for img_path in images:
            match = re.search(r'(\d+)', img_path.stem)
            if match:
                month_num = int(match.group(1))
                if 1 <= month_num <= 12:
                    file_to_month[img_path] = month_num
        
        for img_path, month in sorted(file_to_month.items(), key=lambda x: x[1]):
            days_in_month = calendar.monthrange(year, month)[1]
            new_name = f"{station}-{station_code}-{year}{month:02d}{days_in_month:02d}{obs_time}{img_path.suffix}"
            preview_text.insert(tk.END, f"{img_path.name:20s} → Month {month:02d} → {new_name}\n")
        
        preview_text.config(state='disabled')
        
        # Close button
        ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)
    
    def create_station_aliases(self):
        """Create station aliases"""
        folder = self.alias_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
        
        station = self.station_var.get()
        station_code = self.station_code_var.get()
        year = int(self.year_var.get())
        obs_time = self.obs_time_var.get()
        
        if not station_code:
            messagebox.showerror("Error", "Please enter a station code (e.g., MOZ304A)")
            return
        
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
        
        self.is_processing = True
        self.status_var.set("Creating station aliases...")
        
        def run_alias():
            try:
                # Import and run alias functionality
                import Alias
                self.log_message(f"Creating station aliases in: {folder}")
                self.log_message(f"Station: {station}, Code: {station_code}, Year: {year}, Time: {obs_time}")
                Alias.rename_images(folder, station, station_code, year, obs_time)
                self.log_message("Station aliases created!")
                messagebox.showinfo("Success", "Station aliases created successfully!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Station alias creation failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
        
        threading.Thread(target=run_alias, daemon=True).start()
    
    def restore_original_names(self):
        """Restore original names"""
        folder = self.alias_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
        
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
        
        self.is_processing = True
        self.status_var.set("Restoring original names...")
        
        def run_restore():
            try:
                import restore_original_names
                self.log_message(f"Restoring original names in: {folder}")
                restore_original_names.restore_original_names(folder)
                self.log_message("Original names restored!")
                messagebox.showinfo("Success", "Original names restored successfully!")
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Restore failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
        
        threading.Thread(target=run_restore, daemon=True).start()
    
    def browse_audio_folder(self):
        """Browse for audio folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.audio_folder_var.set(folder)
            
    def audio_callback(self, message):
        """Callback for audio orderer updates"""
        self.detected_numbers_var.set(message)
        self.log_message(f"🎤 {message}")
        self.root.update_idletasks()
    
    def start_audio_recording(self):
        """Start audio recording"""
        folder = self.audio_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
        
        try:
            import audio_image_order
            self.audio_orderer = audio_image_order.AudioImageOrder(folder, self.audio_callback)
            
            success, message = self.audio_orderer.start_recording()
            if success:
                self.audio_status_var.set("🔴 Recording... Speak month numbers")
                self.record_btn.config(state='disabled')
                self.stop_btn.config(state='normal')
                self.log_message(f"🎤 {message}")
            else:
                messagebox.showerror("Error", message)
                
        except ImportError:
            messagebox.showerror("Error", "Audio ordering module not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {e}")
    
    def stop_audio_recording(self):
        """Stop audio recording"""
        if not self.audio_orderer:
            return
        
        success, message = self.audio_orderer.stop_recording()
        
        self.audio_status_var.set("⏹️ Recording stopped")
        self.record_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        detected = self.audio_orderer.get_detected_numbers()
        self.detected_numbers_var.set(f"Detected: {detected}")
        
        self.log_message(f"🎤 {message}")
        self.log_message(f"📊 Detected numbers: {detected}")
    
    def clear_audio_detection(self):
        """Clear detected numbers"""
        self.detected_numbers_var.set("No numbers detected yet")
        self.audio_status_var.set("Ready to record")
        self.audio_orderer = None
        self.log_message("🔄 Audio detection cleared")
    
    def apply_audio_ordering(self):
        """Apply audio ordering to rename files"""
        if not self.audio_orderer:
            messagebox.showerror("Error", "No audio recording to apply")
            return
        
        station = self.audio_station_var.get()
        station_code = self.audio_station_code_var.get()
        year = int(self.audio_year_var.get())
        obs_time = self.audio_obs_time_var.get()
        
        if not station_code:
            messagebox.showerror("Error", "Please enter a station code (e.g., MOZ304A)")
            return
        
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
        
        self.is_processing = True
        self.status_var.set("Applying audio ordering...")
        
        def run_apply():
            try:
                success, result = self.audio_orderer.apply_ordering(station, station_code, year, obs_time)
                
                if success:
                    self.log_message("✅ Audio ordering applied successfully!")
                    for line in result:
                        self.log_message(f"  {line}")
                    messagebox.showinfo("Success", "Audio ordering applied successfully!")
                else:
                    self.log_message(f"❌ {result}")
                    messagebox.showerror("Error", result)
                    
            except Exception as e:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", f"Audio ordering failed: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
        
        threading.Thread(target=run_apply, daemon=True).start()
    
    def install_speech_recognition(self):
        """Install speech recognition packages"""
        self.status_var.set("Installing speech recognition...")
        
        def run_install():
            try:
                import subprocess
                import sys
                
                # Install packages
                packages = ["SpeechRecognition", "pyaudio"]
                for package in packages:
                    self.log_message(f"📦 Installing {package}...")
                    result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        self.log_message(f"✅ {package} installed successfully")
                    else:
                        self.log_message(f"❌ Failed to install {package}: {result.stderr}")
                
                self.log_message("🎤 Speech recognition installation complete!")
                messagebox.showinfo("Success", "Speech recognition installed successfully!")
                
            except Exception as e:
                self.log_message(f"❌ Installation failed: {e}")
                messagebox.showerror("Error", f"Installation failed: {e}")
            finally:
                self.status_var.set("Ready")
        
        threading.Thread(target=run_install, daemon=True).start()
    
    def browse_visual_folder(self):
        """Browse for visual folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.visual_folder_var.set(folder)
    
    def open_visual_selector(self):
        """Open visual number selector window"""
        folder = self.visual_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
        
        station = self.visual_station_var.get()
        station_code = self.visual_station_code_var.get()
        year = int(self.visual_year_var.get())
        obs_time = self.visual_obs_time_var.get()
        
        if not station_code:
            messagebox.showerror("Error", "Please enter a station code (e.g., MOZ304A)")
            return
        
        try:
            import visual_number_order
            
            def callback(results):
                self.log_message("✅ Visual ordering applied successfully!")
                for line in results:
                    self.log_message(f"  {line}")
                messagebox.showinfo("Success", "Visual ordering applied successfully!")
            
            orderer = visual_number_order.VisualNumberOrder(folder, station, station_code, year, obs_time)
            orderer.create_selection_window(callback)
            
            self.log_message(f"🔢 Visual selector opened for {folder}")
            
        except ImportError:
            messagebox.showerror("Error", "Visual ordering module not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open visual selector: {e}")
    
    def browse_simple_folder(self):
        """Browse for simple rename folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.simple_folder_var.set(folder)
    
    def open_month_selector(self):
        """Open month selector window with cropped previews"""
        try:
            import month_selector
            month_selector.open_month_selector(self.root)
            self.log_message("🖼️ Month selector opened")
        except ImportError:
            messagebox.showerror("Error", "Month selector module not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open month selector: {e}")
    
    def simple_rename_images(self):
        """Rename images sequentially as 1.jpg, 2.jpg, etc."""
        folder = self.simple_folder_var.get()
        if not folder or not Path(folder).exists():
            messagebox.showerror("Error", "Please select a valid folder")
            return
        
        if self.is_processing:
            messagebox.showwarning("Warning", "Another operation is in progress")
            return
        
        self.is_processing = True
        self.status_var.set("Renaming images...")
        
        def run_rename():
            try:
                folder_path = Path(folder)
                
                # Get all image files sorted alphabetically
                images = sorted(folder_path.glob("*.*"), key=lambda x: x.name.lower())
                
                # Filter to only image files
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
                images = [img for img in images if img.suffix.lower() in image_extensions]
                
                if not images:
                    self.log_message("❌ No images found in folder")
                    messagebox.showerror("Error", "No images found in the selected folder")
                    return
                
                self.log_message(f"📁 Renaming {len(images)} images in: {folder}")
                
                # Rename images sequentially
                renamed_count = 0
                for i, img_path in enumerate(images, start=1):
                    new_name = f"{i}{img_path.suffix}"
                    new_path = folder_path / new_name
                    
                    # Skip if already has the correct name
                    if img_path.name == new_name:
                        self.log_message(f"  ✓ {img_path.name} (already correct)")
                        continue
                    
                    # Handle name conflicts by using temp names
                    if new_path.exists():
                        temp_name = f"temp_{i}_{img_path.name}"
                        temp_path = folder_path / temp_name
                        img_path.rename(temp_path)
                        img_path = temp_path
                    
                    img_path.rename(new_path)
                    self.log_message(f"  {img_path.name} → {new_name}")
                    renamed_count += 1
                
                self.log_message(f"✅ Successfully renamed {renamed_count} images!")
                messagebox.showinfo("Success", f"Renamed {renamed_count} images to sequential numbers (1-{len(images)})")
                
            except Exception as e:
                self.log_message(f"❌ Error: {e}")
                messagebox.showerror("Error", f"Failed to rename images: {e}")
            finally:
                self.is_processing = False
                self.status_var.set("Ready")
        
        threading.Thread(target=run_rename, daemon=True).start()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = ImageOrganizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
