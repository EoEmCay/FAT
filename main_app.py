import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from pathlib import Path
from src.orchestrator import orchestrator

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Facebook Automation - Complete System")
        self.root.geometry("1000x700")
        self.is_running = False

        header = tk.Label(root, text="Facebook Automation Pipeline", font=("Arial", 16, "bold"), bg="#007AFF", fg="white")
        header.pack(fill=tk.X, padx=10, pady=10)

        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Control Panel")

        self.status = tk.Label(control_frame, text="Status: STOPPED", font=("Arial", 14, "bold"), fg="red")
        self.status.pack(pady=20)

        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="START SYSTEM", command=self.start, bg="green", fg="white", font=("Arial", 12, "bold"), width=20, height=3)
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(btn_frame, text="STOP SYSTEM", command=self.stop, bg="red", fg="white", font=("Arial", 12, "bold"), width=20, height=3)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        tk.Label(control_frame, text="Schedule: 6AM (Scraper) | 7AM (Processor) | 8AM (Publisher)", font=("Arial", 11)).pack(pady=20)

        dash_frame = ttk.Frame(notebook)
        notebook.add(dash_frame, text="Dashboard")

        tk.Label(dash_frame, text="Real-time Logs:").pack(anchor=tk.W, padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(dash_frame, height=25, width=120)
        self.log_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        threading.Thread(target=self.monitor_logs, daemon=True).start()

    def start(self):
        if self.is_running:
            self.log("Already running")
            return

        self.is_running = True
        self.status.config(text="Status: RUNNING", fg="green")
        self.start_btn.config(state=tk.DISABLED)

        def run():
            try:
                self.log("Starting orchestrator...")
                orchestrator.start_system()
                self.log("Orchestrator started successfully")
                self.log("Pipeline will run at 6AM, 7AM, 8AM daily")
                while self.is_running:
                    time.sleep(1)
            except Exception as e:
                self.log(f"Error: {str(e)}")
            finally:
                self.is_running = False

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def stop(self):
        self.is_running = False
        self.status.config(text="Status: STOPPED", fg="red")
        self.start_btn.config(state=tk.NORMAL)
        try:
            orchestrator.stop_system()
        except:
            pass
        self.log("System stopped")

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def monitor_logs(self):
        try:
            last_pos = 0
            while True:
                if Path("logs/orchestrator.log").exists():
                    with open("logs/orchestrator.log", "r") as f:
                        f.seek(last_pos)
                        for line in f:
                            self.log_text.insert(tk.END, line)
                            self.log_text.see(tk.END)
                        last_pos = f.tell()
                time.sleep(1)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
