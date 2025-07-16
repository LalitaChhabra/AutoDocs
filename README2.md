## 🆕 GUI Updates

### GUI Interface (for GIF Converter)
- Launchable via `gui_launcher.py`
- Allows users to start 15-second screen + audio recordings
- Provides a visual countdown and live status feedback

## How to Use the GUI

1. **Press "Start"**  
    Click the "Start" button in the GUI to begin a new recording session.

2. **Recording in Progress**  
    A countdown timer will appear, showing the remaining recording time (starting from 15 seconds). The recording will automatically stop when the timer reaches 1 second.

3. **Processing**  
    After recording ends, the GUI will display a "Loading..." message while the video is being converted to a GIF.

4. **Completion**  
    Once the conversion is finished, the GUI will show a "Saving complete" message to indicate the process is done and your GIF is ready.

## Summary of Changes
- Introduced `gui_launcher.py` file for manual recording control
- Added countdown and status display using `status_callback`
- Updated `av_trigger.py` to support GUI-initiated recording sessions
- Preserved `Ctrl+Shift+R` hotkey functionality for background recording (works in terminal)

