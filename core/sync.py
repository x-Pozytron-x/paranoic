import os
import shutil

def sync_sources_to_mirror(sources, mirror_dir):
  print("[*] Sync started")

  os.makedirs(mirror_dir, exist_ok=True)

  for src in sources:
    if not os.path.exists(src):
      print(f"[!] Source not found: {src}")
      continue

    folder_name = os.path.basename(src.rstrip("\\/"))
    dest = os.path.join(mirror_dir, folder_name)

    print(f"[+] Syncing {src} → {dest}")

    if os.path.exists(dest):
      shutil.rmtree(dest)

    shutil.copytree(src, dest)

  print("[✓] Sync finished")
