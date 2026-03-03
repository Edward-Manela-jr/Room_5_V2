import os
import sys
from pathlib import Path
import calendar
import re

def parse_missing_months(folder_name):
    """
    Extract missing months from folder name.
    Example: "MANSA 2011 Missing 01,07,11"
    Returns: [1, 7, 11]
    """
    match = re.search(r"Missing (.*)", folder_name)
    if not match:
        return []  # No missing months stated
    
    nums = match.group(1).split(",")
    months = []
    for m in nums:
        m = m.strip()
        if m.isdigit():
            months.append(int(m))
    return months

def rename_images(folder, station, station_code, year, obs_time):
    folder = Path(folder)

    # Detect missing months
    missing_months = parse_missing_months(folder.name)

    if missing_months:
        print(f"🚫 Detected missing months: {missing_months}")
    
    # Get available image files and extract month numbers from filenames
    images = sorted(folder.glob("*.*"), key=lambda x: x.name.lower())
    
    # Extract month numbers from filenames (1.jpg = month 1, 2.jpg = month 2, etc.)
    file_to_month = {}
    for img_path in images:
        # Extract number from filename like "1.jpg", "2.jpg", "10.jpg", "11.jpg"
        match = re.search(r'(\d+)', img_path.stem)
        if match:
            month_num = int(match.group(1))
            if 1 <= month_num <= 12:
                file_to_month[img_path] = month_num
            else:
                print(f"⚠️  Invalid month number in filename: {img_path.name}")
        else:
            print(f"⚠️  Could not extract month from: {img_path.name}")
    
    print(f"📋 File-to-month mapping:")
    for img_path, month in file_to_month.items():
        print(f"  {img_path.name:15s} → Month {month:02d}")

    # Process files using the mapping
    for img_path, month in file_to_month.items():
        days_in_month = calendar.monthrange(year, month)[1]
        suffix = img_path.suffix

        # Build final name (use station code like MOZ304A if provided, otherwise use station)
        station_id = station_code if station_code else station
        new_name = f"{station_id}-{year}{month:02d}{days_in_month:02d}{obs_time}{suffix}"
        new_path = folder / new_name

        img_path.rename(new_path)
        print(f"Month {month:2d}: {img_path.name:15s} → {new_name}")

    print("\n✅ DONE — Images renamed successfully!")

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
        obs_time = input("Enter observation time (HH, default 06): ").strip() or "06"
    
    # Remove quotes if user added them
    if folder.startswith('"') and folder.endswith('"'):
        folder = folder[1:-1]
    elif folder.startswith("'") and folder.endswith("'"):
        folder = folder[1:-1]
    
    print(f"\n🔄 Processing:")
    print(f"📁 Folder: {folder}")
    print(f"🏢 Station: {station}")
    print(f"📅 Year: {year}")
    print(f"⏰ Time: {obs_time}")
    print()
    
    rename_images(folder, station, year, obs_time)

if __name__ == "__main__":
    main()
