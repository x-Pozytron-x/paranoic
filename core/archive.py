import os
import py7zr
from datetime import datetime

def archive_snapshot(snapshot_path, archive_dir, password, log):
  date = datetime.now().strftime("%Y-%m-%d")
  archive_name = f"paranoic-backup-{date}.7z"
  archive_path = os.path.join(archive_dir, archive_name)

  log("[*] Creating archive...")

  os.makedirs(archive_dir, exist_ok=True)

  with py7zr.SevenZipFile(
    archive_path,
    mode="w",
    password=password
  ) as archive:
    archive.writeall(snapshot_path, arcname=os.path.basename(snapshot_path))

  log("[✓] Archive created")
