import json
from core.sync import sync_sources_to_mirror
from core.snapshot import create_snapshot
from core.archive import archive_snapshot

print("=== Paranoic backup started ===")

with open("config.json", "r", encoding="utf-8") as f:
  config = json.load(f)

sync_sources_to_mirror(
  config["sources"],
  config["mirror_dir"]
)

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
