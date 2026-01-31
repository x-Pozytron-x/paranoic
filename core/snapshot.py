import os
import shutil
from datetime import datetime

def create_snapshot(mirror_dir, snapshots_dir, log):
  timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  snapshot_path = os.path.join(snapshots_dir, timestamp)

  log("[*] Creating snapshot...")

  os.makedirs(snapshots_dir, exist_ok=True)
  shutil.copytree(mirror_dir, snapshot_path)
  log(f"[+] Snapshot created: {snapshot_path}")
  return snapshot_path
