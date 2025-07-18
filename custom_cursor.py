import ctypes
import os

def set_global_cursor(cursor_filename="red_dot.cur"):
    cursor_path = os.path.abspath(cursor_filename)
    ctypes.windll.user32.SetSystemCursor(
        ctypes.windll.user32.LoadCursorFromFileW(cursor_path), 32512  # OCR_NORMAL
    )

def restore_default_cursor():
    # Restores all default system cursors
    ctypes.windll.user32.SystemParametersInfoW(87, 0, 0, 0)  # SPI_SETCURSORS
