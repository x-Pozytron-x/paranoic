import os
import shutil
import time
from watchdog.events import FileSystemEventHandler
from core.exclude import is_excluded

RETRY_COUNT = 5
RETRY_DELAY = 0.5  # сек


class SyncHandler(FileSystemEventHandler):
  def __init__(self, src, dst, log, exclude):
    self.src_root = src
    self.dst_root = dst
    self.log = log
    self.exclude = exclude

  def _map_dst(self, path):
    rel = os.path.relpath(path, self.src_root)
    return os.path.join(self.dst_root, rel)

  def _rel(self, path):
    return os.path.relpath(path, self.src_root)

  def _safe_copy(self, src, dst):
    for _ in range(RETRY_COUNT):
      try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        return True
      except PermissionError:
        time.sleep(RETRY_DELAY)
      except FileNotFoundError:
        return False
    self.log(f"[!] Skipped busy file: {self._rel(src)}")
    return False

  def on_created(self, event):
    if event.is_directory:
      return

    if is_excluded(event.src_path, self.exclude, self.src_root):
      return

    dst = self._map_dst(event.src_path)
    if self._safe_copy(event.src_path, dst):
      self.log(f"[+] Created: {self._rel(event.src_path)}")

  def on_modified(self, event):
    if event.is_directory:
      return

    if is_excluded(event.src_path, self.exclude, self.src_root):
      return

    dst = self._map_dst(event.src_path)
    if self._safe_copy(event.src_path, dst):
      self.log(f"[~] Modified: {self._rel(event.src_path)}")

  def on_deleted(self, event):
    if event.is_directory:
      return

    dst = self._map_dst(event.src_path)
    if os.path.exists(dst):
      os.remove(dst)
      self.log(f"[-] Deleted: {self._rel(event.src_path)}")
