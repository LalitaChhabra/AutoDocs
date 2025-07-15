import pyautogui
import sounddevice as sd
import cv2
import numpy as np
import imageio
import wavio
import datetime
import threading
import keyboard
import time
import os
import sys

from PIL import Image, ImageDraw
from pystray import Icon, MenuItem, Menu
from plyer import notification

from pynput import mouse
from PIL import ImageDraw

mouse_clicked = False  # global flag
last_click_time = 0  # timestamp of last click
click_duration = 0.5  # how long to show click highlight (seconds)


# SETTINGS
RECORD_TIME = 15  # seconds
SAMPLE_RATE = 48000
CHANNELS = 1
SAMPWIDTH = 2

def notify(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=3  # seconds
    )

from PIL import ImageDraw


def record_screen(ts, start_event, status_callback=None):
    """Record screen as video first, then convert to GIF"""
    video_file = f"screen_{ts}.mp4"
    gif_file = f"screen_{ts}.gif"
    
    # Wait for the start signal for the audio recording
    start_event.wait()
    
    start_time = time.perf_counter()
    fps = 10
    frame_interval = 1.0 / fps
    next_capture_time = start_time

    print(f"🎥 Screen recording started at: {start_time}")
    
    # Get screen dimensions
    screen_width, screen_height = pyautogui.size()
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(video_file, fourcc, fps, (screen_width, screen_height))
    
    frames_for_gif = []
    
    while (time.perf_counter() - start_time) < RECORD_TIME:
        now = time.perf_counter()
        if now >= next_capture_time:
            try:
                screenshot = pyautogui.screenshot()
                cursor_x, cursor_y = pyautogui.position()
                draw = ImageDraw.Draw(screenshot)

                # Cursor arrow
                arrow_size = 10
                draw.polygon([
                    (cursor_x, cursor_y),
                    (cursor_x + arrow_size, cursor_y + 3),
                    (cursor_x + 3, cursor_y + arrow_size)
                ], fill="black")

                # Click highlight - show for a brief period after click
                current_time = time.perf_counter()
                if mouse_clicked or (current_time - last_click_time) < click_duration:
                    radius = 20
                    # Draw multiple circles for better visibility
                    draw.ellipse([
                        (cursor_x - radius, cursor_y - radius),
                        (cursor_x + radius, cursor_y + radius)
                    ], outline="red", width=4)
                    draw.ellipse([
                        (cursor_x - radius//2, cursor_y - radius//2),
                        (cursor_x + radius//2, cursor_y + radius//2)
                    ], outline="yellow", width=2)

                # Convert PIL image to OpenCV format for video
                frame_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                video_writer.write(frame_cv)
                
                # Store frame for GIF conversion (downsample for smaller GIF)
                frames_for_gif.append(screenshot)

                # Schedule next frame
                next_capture_time += frame_interval
                
            except Exception as e:
                print(f"Error capturing frame: {e}")
                continue

        else:
            time.sleep(0.005)  # Prevent CPU overuse

    # Release video writer
    video_writer.release()
    
    end_time = time.perf_counter()
    actual_duration = end_time - start_time
    print(f"🎥 Screen recording completed. Duration: {actual_duration:.2f}s, Frames: {len(frames_for_gif)}")
    print(f"🎥 Video saved: {video_file}")
    
    # Convert to GIF
    try:
        print(f"🎥 Converting video to GIF...")
        imageio.mimsave(gif_file, frames_for_gif, duration=frame_interval)
        print(f"🎥 GIF created: {gif_file}")
    except Exception as e:
        print(f"Error creating GIF: {e}")
        
    return gif_file


def record_audio(ts, start_event, status_callback=None):

    """Records audio and saves as WAV"""
    wav_file = f"audio_{ts}.wav"
    print(f"🎵 Audio recording ready, waiting for start signal...")
    
    try:
        # Wait for the start signal
        start_event.wait()
        
        start_time = time.perf_counter()
        print(f"🎵 Audio recording started at: {start_time}")
        
        audio = sd.rec(int(RECORD_TIME * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS)
        sd.wait()
        
        end_time = time.perf_counter()
        actual_duration = end_time - start_time
        print(f"🎵 Audio recording completed. Duration: {actual_duration:.2f}s")
        
        wavio.write(wav_file, audio, SAMPLE_RATE, sampwidth=SAMPWIDTH)
        print(f"🎵 Audio recorded: {wav_file}")
    except Exception as e:
        print(f"Error recording audio: {e}")
        
    return wav_file

def record(status_callback=None):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"🔴 Starting recording session: {ts}")
    notify("Recording", f"Recording screen and audio for {RECORD_TIME} seconds...")

    if status_callback:
        status_callback("🔴 Recording started...")

    start_event = threading.Event()

    screen_thread = threading.Thread(target=record_screen, args=(ts, start_event, status_callback))
    audio_thread = threading.Thread(target=record_audio, args=(ts, start_event, status_callback))

    screen_thread.start()
    audio_thread.start()

    time.sleep(0.1)
    start_event.set()

    if status_callback:
        for i in range(RECORD_TIME, 0, -1):
            status_callback(f"⏳ {i} seconds remaining...")
            time.sleep(1)


     # Start animated loading spinner in separate thread
    loading = True
    def loading_spinner():
        dots = 0
        while loading:
            status_callback("🔄 Saving" + "." * (dots % 4))
            dots += 1
            time.sleep(0.5)

    spinner_thread = threading.Thread(target=loading_spinner, daemon=True)
    spinner_thread.start()

    # Wait for recordings to finish
    screen_thread.join()
    audio_thread.join()

    # Stop spinner
    loading = False
    spinner_thread.join(timeout=0.1)

    if status_callback:
        status_callback("✅ Recording session complete. Files saved!")

    notify("Done", "Recording complete. Files saved.")
    print(f"✅ Recording session complete: screen_{ts}.mp4, screen_{ts}.gif & audio_{ts}.wav")


# test 1 test2 test3... 