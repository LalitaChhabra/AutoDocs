import tkinter as tk
import threading
from av_trigger import record  # make sure this is the file where your modified record() lives

def start_gui():
    def start_recording():
        # Clear any previous status and start a new thread
        update_status("🔴 Starting recording...")

        def threaded_record():
            try:
                record(status_callback=update_status)
            except Exception as e:
                update_status(f"❌ Error: {e}")

        threading.Thread(target=threaded_record, daemon=True).start()

    def update_status(message):
        # Update the status label text in the GUI
        status_var.set(message)

    # Setup GUI window
    root = tk.Tk()
    root.title("QA Recorder")

    tk.Label(root, text="QA Recorder").pack(pady=(10, 5))
    tk.Button(root, text="Start Recording", command=start_recording).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

    # Status label
    status_var = tk.StringVar()
    status_label = tk.Label(root, textvariable=status_var, fg="blue", wraplength=300, justify="left")
    status_label.pack(pady=(10, 10))
    status_var.set("🕒 Ready to record. Click the button to begin.")

    root.mainloop()

if __name__ == "__main__":
    start_gui()
