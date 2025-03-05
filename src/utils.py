import json


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
