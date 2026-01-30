import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import subprocess

CONFIG_PATH = "config.json"


class ParanoicApp:
  def __init__(self):
    self.process = None

    self.root = tk.Tk()
    self.root.title("Paranoic Backup")
    self.root.geometry("700x500")

    self.sources = []

    self._load_config()
    self._build_ui()

  def run(self):
    self.root.mainloop()


  # ---------------- CONFIG ----------------
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
    self.config["password"] = self.password_var.get()

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
      json.dump(self.config, f, indent=2)

    messagebox.showinfo("Paranoic", "Config saved")

  # ---------------- UI ----------------

  def _build_ui(self):
    frame = tk.Frame(self.root)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # -------- Sources --------
    tk.Label(frame, text="Source folders").pack(anchor="w")

    self.sources_list = tk.Listbox(frame, height=5)
    self.sources_list.pack(fill="x")

    for src in self.config["sources"]:
      self.sources_list.insert(tk.END, src)

    tk.Button(frame, text="+ Add folder", command=self.add_source).pack(anchor="w", pady=5)


    # -------- Target dirs --------
    self.mirror_var = tk.StringVar(value=self.config["mirror_dir"])
    self.snapshot_var = tk.StringVar(value=self.config["snapshots_dir"])
    self.archive_var = tk.StringVar(value=self.config["archive_dir"])

    self._dir_picker(frame, "Mirror directory", self.mirror_var)
    self._dir_picker(frame, "Snapshots directory", self.snapshot_var)
    self._dir_picker(frame, "Archive directory", self.archive_var)

    # -------- Password --------
    tk.Label(frame, text="Password").pack(anchor="w", pady=(10, 0))
    self.password_var = tk.StringVar(value=self.config.get("password", ""))
    tk.Entry(frame, textvariable=self.password_var, show="*").pack(fill="x")

    # -------- Buttons --------
    btns = tk.Frame(frame)
    btns.pack(fill="x", pady=15)

    tk.Button(btns, text="💾 Save", command=self._save_all).pack(side="left", padx=5)
    tk.Button(btns, text="▶ Start", command=self.start_backup).pack(side="left", padx=5)
    tk.Button(btns, text="⏹ Stop", command=self.stop_backup).pack(side="left", padx=5)


  # ---------------- HELPERS ----------------

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

  def _save_all(self):
    self.config["mirror_dir"] = self.mirror_var.get()
    self.config["snapshots_dir"] = self.snapshot_var.get()
    self.config["archive_dir"] = self.archive_var.get()
    self._save_config()

  # def _save_config(self):
  #   with open(CONFIG_PATH, "w", encoding="utf-8") as f:
  #     json.dump(self.config, f, indent=2)

  # ---------------- PROCESS ----------------

  def start_backup(self):
    if self.process:
      messagebox.showwarning("Paranoic", "Backup already running")
      return

    self._save_all()

    self.process = subprocess.Popen(
      ["python", "main.py"],
      creationflags=subprocess.CREATE_NEW_CONSOLE
    )

  def stop_backup(self):
    if not self.process:
      return

    self.process.terminate()
    self.process = None