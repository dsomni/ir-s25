import json
import math
import os
from pathlib import Path


def save_json(path: str, data: dict):
    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(data, f, indent=4)


def load_json(path: str) -> dict:
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def save(path: str, data: str):
    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(data)


def load(path: str) -> str:
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        return f.read()


def from_current_file(path: str) -> Path:
    dirname = os.path.dirname(__file__)
    return Path(os.path.join(dirname, path))


def round_float(x: float, places: int = 3) -> float:
    a = 10**places
    return math.ceil(x * a) / a
