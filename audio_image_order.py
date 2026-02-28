#!/usr/bin/env python3
"""
Audio-based Image Ordering System
Uses speech recognition to order images by month numbers
"""

import os
import sys
import threading
import queue
import time
from pathlib import Path
import re

# Try to import speech recognition
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("⚠️  Speech recognition not available. Install with: pip install SpeechRecognition")

class AudioImageOrder:
    def __init__(self, folder_path, callback=None):
        self.folder_path = Path(folder_path)
        self.callback = callback
        self.is_recording = False
        self.recognizer = sr.Recognizer() if SPEECH_AVAILABLE else None
        self.microphone = sr.Microphone() if SPEECH_AVAILABLE else None
        self.audio_queue = queue.Queue()
        self.detected_numbers = []
        self.recording_thread = None
        
    def start_recording(self):
        """Start audio recording for image ordering"""
        if not SPEECH_AVAILABLE:
            return False, "Speech recognition not available"
            
        if self.is_recording:
            return False, "Already recording"
            
        self.is_recording = True
        self.detected_numbers = []
        
        # Start recording in separate thread
        self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.recording_thread.start()
        
        return True, "Recording started"
    
    def stop_recording(self):
        """Stop audio recording"""
        if not self.is_recording:
            return False, "Not recording"
            
        self.is_recording = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=2)
            
        return True, f"Recording stopped. Detected numbers: {self.detected_numbers}"
    
    def _record_audio(self):
        """Record audio and process speech recognition"""
        if not self.microphone or not self.recognizer:
            return
            
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
        while self.is_recording:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                # Try to recognize speech
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    # Extract numbers from speech
                    numbers = self._extract_numbers(text)
                    
                    for num in numbers:
                        if 1 <= num <= 12 and num not in self.detected_numbers:
                            self.detected_numbers.append(num)
                            if self.callback:
                                self.callback(f"Detected: {num}")
                            
                except sr.UnknownValueError:
                    # Speech not understood, continue
                    pass
                except sr.RequestError:
                    # API error, continue
                    pass
                    
            except sr.WaitTimeoutError:
                # No speech detected, continue
                continue
            except Exception as e:
                if self.callback:
                    self.callback(f"Error: {e}")
                break
                
            time.sleep(0.1)  # Small delay to prevent CPU overload
    
    def _extract_numbers(self, text):
        """Extract month numbers from speech text"""
        # Handle various ways people might say numbers
        number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12
        }
        
        numbers = []
        
        # First check for word numbers
        for word, num in number_words.items():
            if word in text:
                numbers.append(num)
        
        # Then check for digit numbers
        digit_matches = re.findall(r'\b(1[0-2]|[1-9])\b', text)
        for match in digit_matches:
            num = int(match)
            if 1 <= num <= 12:
                numbers.append(num)
        
        return numbers
    
    def get_detected_numbers(self):
        """Get the list of detected month numbers"""
        return sorted(self.detected_numbers)
    
    def apply_ordering(self, station, year, obs_time="06"):
        """Apply the detected ordering to rename images"""
        if not self.detected_numbers:
            return False, "No numbers detected"
        
        folder = self.folder_path
        images = sorted(folder.glob("*.*"), key=lambda x: x.name.lower())
        
        if len(images) != len(self.detected_numbers):
            return False, f"Mismatch: {len(images)} images vs {len(self.detected_numbers)} detected numbers"
        
        results = []
        
        for img_path, month in zip(images, self.detected_numbers):
            # Build new name
            new_name = f"{station}-{year}{month:02d}{calendar.monthrange(year, month)[1]:02d}{obs_time}{img_path.suffix}"
            new_path = folder / new_name
            
            # Rename file
            try:
                img_path.rename(new_path)
                results.append(f"{img_path.name} → {new_name}")
            except Exception as e:
                results.append(f"Error renaming {img_path.name}: {e}")
        
        return True, results

def install_speech_recognition():
    """Install speech recognition package"""
    import subprocess
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "SpeechRecognition"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "pyaudio"], check=True)
        return True, "Speech recognition installed successfully"
    except subprocess.CalledProcessError as e:
        return False, f"Installation failed: {e}"

def main():
    """Command line interface for testing"""
    if len(sys.argv) < 2:
        print("Usage: python audio_image_order.py <folder_path>")
        return
    
    folder_path = sys.argv[1]
    
    if not SPEECH_AVAILABLE:
        print("🎤 Speech recognition not available.")
        print("Install with: pip install SpeechRecognition pyaudio")
        return
    
    def callback(message):
        print(f"🎤 {message}")
    
    orderer = AudioImageOrder(folder_path, callback)
    
    print("🎤 Audio Image Ordering System")
    print(f"📁 Folder: {folder_path}")
    print("📋 Instructions:")
    print("1. Click Start Recording")
    print("2. Say month numbers as you swipe through images")
    print("3. Say 'one', 'two', 'three' or '1', '2', '3'")
    print("4. Click Stop Recording when done")
    print("5. Apply ordering to rename files")
    
    # Simple command line interface
    while True:
        command = input("\n> ").strip().lower()
        
        if command == "start":
            success, message = orderer.start_recording()
            print(f"{'✅' if success else '❌'} {message}")
            
        elif command == "stop":
            success, message = orderer.stop_recording()
            print(f"{'✅' if success else '❌'} {message}")
            print(f"📊 Detected numbers: {orderer.get_detected_numbers()}")
            
        elif command == "apply":
            station = input("Station code: ").strip()
            year = int(input("Year: ").strip())
            obs_time = input("Observation time (default 06): ").strip() or "06"
            
            success, result = orderer.apply_ordering(station, year, obs_time)
            if success:
                print("✅ Ordering applied successfully:")
                for line in result:
                    print(f"  {line}")
            else:
                print(f"❌ {result}")
                
        elif command == "quit" or command == "exit":
            break
            
        elif command == "help":
            print("Commands: start, stop, apply, quit, help")
            
        else:
            print("Unknown command. Type 'help' for commands.")

if __name__ == "__main__":
    main()
