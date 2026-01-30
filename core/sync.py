import os
import shutil

def sync_dir(src, dst):
  for root, dirs, files in os.walk(src):
    rel_path = os.path.relpath(root, src)
    dest_root = os.path.join(dst, rel_path)

    os.makedirs(dest_root, exist_ok=True)

    for file in files:
      src_file = os.path.join(root, file)
      dst_file = os.path.join(dest_root, file)

      if not os.path.exists(dst_file) or (
        os.path.getmtime(src_file) > os.path.getmtime(dst_file)
      ):
        shutil.copy2(src_file, dst_file)

  # удаление лишних файлов в mirror
  for root, dirs, files in os.walk(dst):
    rel_path = os.path.relpath(root, dst)
    src_root = os.path.join(src, rel_path)

    for file in files:
      dst_file = os.path.join(root, file)
      src_file = os.path.join(src_root, file)

      if not os.path.exists(src_file):
        os.remove(dst_file)

def sync_sources_to_mirror(sources, mirror_dir):
  print("[*] Incremental sync started")

  os.makedirs(mirror_dir, exist_ok=True)

  for src in sources:
    if not os.path.exists(src):
      print(f"[!] Source not found: {src}")
      continue

    folder_name = os.path.basename(src.rstrip("\\/"))
    dst = os.path.join(mirror_dir, folder_name)

    print(f"[+] Syncing {src} → {dst}")
    os.makedirs(dst, exist_ok=True)

    sync_dir(src, dst)

  print("[✓] Incremental sync finished")
