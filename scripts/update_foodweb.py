#!/usr/bin/env python3
"""Pin a release of the Colorado Open Food Web into data/foodweb/.

  python scripts/update_foodweb.py v2026.10.1            # download that release and check its checksums
  python scripts/update_foodweb.py v2026.10.1 --from-dir ../open-food-web/release   # use a local copy (testing)

The Food Web builds and maintains the data; this app reads a pinned release of it and never runs the
pipeline. Upgrading means running this with a newer version and reviewing the diff. Data CC BY 4.0:
credit "Colorado Open Food Web".
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import urllib.request

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DEST = os.path.join(REPO, "data", "foodweb")
BASE = "https://github.com/open-food-web/colorado-open-food-web/releases/download/{tag}/{name}"
UA = "Mozilla/5.0 (compatible; ColoradoFarmTrail/1.0; +https://coloradofarmtrail.com)"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(tag, name, dest, from_dir):
    if from_dir:
        shutil.copyfile(os.path.join(from_dir, name), dest)
        return
    req = urllib.request.Request(BASE.format(tag=tag, name=name), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as out:
        shutil.copyfileobj(r, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version", help="release tag, e.g. v2026.10.1")
    ap.add_argument("--from-dir", help="read the release files from this folder instead of GitHub")
    a = ap.parse_args()
    tmp = os.path.join(REPO, ".cache", "foodweb-download")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    fetch(a.version, "MANIFEST.json", os.path.join(tmp, "MANIFEST.json"), a.from_dir)
    manifest = json.load(open(os.path.join(tmp, "MANIFEST.json"), encoding="utf-8"))
    if manifest["version"] != a.version:
        sys.exit(f"manifest says {manifest['version']}, not {a.version}")
    for name, info in manifest["files"].items():
        fetch(a.version, name, os.path.join(tmp, name), a.from_dir)
        got = sha256(os.path.join(tmp, name))
        if got != info["sha256"]:
            sys.exit(f"CHECKSUM MISMATCH for {name}: expected {info['sha256']}, got {got}")
        print(f"ok  {name}")
    os.makedirs(DEST, exist_ok=True)
    for name in list(manifest["files"]) + ["MANIFEST.json"]:
        shutil.copyfile(os.path.join(tmp, name), os.path.join(DEST, name))
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Pinned Colorado Open Food Web {a.version} in data/foodweb/ "
          f"({manifest['counts']['listings']} listings). Now run scripts/build_map_data.py.")


if __name__ == "__main__":
    main()
