import tkinter as tk
from tkinter import filedialog
import json
import os
import threading
import queue

from core.runner import run_backup

CONFIG_PATH = "config.json"
STOP_FILE = "stop.flag"
PROCESS_FINISHED = "__PROCESS_FINISHED__"


class ParanoicApp:
  def __init__(self):
    self.root = tk.Tk()
    self.root.title("Paranoic Backup")
    self.root.geometry("700x620")

    self.log_queue = queue.Queue()
    self.process_thread = None

    self._load_config()
    self._build_ui()

  # ===================== RUN =====================

  def run(self):
    self._poll_logs()
    self.root.mainloop()

  # ===================== CONFIG =====================

  def _load_config(self):
    if os.path.exists(CONFIG_PATH):
      with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        self.config = json.load(f)
    else:
      self.config = {
        "sources": [],
        "mirror_dir": "",
        "snapshots_dir": "",
        "archive_dir": "",
        "password": ""
      }

  def _save_config(self):
    self.config["mirror_dir"] = self.mirror_var.get()
    self.config["snapshots_dir"] = self.snapshot_var.get()
    self.config["archive_dir"] = self.archive_var.get()
    self.config["password"] = self.password_var.get()

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
      json.dump(self.config, f, indent=2)

    self.log("💾 Config saved")

  # ===================== UI =====================

  def _build_ui(self):
    frame = tk.Frame(self.root)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ---- Sources ----
    tk.Label(frame, text="Source folders").pack(anchor="w")
    self.sources_list = tk.Listbox(frame, height=5)
    self.sources_list.pack(fill="x")

    for src in self.config["sources"]:
      self.sources_list.insert(tk.END, src)

    tk.Button(frame, text="+ Add folder", command=self.add_source).pack(anchor="w", pady=5)

    # ---- Directories ----
    self.mirror_var = tk.StringVar(value=self.config["mirror_dir"])
    self.snapshot_var = tk.StringVar(value=self.config["snapshots_dir"])
    self.archive_var = tk.StringVar(value=self.config["archive_dir"])

    self._dir_picker(frame, "Mirror directory", self.mirror_var)
    self._dir_picker(frame, "Snapshots directory", self.snapshot_var)
    self._dir_picker(frame, "Archive directory", self.archive_var)

    # ---- Password ----
    tk.Label(frame, text="Password").pack(anchor="w", pady=(10, 0))
    self.password_var = tk.StringVar(value=self.config.get("password", ""))
    tk.Entry(frame, textvariable=self.password_var, show="*").pack(fill="x")

    # ---- Exclude ----
    tk.Label(frame, text="Exclude patterns").pack(anchor="w", pady=(10, 0))
    self.exclude_box = tk.Text(frame, height=5)
    self.exclude_box.pack(fill="x")
    if "exclude" in self.config:
      self.exclude_box.insert("1.0", "\n".join(self.config["exclude"]))

    # ---- Buttons ----
    btns = tk.Frame(frame)
    btns.pack(fill="x", pady=10)

    self.start_btn = tk.Button(btns, text="▶ Start", command=self.start_backup)
    self.start_btn.pack(side="left", padx=5)

    self.stop_btn = tk.Button(btns, text="⏹ Stop", command=self.stop_backup, state="disabled")
    self.stop_btn.pack(side="left", padx=5)

    tk.Button(btns, text="💾 Save", command=self._save_config).pack(side="left", padx=5)

    # ---- Log ----
    tk.Label(frame, text="Log").pack(anchor="w", pady=(10, 0))
    self.log_box = tk.Text(frame, height=12, state="disabled")
    self.log_box.pack(fill="both", expand=True)

  # ===================== LOGGING =====================

  def log(self, message):
    self.log_queue.put(message)

  def _poll_logs(self):
    while not self.log_queue.empty():
      msg = self.log_queue.get()

      if msg == PROCESS_FINISHED:
        self.process_thread = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self._write_log("🟢 Ready")
        continue

      self._write_log(msg)

    self.root.after(200, self._poll_logs)

  def _write_log(self, text):
    self.log_box.config(state="normal")
    self.log_box.insert("end", text + "\n")
    self.log_box.see("end")
    self.log_box.config(state="disabled")

  # ===================== HELPERS =====================

  def _dir_picker(self, parent, label, var):
    tk.Label(parent, text=label).pack(anchor="w", pady=(10, 0))
    row = tk.Frame(parent)
    row.pack(fill="x")

    tk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
    tk.Button(row, text="Browse", command=lambda: self.pick_dir(var)).pack(side="left", padx=5)

  def pick_dir(self, var):
    path = filedialog.askdirectory()
    if path:
      var.set(path)

  def add_source(self):
    path = filedialog.askdirectory()
    if not path:
      return

    if path not in self.config["sources"]:
      self.config["sources"].append(path)
      self.sources_list.insert(tk.END, path)
      self._save_config()

  # ===================== PROCESS =====================

  def start_backup(self):
    if self.process_thread:
      self.log("⚠ Backup already running")
      return

    if os.path.exists(STOP_FILE):
      os.remove(STOP_FILE)

    self._save_config()
    self.log("▶ Backup started")

    self.start_btn.config(state="disabled")
    self.stop_btn.config(state="normal")

    self.process_thread = threading.Thread(
      target=run_backup,
      args=(self.log,),
      daemon=True
    )
    self.process_thread.start()

  def stop_backup(self):
    if not self.process_thread:
      self.log("⚠ Backup is not running")
      return

    with open(STOP_FILE, "w"):
      pass

    self.log("⏹ Stop requested (waiting...)")
    self.stop_btn.config(state="disabled")


if __name__ == "__main__":
  ParanoicApp().run()
 