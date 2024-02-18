from pathlib import Path


TMP = Path("tmp").absolute()
OUT = Path("out").absolute()
DOWNLOADED = Path("downloaded").absolute()
CONVERTED = Path("converted").absolute()
CHECKPOINTS = Path("ckpts").absolute()
_ALL_PATHS = [TMP, OUT, DOWNLOADED, CONVERTED, CHECKPOINTS]


def create_default_folders():
    for path in _ALL_PATHS:
        path.mkdir(parents=True, exist_ok=True)
