import os
import shutil
import time
from watchdog.events import FileSystemEventHandler

RETRY_COUNT = 5
RETRY_DELAY = 0.5  # сек

class SyncHandler(FileSystemEventHandler):
  def __init__(self, src, dst, log):
    self.src_root = src
    self.dst_root = dst
    self.log = log

  def _map_path(self, path):
    rel = os.path.relpath(path, self.src_root)
    return os.path.join(self.dst_root, rel)

  def _safe_copy(self, src, dst):
    for attempt in range(RETRY_COUNT):
      try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        return
      except PermissionError:
        time.sleep(RETRY_DELAY)
      except FileNotFoundError:
        return
    print(f"[!] Skipped busy file: {src}")

  def on_created(self, event):
    dst = self._map_path(event.src_path)

    if event.is_directory:
      os.makedirs(dst, exist_ok=True)
    else:
      self._safe_copy(event.src_path, dst)

  def on_modified(self, event):
    if not event.is_directory:
      dst = self._map_path(event.src_path)
      self._safe_copy(event.src_path, dst)

  def on_deleted(self, event):
    dst = self._map_path(event.src_path)
    if os.path.exists(dst):
      try:
        if os.path.isdir(dst):
          shutil.rmtree(dst)
        else:
          os.remove(dst)
      except PermissionError:
        pass
