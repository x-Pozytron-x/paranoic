import fnmatch
import os

def is_excluded(path, patterns, root=None):
  name = os.path.basename(path)

  for pattern in patterns:
    # по имени файла
    if fnmatch.fnmatch(name, pattern):
      return True

    # по относительному пути
    if root:
      rel = os.path.relpath(path, root)
      if fnmatch.fnmatch(rel, pattern):
        return True

  return False
