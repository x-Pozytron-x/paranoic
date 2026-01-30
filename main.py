import json
from core.sync import sync_sources_to_mirror
from core.snapshot import create_snapshot
from core.archive import archive_snapshot

from watchdog.observers import Observer
from core.watch import SyncHandler
import time
import os


print("=== Paranoic backup started ===")

with open("config.json", "r", encoding="utf-8") as f:
  config = json.load(f)

sync_sources_to_mirror(
  config["sources"],
  config["mirror_dir"]
)


observers = []

for src in config["sources"]:
  folder = os.path.basename(src.rstrip("\\/"))
  dst = os.path.join(config["mirror_dir"], folder)

  handler = SyncHandler(src, dst)
  observer = Observer()
  observer.schedule(handler, src, recursive=True)
  observer.start()

  observers.append(observer)

print("[*] Realtime sync active. Press Ctrl+C to stop.")

try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  print("\n[*] Stopping sync...")
  for obs in observers:
    obs.stop()
    obs.join()

snapshot_path = create_snapshot(
  config["mirror_dir"],
  config["snapshots_dir"]
)

archive_snapshot(
  snapshot_path,
  config["archive_dir"],
  config["password"]
)

print("=== Paranoic backup finished ===")
