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
        
        # Tab 5: Settings
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
        main_frame = ttk.Frame(self.alias_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="🏷️ Station Alias", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame, text="Select Folder", padding="10")
        folder_frame.pack(fill='x', pady=(0, 20))
        
        self.alias_folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.alias_folder_var, width=70)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_alias_folder)
        browse_btn.pack(side='right')
        
        # Configuration
        config_frame = ttk.LabelFrame(main_frame, text="Station Configuration", padding="10")
        config_frame.pack(fill='x', pady=(0, 20))
        
        # Station dropdown
        station_frame = ttk.Frame(config_frame)
        station_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(station_frame, text="Station Code:").pack(side='left', padx=(0, 10))
        self.station_var = tk.StringVar()
        station_combo = ttk.Combobox(station_frame, textvariable=self.station_var, values=STATION_CODES, width=20)
        station_combo.pack(side='left', padx=(0, 10))
        if STATION_CODES:
            station_combo.current(0)
        
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
        ops_frame = ttk.LabelFrame(main_frame, text="Operations", padding="10")
        ops_frame.pack(fill='x', pady=(0, 20))
        
        btn_frame = ttk.Frame(ops_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="🏷️ Create Station Aliases", command=self.create_station_aliases).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔍 Preview Changes", command=self.preview_alias_changes).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="↩️ Restore Original Names", command=self.restore_original_names).pack(side='left', padx=5)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
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
        
        info_label = ttk.Label(info_frame, text=info_text.strip(), justify='left')
        info_label.pack()
        
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
        year = int(self.year_var.get())
        obs_time = self.obs_time_var.get()
        
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
        preview_text.insert(tk.END, f"📅 Year: {year}\n")
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
            new_name = f"{station}-{year}{month:02d}{days_in_month:02d}{obs_time}{img_path.suffix}"
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
        year = int(self.year_var.get())
        obs_time = self.obs_time_var.get()
        
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
                self.log_message(f"Station: {station}, Year: {year}, Time: {obs_time}")
                Alias.rename_images(folder, station, year, obs_time)
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

def main():
    """Main entry point"""
    root = tk.Tk()
    app = ImageOrganizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
