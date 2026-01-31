import json
import os
import time

from watchdog.observers import Observer
from core.sync import sync_sources_to_mirror
from core.snapshot import create_snapshot
from core.archive import archive_snapshot
from core.watch import SyncHandler


def run_backup(log):
  STOP_FILE = "stop.flag"

  log("=== Paranoic backup started ===")

  with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

  sync_sources_to_mirror(
    config["sources"],
    config["mirror_dir"],
    log
  )

  observers = []

  for src in config["sources"]:
    folder = os.path.basename(src.rstrip("\\/"))
    dst = os.path.join(config["mirror_dir"], folder)

    handler = SyncHandler(src, dst, log)
    observer = Observer()
    observer.schedule(handler, src, recursive=True)
    observer.start()
    observers.append(observer)

  log("[*] Realtime sync active")

  try:
    while True:
      if os.path.exists(STOP_FILE):
        log("[*] Stop signal received")
        os.remove(STOP_FILE)
        break
      time.sleep(1)

  finally:
    log("[*] Stopping sync...")

    for obs in observers:
      obs.stop()
    for obs in observers:
      obs.join()

    snapshot_path = create_snapshot(
      config["mirror_dir"],
      config["snapshots_dir"],
      log
    )

    archive_snapshot(
      snapshot_path,
      config["archive_dir"],
      config["password"],
      log
    )

    log("=== Paranoic backup finished ===")
    
  log("__PROCESS_FINISHED__")