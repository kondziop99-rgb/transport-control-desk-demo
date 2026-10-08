#!/usr/bin/env python3
import hashlib
import os
import runpy
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTS = ROOT / "line_parts"
TARGET = Path("/tmp/transport-control-code")
STATIC = TARGET / "static"
TARGET.mkdir(parents=True, exist_ok=True)
STATIC.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("PUBLIC_MODE", "1")
os.environ.setdefault("APP_ACCESS_KEY", "transport-demo")
os.environ.setdefault("DATA_DIR", "/tmp/transport-control-desk")


def assemble(paths, dest, expected_sha):
    data = b"".join((PARTS / p).read_bytes() for p in paths)
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_sha:
        raise SystemExit(f"Source integrity check failed for {dest.name}: {actual} != {expected_sha}")
    dest.write_bytes(data)


assemble(
    ["app_01.py.part", "app_02.py.part", "app_03.py.part", "app_04.py.part", "app_05.py.part"],
    TARGET / "app.py",
    "1cffa9449baad0f3958d7249224f0dbfcafb826bf9a3fd1054fa70d3c1b5da8f",
)
assemble(
    ["appjs_01.js.part", "appjs_02.js.part", "appjs_03.js.part"],
    STATIC / "app.js",
    "69ae8af121177d0beb3da9b0ded228f597c83f74ae5b0ccf90e8c88089ace5d4",
)

for name, expected in {
    "index.html": "b4861a1086b3737417099a1bee9a66ceba420daf0cb49803299c90ae094ad056",
    "style.css": "89cad243ac305c1cf0f77d18a4cfa4ee1dcd4193e65c8821a4f53676911c9379",
}.items():
    src = PARTS / name
    data = src.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise SystemExit(f"Source integrity check failed for {name}: {actual} != {expected}")
    (STATIC / name).write_bytes(data)

sys.path.insert(0, str(TARGET))
sys.argv[0] = str(TARGET / "app.py")
runpy.run_path(str(TARGET / "app.py"), run_name="__main__")
