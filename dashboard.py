import tkinter as tk
from tkinter import scrolledtext
import threading
import time
from pathlib import Path

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent Dashboard")
        self.root.geometry("800x600")
        tk.Label(root, text="Agent Execution Dashboard", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(root, text="Real-time Logs:").pack(anchor=tk.W, padx=10)
        self.log_text = scrolledtext.ScrolledText(root, height=20)
        self.log_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        threading.Thread(target=self.read_logs, daemon=True).start()

    def read_logs(self):
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
    app = Dashboard(root)
    root.mainloop()