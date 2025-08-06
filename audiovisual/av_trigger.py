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

from PIL import Image, ImageDraw, ImageStat
from pystray import Icon, MenuItem, Menu
from plyer import notification

from pynput import mouse
from PIL import ImageDraw

# load your custom cursor image
CURSOR_IMG = Image.open("cursor.png")

mouse_clicked = False  # global flag
last_click_time = 0  # timestamp of last click
click_duration = 0.5  # how long to show click highlight (seconds)


# SETTINGS
RECORD_TIME = 15  # seconds (default)
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


def record_screen(ts, start_event, duration):
    
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
    
    while (time.perf_counter() - start_time) < duration:
        now = time.perf_counter()
        if now < next_capture_time:
            time.sleep(0.005)
            continue
        next_capture_time += frame_interval

        try:
            # ——— 1) grab a fresh screenshot
            screenshot = pyautogui.screenshot()
            screen_w, screen_h = screenshot.size

            # ——— 2) get the real mouse position
            cursor_x, cursor_y = pyautogui.position()
            # clamp into bounds just in case
            cursor_x = max(0, min(cursor_x, screen_w - 1))
            cursor_y = max(0, min(cursor_y, screen_h - 1))

            draw = ImageDraw.Draw(screenshot)

            # ——— 3a) sample a small region around the cursor to decide light vs dark background
            sample_size = 9
            left = max(0, cursor_x - sample_size//2)
            upper = max(0, cursor_y - sample_size//2)
            right = min(screen_w, left + sample_size)
            lower = min(screen_h, upper + sample_size)
            region = screenshot.crop((left, upper, right, lower)).convert("L")
            mean_lum = ImageStat.Stat(region).mean[0]

            # if background is bright, draw black cursor; if dark, draw white
            if mean_lum > 160:
                fill_col = "black"
                outline_col = "white"
            else:
                fill_col = "white"
                outline_col = "black"         

            # ——— 3b) define a Windows‑style arrow (proper shape)
            arrow = [
                (cursor_x, cursor_y),                    # tip
                (cursor_x + 3, cursor_y + 15),          # left side down
                (cursor_x + 8, cursor_y + 12),          # notch left
                (cursor_x + 12, cursor_y + 18),         # bottom left
                (cursor_x + 15, cursor_y + 16),         # bottom right
                (cursor_x + 11, cursor_y + 8),          # notch right (moved right and up)
                (cursor_x + 17, cursor_y + 2),          # right side (moved right and up)
                (cursor_x, cursor_y),                    # back to tip (close polygon)
            ]

            # draw the outline slightly thicker for visibility
            draw.polygon(arrow, fill=outline_col, width=2)
            # draw the inner fill
            draw.polygon(arrow, fill=fill_col, outline=outline_col, width=1)

            # ——— 4) draw click‑highlight if we saw a click
            if 0 < last_click_time and (time.perf_counter() - last_click_time) < click_duration:
                O = 20

                # make sure our image is RGBA
                base = screenshot.convert("RGBA")

                # create a transparent overlay
                overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
                od = ImageDraw.Draw(overlay)

                # draw semi‑transparent yellow fill
                #    (255,255,0,128) → yellow at 50% opacity
                # Adjust the highlight to be centered on the arrow
                arrow_center_x = sum([point[0] for point in arrow]) // len(arrow)
                arrow_center_y = sum([point[1] for point in arrow]) // len(arrow)

                bbox = [(arrow_center_x - O, arrow_center_y - O), (arrow_center_x + O, arrow_center_y + O)]
                od.ellipse(bbox, fill=(255, 255, 0, 128))

                # composite the overlay onto the frame
                composed = Image.alpha_composite(base, overlay)

                # draw the red outline on top
                draw2 = ImageDraw.Draw(composed)
                draw2.ellipse(bbox, outline="red", width=4)

                # convert back to RGB for your video writer
                screenshot = composed.convert("RGB")

            # ——— 5) convert & write frame
            frame_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            video_writer.write(frame_cv)
            frames_for_gif.append(screenshot)

        except Exception as e:
            print("Error capturing frame:", e)
            continue

    # Release video writer
    video_writer.release()
    
    end_time = time.perf_counter()
    actual_duration = end_time - start_time
    print(f"🎥 Screen recording completed. Duration: {actual_duration:.2f}s, Frames: {len(frames_for_gif)}")
    print(f"🎥 Video saved: {video_file}")
    
    # Convert to GIF
    try:
        print(f"🎥 Converting video to GIF...")
        imageio.mimsave(gif_file, frames_for_gif, duration=frame_interval, loop=0)
        print(f"🎥 GIF created: {gif_file}")
    except Exception as e:
        print(f"Error creating GIF: {e}")
        
    return gif_file


def record_audio(ts, start_event, duration):
    """Records audio and saves as WAV"""
    wav_file = f"audio_{ts}.wav"
    print(f"🎵 Audio recording ready, waiting for start signal...")
    
    try:
        # Wait for the start signal
        start_event.wait()
        
        start_time = time.perf_counter()
        print(f"🎵 Audio recording started at: {start_time}")
        
        audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS)
        sd.wait()
        
        end_time = time.perf_counter()
        actual_duration = end_time - start_time
        print(f"🎵 Audio recording completed. Duration: {actual_duration:.2f}s")
        
        wavio.write(wav_file, audio, SAMPLE_RATE, sampwidth=SAMPWIDTH)
        print(f"🎵 Audio recorded: {wav_file}")
    except Exception as e:
        print(f"Error recording audio: {e}")
        
    return wav_file

def record(duration=None, status_callback=None):
    if duration is None:
        duration = RECORD_TIME
    
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"🔴 Starting recording session: {ts}")

    if status_callback:
        status_callback("🔴 Recording started...")

    start_event = threading.Event()
    
    screen_thread = threading.Thread(target=record_screen, args=(ts, start_event, duration))
    audio_thread = threading.Thread(target=record_audio, args=(ts, start_event, duration))
    
    screen_thread.start()
    audio_thread.start()

    time.sleep(0.1)
    start_event.set()

    if status_callback:
        for i in range(duration, 0, -1):
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

    print(f"✅ Recording session complete: screen_{ts}.mp4, screen_{ts}.gif & audio_{ts}.wav")


