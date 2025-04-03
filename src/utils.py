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


def parse_document_content(content: str) -> dict:
    result = {
        "element_type": "",
        "full_name": "",
        "module_name": "",
        "parameters": "",
        "description": "",
    }

    if not content:
        return result

    # Split into sections
    sections = content.split("\n\n")

    # First line is always element type
    if sections:
        result["element_type"] = sections[0].strip()

    # Second section contains name and module
    if len(sections) > 1:
        name_module = sections[1]
        if "FROM" in name_module:
            name_part, module_part = name_module.split("FROM", 1)
            result["full_name"] = name_part.strip()
            result["module_name"] = module_part.strip()

    for section in sections[2:]:
        if section.startswith("PARAMETERS"):
            result["parameters"] = section.removeprefix("PARAMETERS").strip()
            continue
        if section.startswith("DESCRIPTION"):
            result["description"] = section.removeprefix("DESCRIPTION").strip()
            continue

    return result
