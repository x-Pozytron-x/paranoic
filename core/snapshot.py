import os
import shutil
from datetime import datetime

def create_snapshot(mirror_dir, snapshots_dir):
  timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  snapshot_path = os.path.join(snapshots_dir, timestamp)

  print(f"[+] Creating snapshot: {snapshot_path}")

  os.makedirs(snapshots_dir, exist_ok=True)
  shutil.copytree(mirror_dir, snapshot_path)

  return snapshot_path
