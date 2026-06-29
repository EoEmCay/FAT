import tkinter as tk
from tkinter import scrolledtext
import threading
from src.orchestrator import orchestrator
import time

class FacebookAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Facebook Automation")
        self.root.geometry("600x500")

        header = tk.Label(root, text="Facebook Automation Pipeline", font=("Arial", 14, "bold"))
        header.pack(pady=10)

        self.status = tk.Label(root, text="Status: STOPPED", font=("Arial", 12))
        self.status.pack(pady=5)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="START", command=self.start_pipeline, bg="green", fg="white", width=20, font=("Arial", 12))
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(btn_frame, text="STOP", command=self.stop_pipeline, bg="red", fg="white", width=20, font=("Arial", 12))
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        tk.Label(root, text="Logs:").pack(anchor=tk.W, padx=10)
        self.log_text = scrolledtext.ScrolledText(root, height=15, width=70)
        self.log_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.is_running = False

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def start_pipeline(self):
        if self.is_running:
            self.log("Already running")
            return

        self.is_running = True
        self.status.config(text="Status: RUNNING")
        self.start_btn.config(state=tk.DISABLED)

        def run():
            try:
                self.log("Starting orchestrator...")
                orchestrator.start_system()
                self.log("OK: Pipeline started")
                self.log("Will run at 06:00, 07:00, 08:00 daily")
                while self.is_running:
                    time.sleep(1)
            except Exception as e:
                self.log(f"ERROR: {str(e)}")
            finally:
                self.is_running = False

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def stop_pipeline(self):
        self.is_running = False
        self.status.config(text="Status: STOPPED")
        self.start_btn.config(state=tk.NORMAL)
        try:
            orchestrator.stop_system()
        except:
            pass
        self.log("Pipeline stopped")

if __name__ == "__main__":
    root = tk.Tk()
    app = FacebookAutomationApp(root)
    root.mainloop()