def create_image():
    """Creates a basic icon image for tray"""
    image = Image.new('RGB', (64, 64), color=(0, 102, 204))  # blue
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill='white')
    return image

def setup_tray():
    icon = Icon("QA Recorder")

    def quit_app(icon, item):
        icon.stop()
        os._exit(0)

    def record_10_seconds(icon, item):
        threading.Thread(target=record, args=(10,), daemon=True).start()

    def record_15_seconds(icon, item):
        threading.Thread(target=record, args=(15,), daemon=True).start()

    def record_20_seconds(icon, item):
        threading.Thread(target=record, args=(20,), daemon=True).start()

    icon.icon = create_image()
    icon.menu = Menu(
        MenuItem('Record 10 seconds', record_10_seconds),
        MenuItem('Record 15 seconds', record_15_seconds),
        MenuItem('Record 20 seconds', record_20_seconds),
        MenuItem('Quit', quit_app)
    )

    # Start listening for hotkey (defaults to 15 seconds)
    keyboard.add_hotkey('ctrl+shift+r', on_hotkey)

    icon.run()

# mouse listener to detect clicks
def on_click(x, y, button, pressed):
    global mouse_clicked, last_click_time
    if pressed:
        mouse_clicked = True
        last_click_time = time.perf_counter()
        # Removed terminal output for cleaner recording
    else:
        mouse_clicked = False

def on_hotkey():
    """Handle hotkey press for recording"""
    threading.Thread(target=record, args=(15,), daemon=True).start()

# MAIN
if __name__ == '__main__':
    # Start mouse listener first
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    setup_tray()
