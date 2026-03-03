#!/usr/bin/env python3
"""
Month Selector - Visual Month Selection with Cropped Image Previews
Browse images, view cropped previews, and select month numbers to rename files
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from pathlib import Path
import os
import shutil
import datetime
import calendar


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

# Years for dropdown (1900-2026)
YEARS = list(range(1900, 2027))

# Observation times for dropdown
OBSERVATION_TIMES = ["06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18"]


class MonthSelector:
    def __init__(self, parent, station="", station_code="", year="", obs_time="06"):
        self.parent = parent
        self.folder_path = None
        self.image_files = []
        self.current_index = 0
        self.selected_months = {}  # {index: month_number}
        self.photo_images = []  # Keep references to prevent garbage collection
        
        # Zoom factor (0.5x to 3.0x)
        self.zoom_factor = 1.0
        
        # Station configuration
        self.station = station
        self.station_code = station_code
        self.year = year
        self.obs_time = obs_time
        
        self.create_window()
    
    def create_window(self):
        """Create the month selector window"""
        self.window = tk.Toplevel()
        self.window.title("Month Selector - Cropped Previews")
        self.window.geometry("900x750")
        self.window.minsize(800, 600)
        
        # Configure grid weights for resizing
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        
        # Create main frames
        self.create_header()
        self.create_image_view()
        self.create_controls()
        self.create_month_buttons()
        self.create_status_bar()
        
        # Initially disable controls until folder is selected
        self.set_controls_state('disabled')
    
    def create_header(self):
        """Create header with folder selection and station config"""
        header_frame = tk.Frame(self.window, bg='#2c3e50', pady=10)
        header_frame.grid(row=0, column=0, sticky='ew')
        header_frame.columnconfigure(1, weight=1)
        
        # Row 0: Folder selection
        tk.Label(header_frame, text="📁 Folder:", bg='#2c3e50', fg='white', 
                font=('Arial', 11)).grid(row=0, column=0, padx=10, sticky='w')
        
        self.folder_label = tk.Label(header_frame, text="No folder selected", 
                                    bg='#2c3e50', fg='#bdc3c7', font=('Arial', 10),
                                    anchor='w')
        self.folder_label.grid(row=0, column=1, padx=10, sticky='ew')
        
        self.browse_btn = tk.Button(header_frame, text="Browse", 
                                   command=self.browse_folder,
                                   font=('Arial', 10), bg='#3498db', fg='white',
                                   relief='flat', padx=15)
        self.browse_btn.grid(row=0, column=2, padx=10)
        
        # Row 1: Station Configuration
        config_frame = tk.Frame(header_frame, bg='#2c3e50')
        config_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky='ew')
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)
        config_frame.columnconfigure(5, weight=1)
        
        # Station Name
        tk.Label(config_frame, text="Station:", bg='#2c3e50', fg='white', 
                font=('Arial', 10)).grid(row=0, column=0, padx=10, sticky='w')
        self.station_var = tk.StringVar(value=self.station)
        station_combo = ttk.Combobox(config_frame, textvariable=self.station_var, 
                                      values=STATION_CODES, width=15, state='readonly')
        station_combo.grid(row=0, column=1, padx=10, sticky='w')
        if STATION_CODES:
            station_combo.current(0)
        
        # Station Code
        tk.Label(config_frame, text="Code:", bg='#2c3e50', fg='white', 
                font=('Arial', 10)).grid(row=0, column=2, padx=10, sticky='w')
        self.station_code_var = tk.StringVar(value=self.station_code)
        code_combo = ttk.Combobox(config_frame, textvariable=self.station_code_var, 
                                  values=STATION_CODE_ALIASES, width=12, state='readonly')
        code_combo.grid(row=0, column=3, padx=10, sticky='w')
        if STATION_CODE_ALIASES:
            code_combo.current(0)
        
        # Year
        tk.Label(config_frame, text="Year:", bg='#2c3e50', fg='white', 
                font=('Arial', 10)).grid(row=0, column=4, padx=10, sticky='w')
        self.year_var = tk.StringVar(value=self.year)
        year_combo = ttk.Combobox(config_frame, textvariable=self.year_var, 
                                  values=YEARS, width=6, state='readonly')
        year_combo.grid(row=0, column=5, padx=10, sticky='w')
        current_year = datetime.datetime.now().year
        if current_year in YEARS:
            year_combo.set(str(current_year))
        
        # Observation Time
        tk.Label(config_frame, text="Time:", bg='#2c3e50', fg='white', 
                font=('Arial', 10)).grid(row=0, column=6, padx=10, sticky='w')
        self.obs_time_var = tk.StringVar(value=self.obs_time)
        time_combo = ttk.Combobox(config_frame, textvariable=self.obs_time_var, 
                                   values=OBSERVATION_TIMES, width=4, state='readonly')
        time_combo.grid(row=0, column=7, padx=10, sticky='w')
        time_combo.set("06")
    
    def create_image_view(self):
        """Create image preview area with cropped view"""
        # Main container
        container = tk.Frame(self.window, bg='#ecf0f1')
        container.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Canvas for image with scrollbar
        self.canvas_frame = tk.Frame(container, bg='#34495e', relief='sunken', bd=2)
        self.canvas_frame.grid(row=0, column=0, sticky='nsew')
        
        # Canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg='#2c3e50', highlightthickness=0)
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Vertical scrollbar
        v_scrollbar = tk.Scrollbar(self.canvas_frame, orient='vertical', 
                                   command=self.canvas.yview)
        v_scrollbar.pack(side='right', fill='y')
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Frame inside canvas for image
        self.image_container = tk.Frame(self.canvas, bg='#2c3e50')
        self.canvas_window = self.canvas.create_window(0, 0, window=self.image_container, 
                                                         anchor='nw')
        
        # Bind mousewheel
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Configure scrolling
        self.image_container.bind("<Configure>", 
                                   lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Image display label
        self.image_label = tk.Label(self.image_container, bg='#2c3e50', 
                                     text="Select a folder to preview images",
                                     fg='#95a5a6', font=('Arial', 14))
        self.image_label.pack(pady=50)
        
        # Image counter
        self.counter_label = tk.Label(container, text="", bg='#ecf0f1', 
                                       fg='#2c3e50', font=('Arial', 11, 'bold'))
        self.counter_label.grid(row=1, column=0, pady=5)
    
    def create_controls(self):
        """Create navigation controls"""
        control_frame = tk.Frame(self.window, bg='#ecf0f1', pady=10)
        control_frame.grid(row=2, column=0, sticky='ew')
        
        # Navigation buttons
        nav_frame = tk.Frame(control_frame, bg='#ecf0f1')
        nav_frame.pack()
        
        self.prev_btn = tk.Button(nav_frame, text="◀ Previous", command=self.prev_image,
                                  font=('Arial', 11), bg='#95a5a6', fg='white',
                                  relief='flat', padx=20, pady=5)
        self.prev_btn.pack(side='left', padx=5)
        
        self.next_btn = tk.Button(nav_frame, text="Next ▶", command=self.next_image,
                                  font=('Arial', 11), bg='#95a5a6', fg='white',
                                  relief='flat', padx=20, pady=5)
        self.next_btn.pack(side='left', padx=5)
        
        # Jump to
        tk.Label(nav_frame, text=" Jump to:", bg='#ecf0f1', 
                font=('Arial', 10)).pack(side='left', padx=(20, 5))
        
        self.jump_entry = tk.Entry(nav_frame, width=6, font=('Arial', 10))
        self.jump_entry.pack(side='left', padx=5)
        self.jump_entry.bind('<Return>', lambda e: self.jump_to_image())
        
        tk.Button(nav_frame, text="Go", command=self.jump_to_image,
                 font=('Arial', 10), bg='#3498db', fg='white',
                 relief='flat', padx=10).pack(side='left')
        
        # Zoom slider
        zoom_frame = tk.Frame(control_frame, bg='#ecf0f1')
        zoom_frame.pack(pady=(10, 0))
        
        tk.Label(zoom_frame, text="🔍 Zoom:", bg='#ecf0f1', 
                font=('Arial', 10)).pack(side='left', padx=(0, 10))
        
        self.zoom_slider = tk.Scale(zoom_frame, from_=0.5, to=3.0, resolution=0.1,
                                     orient='horizontal', length=200,
                                     command=self.on_zoom_changed,
                                     bg='#ecf0f1', troughcolor='#bdc3c7',
                                     activebackground='#3498db', font=('Arial', 9))
        self.zoom_slider.set(1.0)
        self.zoom_slider.pack(side='left')
        
        self.zoom_label = tk.Label(zoom_frame, text="1.0x", bg='#ecf0f1',
                                   fg='#2c3e50', font=('Arial', 10, 'bold'), width=5)
        self.zoom_label.pack(side='left', padx=10)
    
    def on_zoom_changed(self, value):
        """Handle zoom slider changes"""
        self.zoom_factor = float(value)
        self.zoom_label.config(text=f"{self.zoom_factor:.1f}x")
        # Refresh the image with new zoom level
        if self.image_files and self.current_index < len(self.image_files):
            self.show_image()
    
    def create_month_buttons(self):
        """Create month selection buttons (1-12)"""
        month_frame = tk.Frame(self.window, bg='#ecf0f1', pady=10)
        month_frame.grid(row=3, column=0, sticky='ew', padx=20)
        
        # Title
        tk.Label(month_frame, text="Select Month for Current Image:", 
                bg='#ecf0f1', fg='#2c3e50', font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Month buttons frame
        buttons_container = tk.Frame(month_frame, bg='#ecf0f1')
        buttons_container.pack()
        
        # Month names for display
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Create 4x3 grid of month buttons
        self.month_buttons = {}
        for i in range(1, 13):
            row = (i - 1) // 4
            col = (i - 1) % 4
            
            btn = tk.Button(buttons_container, 
                           text=f"{i}\n{month_names[i-1]}",
                           font=('Arial', 11, 'bold'),
                           bg='#27ae60', fg='white',
                           relief='raised',
                           padx=15, pady=8,
                           command=lambda m=i: self.select_month(m))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            self.month_buttons[i] = btn
        
        # Selected months info
        self.selection_info = tk.Label(month_frame, text="", 
                                       bg='#ecf0f1', fg='#e74c3c', 
                                       font=('Arial', 10, 'bold'))
        self.selection_info.pack(pady=10)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.window, bg='#34495e', pady=8)
        status_frame.grid(row=4, column=0, sticky='ew')
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                     bg='#34495e', fg='white', 
                                     font=('Arial', 10), anchor='w')
        self.status_label.pack(side='left', padx=10)
        
        # Apply and Clear buttons
        btn_frame = tk.Frame(status_frame, bg='#34495e')
        btn_frame.pack(side='right', padx=10)
        
        self.clear_btn = tk.Button(btn_frame, text="Clear All", 
                                   command=self.clear_selections,
                                   font=('Arial', 10), bg='#e74c3c', fg='white',
                                   relief='flat', padx=15)
        self.clear_btn.pack(side='left', padx=5)
        
        self.apply_btn = tk.Button(btn_frame, text="Apply & Rename", 
                                   command=self.apply_rename,
                                   font=('Arial', 10, 'bold'), bg='#27ae60', fg='white',
                                   relief='flat', padx=15)
        self.apply_btn.pack(side='left', padx=5)
    
    def browse_folder(self):
        """Browse for folder with images"""
        folder = filedialog.askdirectory(title="Select Folder with Images")
        if folder:
            self.folder_path = Path(folder)
            self.load_images()
    
    def load_images(self):
        """Load images from selected folder"""
        self.image_files = []
        self.selected_months = {}
        self.photo_images = []
        self.current_index = 0
        
        # Supported image extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
        # Get all image files
        for file in sorted(self.folder_path.iterdir()):
            if file.is_file() and file.suffix.lower() in image_extensions:
                self.image_files.append(file)
        
        if not self.image_files:
            messagebox.showinfo("No Images", "No image files found in the selected folder.")
            self.folder_label.config(text="No folder selected")
            self.folder_path = None
            return
        
        # Update UI
        self.folder_label.config(text=str(self.folder_path))
        self.set_controls_state('normal')
        self.show_image()
        self.update_counter()
        self.status_label.config(text=f"Loaded {len(self.image_files)} images")
    
    def set_controls_state(self, state):
        """Enable or disable controls"""
        self.prev_btn.config(state=state, bg='#95a5a6' if state == 'disabled' else '#3498db')
        self.next_btn.config(state=state, bg='#95a5a6' if state == 'disabled' else '#3498db')
        self.jump_entry.config(state=state)
        
        if state == 'disabled':
            for btn in self.month_buttons.values():
                btn.config(state='disabled', bg='#7f8c8d')
            self.clear_btn.config(state='disabled', bg='#7f8c8d')
            self.apply_btn.config(state='disabled', bg='#7f8c8d')
        else:
            for btn in self.month_buttons.values():
                btn.config(state='normal', bg='#27ae60')
            self.clear_btn.config(state='normal', bg='#e74c3c')
            self.apply_btn.config(state='normal', bg='#27ae60')
    
    def crop_top_left_half(self, image_path, target_size=(400, 300)):
        """Crop the top-left half of an image with EXIF orientation handling"""
        try:
            from PIL import ExifTags
            
            with Image.open(image_path) as img:
                # Handle EXIF orientation
                try:
                    exif = img.getexif()
                    if exif:
                        for tag, value in exif.items():
                            if ExifTags.TAGS.get(tag) == 'Orientation':
                                if value == 3:
                                    img = img.rotate(180, expand=True)
                                elif value == 6:
                                    img = img.rotate(270, expand=True)
                                elif value == 8:
                                    img = img.rotate(90, expand=True)
                                break
                except Exception:
                    pass  # Ignore EXIF errors
                
                # Get original dimensions
                width, height = img.size
                
                # Calculate crop area (top-left half)
                crop_width = width // 2
                crop_height = height // 2
                
                # Crop the image
                cropped = img.crop((0, 0, crop_width, crop_height))
                
                # Resize for display
                cropped.thumbnail(target_size, Image.Resampling.LANCZOS)
                
                return cropped
        except Exception as e:
            print(f"Error cropping image: {e}")
            return None
    
    def show_image(self):
        """Display the current image with cropped preview and zoom"""
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        # Clear previous image
        for widget in self.image_container.winfo_children():
            widget.destroy()
        
        # Get current image
        image_path = self.image_files[self.current_index]
        
        # Create cropped preview
        cropped_img = self.crop_top_left_half(image_path)
        
        if cropped_img:
            # Apply zoom factor - resize the cropped image
            if self.zoom_factor != 1.0:
                new_width = int(cropped_img.width * self.zoom_factor)
                new_height = int(cropped_img.height * self.zoom_factor)
                cropped_img = cropped_img.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage
            self.current_photo = ImageTk.PhotoImage(cropped_img)
            self.photo_images.append(self.current_photo)  # Keep reference
            
            # Display on canvas
            img_label = tk.Label(self.image_container, image=self.current_photo, 
                                bg='#2c3e50')
            img_label.pack(pady=10)
            
            # Filename label
            filename_label = tk.Label(self.image_container, 
                                     text=f"📄 {image_path.name}",
                                     bg='#2c3e50', fg='white', 
                                     font=('Arial', 10))
            filename_label.pack(pady=5)
            
            # Update month button states based on current selection
            self.update_month_buttons()
        else:
            # Show error placeholder
            error_label = tk.Label(self.image_container, 
                                 text="❌ Could not load image",
                                 bg='#2c3e50', fg='#e74c3c', 
                                 font=('Arial', 12))
            error_label.pack(pady=50)
        
        # Update canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)  # Scroll to top
    
    def update_month_buttons(self):
        """Update month button appearance based on selection"""
        current_month = self.selected_months.get(self.current_index)
        
        for month, btn in self.month_buttons.items():
            if month == current_month:
                btn.config(bg='#e74c3c', relief='sunken')  # Selected - red
            else:
                btn.config(bg='#27ae60', relief='raised')  # Not selected - green
        
        # Update selection info
        if current_month:
            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                         'July', 'August', 'September', 'October', 'November', 'December']
            self.selection_info.config(
                text=f"Image {self.current_index + 1}: Selected Month {month_names[current_month]}")
        else:
            self.selection_info.config(text=f"Image {self.current_index + 1}: No month selected")
    
    def update_counter(self):
        """Update image counter label"""
        if self.image_files:
            self.counter_label.config(
                text=f"Image {self.current_index + 1} of {len(self.image_files)} | "
                     f"Selected: {len(self.selected_months)}/{len(self.image_files)}")
        else:
            self.counter_label.config(text="")
    
    def prev_image(self):
        """Show previous image"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()
            self.update_counter()
    
    def next_image(self):
        """Show next image"""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.show_image()
            self.update_counter()
    
    def jump_to_image(self):
        """Jump to specific image number"""
        try:
            num = int(self.jump_entry.get())
            if 1 <= num <= len(self.image_files):
                self.current_index = num - 1
                self.show_image()
                self.update_counter()
                self.jump_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Invalid Number", 
                                      f"Please enter a number between 1 and {len(self.image_files)}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number")
    
    def select_month(self, month):
        """Select month for current image"""
        if not self.image_files:
            return
        
        # Toggle: if already selected, deselect
        if self.selected_months.get(self.current_index) == month:
            del self.selected_months[self.current_index]
        else:
            self.selected_months[self.current_index] = month
        
        self.update_month_buttons()
        self.update_counter()
    
    def clear_selections(self):
        """Clear all month selections"""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all month selections?"):
            self.selected_months = {}
            self.show_image()
            self.update_counter()
            self.status_label.config(text="All selections cleared")
    
    def apply_rename(self):
        """Apply month-based renaming to files"""
        if not self.selected_months:
            messagebox.showwarning("No Selections", "Please select months for at least one image.")
            return
        
        # Get current configuration from UI
        station = self.station_var.get()
        station_code = self.station_code_var.get()
        year = self.year_var.get()
        obs_time = self.obs_time_var.get()
        
        if not station_code:
            messagebox.showwarning("Missing Configuration", "Please select a station code.")
            return
        
        if not year:
            messagebox.showwarning("Missing Configuration", "Please select a year.")
            return
        
        # Confirm rename
        count = len(self.selected_months)
        # Calculate actual days in month for the example
        first_month = self.selected_months[sorted(self.selected_months.keys())[0]]
        year_int = int(year)
        days_in_first_month = calendar.monthrange(year_int, first_month)[1]
        filename_example = f"{station}-{station_code}-{year}{first_month:02d}{days_in_first_month:02d}{obs_time}.ext" if self.selected_months else "STATION-STATIONCODE-YEARMONTHDAY TIME.ext"
        if not messagebox.askyesno("Confirm Rename", 
                                   f"Rename {count} file(s)?\n\nExample: {filename_example}"):
            return
        
        renamed = 0
        errors = []
        
        # Sort by image index to rename in order
        for img_index in sorted(self.selected_months.keys()):
            month = self.selected_months[img_index]
            img_path = self.image_files[img_index]
            
            try:
                # Get file extension
                ext = img_path.suffix
                
                # Calculate actual days in the selected month
                year_int = int(year)
                days_in_month = calendar.monthrange(year_int, month)[1]
                
                # Create new filename with full format: STATION-STATIONCODE-YEARMONTHDAY TIME.ext
                # Example: CHIPAT01-MOZ304A-2026013106.jpg (31 days in January)
                new_name = f"{station}-{station_code}-{year}{month:02d}{days_in_month:02d}{obs_time}{ext}"
                new_path = img_path.parent / new_name
                
                # Handle existing files
                counter = 1
                while new_path.exists() and new_path != img_path:
                    new_name = f"{station}-{station_code}-{year}{month:02d}{days_in_month:02d}{obs_time}_{counter}{ext}"
                    new_path = img_path.parent / new_name
                    counter += 1
                
                # Rename the file
                shutil.move(str(img_path), str(new_path))
                renamed += 1
                
            except Exception as e:
                errors.append(f"{img_path.name}: {str(e)}")
        
        # Show results
        if errors:
            error_msg = f"Renamed {renamed} files with {len(errors)} errors:\n\n"
            error_msg += "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... and {len(errors) - 10} more"
            messagebox.showwarning("Rename Complete with Errors", error_msg)
        else:
            messagebox.showinfo("Success", f"Successfully renamed {renamed} files!\n\nFormat: {station}-{station_code}-{year}MMDD{obs_time}.ext")
        
        # Reload images
        self.status_label.config(text=f"Renamed {renamed} files")
        self.load_images()


def open_month_selector(parent, station="", station_code="", year="", obs_time="06"):
    """Open the month selector window"""
    selector = MonthSelector(parent, station, station_code, year, obs_time)
    return selector.window
