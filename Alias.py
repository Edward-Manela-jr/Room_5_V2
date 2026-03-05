import os
import sys
from pathlib import Path
import calendar
import re

# Force UTF-8 output for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def parse_missing_months(folder_name):
    """
    Extract missing months from folder name.
    Example: "MANSA 2011 Missing 01,07,11"
    Returns: [1, 7, 11]
    """
    match = re.search(r"Missing\s*(\d+(?:,\d+)*)", folder_name, re.IGNORECASE)
    if not match:
        return []  # No missing months stated
    
    nums = match.group(1).split(",")
    months = []
    for m in nums:
        m = m.strip()
        if m.isdigit() and 1 <= int(m) <= 12:
            months.append(int(m))
    return months

def rename_images(folder, station, station_code, year, obs_time):
    """
    Rename images based on their POSITION in the folder (not filename).
    - 1st image = January (month 1)
    - 2nd image = February (month 2)
    - etc.
    
    This assumes a human has already arranged the images in correct order.
    """
    folder = Path(folder)
    
    # Detect missing months
    missing_months = parse_missing_months(folder.name)
    if missing_months:
        print(f"🚫 Detected missing months: {missing_months}")
    
    # Get all image files, sorted by name (human-ordered)
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'}
    images = sorted([f for f in folder.iterdir() if f.suffix.lower() in image_extensions], 
                    key=lambda x: x.name.lower())
    
    if not images:
        print("⚠️  No image files found in folder!")
        return
    
    print(f"📋 Found {len(images)} images. Processing by position...")
    
    # Build list of months to process (skip missing months)
    all_months = list(range(1, 13))  # 1-12
    months_to_process = [m for m in all_months if m not in missing_months]
    
    print(f"📋 Months to rename: {months_to_process}")
    
    # Process each image by position
    station_id = station_code if station_code else station
    
    for idx, img_path in enumerate(images):
        if idx >= len(months_to_process):
            print(f"⚠️  More images than months to process. Stopping at month {months_to_process[-1]}")
            break
        
        month = months_to_process[idx]
        days_in_month = calendar.monthrange(year, month)[1]
        suffix = img_path.suffix
        
        # Build final name: STATIONNAME-STATIONCODE-YYYYMMDDHH.ext
        new_name = f"{station}-{station_id}-{year}{month:02d}{days_in_month:02d}{obs_time}{suffix}"
        new_path = folder / new_name
        
        # Handle filename conflicts
        counter = 1
        while new_path.exists() and new_path != img_path:
            new_name = f"{station_id}-{year}{month:02d}{days_in_month:02d}{obs_time}_{counter}{suffix}"
            new_path = folder / new_name
            counter += 1
        
        img_path.rename(new_path)
        print(f"  Position {idx+1} → Month {month:02d}: {img_path.name:30s} → {new_name}")

    print("\n✅ DONE — Images renamed successfully by position!")

def main():
    if len(sys.argv) >= 5:
        # Command line mode
        folder = sys.argv[1]
        station = sys.argv[2]
        station_code = sys.argv[3]
        year = int(sys.argv[4])
        obs_time = sys.argv[5] if len(sys.argv) > 5 else "06"
    else:
        # Interactive mode
        folder = input("Enter folder path: ").strip()
        station = input("Enter station name: ").strip()
        station_code = input("Enter station code (e.g., MOZ304A): ").strip()
        year = int(input("Enter year: ").strip())
        obs_time = input("Enter observation time (HHMM, default 06): ").strip() or "06"
    
    # Remove quotes if user added them
    if folder.startswith('"') and folder.endswith('"'):
        folder = folder[1:-1]
    elif folder.startswith("'") and folder.endswith("'"):
        folder = folder[1:-1]
    
    print(f"\n🔄 Processing (Position-based renaming):")
    print(f"📁 Folder: {folder}")
    print(f"🏢 Station: {station}")
    print(f"📋 Station Code: {station_code}")
    print(f"📅 Year: {year}")
    print(f"⏰ Time: {obs_time}")
    print()
    
    rename_images(folder, station, station_code, year, obs_time)

if __name__ == "__main__":
    main()
