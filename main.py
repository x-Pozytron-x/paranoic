import json
import os
import time

from watchdog.observers import Observer

from core.sync import sync_sources_to_mirror
from core.snapshot import create_snapshot
from core.archive import archive_snapshot
from core.watch import SyncHandler


STOP_FILE = "stop.flag"

print("=== Paranoic backup started ===")

# -------- Load config --------
with open("config.json", "r", encoding="utf-8") as f:
  config = json.load(f)

# -------- Initial sync --------
sync_sources_to_mirror(
  config["sources"],
  config["mirror_dir"]
)

# -------- Realtime observers --------
observers = []

for src in config["sources"]:
  folder = os.path.basename(src.rstrip("\\/"))
  dst = os.path.join(config["mirror_dir"], folder)

  handler = SyncHandler(src, dst)
  observer = Observer()
  observer.schedule(handler, src, recursive=True)
  observer.start()

  observers.append(observer)

print("[*] Realtime sync active")

# -------- Main loop --------
try:
  while True:
    if os.path.exists(STOP_FILE):
      print("[*] Stop signal received")
      os.remove(STOP_FILE)
      break
    time.sleep(1)

finally:
  print("[*] Stopping sync...")

  for obs in observers:
    obs.stop()

  for obs in observers:
    obs.join()

  # -------- Snapshot --------
  snapshot_path = create_snapshot(
    config["mirror_dir"],
    config["snapshots_dir"]
  )

  # -------- Archive --------
  archive_snapshot(
    snapshot_path,
    config["archive_dir"],
    config["password"]
  )

  print("=== Paranoic backup finished ===")
