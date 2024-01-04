from pathlib import Path


TMP = Path("tmp")
OUT = Path("out")
DOWNLOADED = Path("downloaded")
CONVERTED = Path("converted")
CHECKPOINTS = Path("checkpoints")
_ALL_PATHS = [TMP, OUT, DOWNLOADED, CONVERTED, CHECKPOINTS]


def create_default_folders():
    for path in _ALL_PATHS:
        path.mkdir(parents=True, exist_ok=True)
