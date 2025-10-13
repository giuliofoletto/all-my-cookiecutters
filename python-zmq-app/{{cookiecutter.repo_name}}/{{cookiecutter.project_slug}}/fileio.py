import json
import tomllib
from pathlib import Path

import networkx as nx


def process_existing_file_name(file_name, folders=[], formats=[]):
    base_candidates = [Path(file_name)]
    for folder in folders:
        base_candidates.append(
            Path(__file__).parent.parent.absolute() / folder / file_name
        )
    candidates = []
    for base in base_candidates:
        candidates.append(base)
        for format in formats:
            candidates.append(base.with_suffix(format))
    file_found = False
    path = None
    for candidate in candidates:
        if candidate.exists():
            path = candidate
            file_found = True
            break
    if not file_found:
        raise FileNotFoundError("File not found")
    else:
        return path


def process_directory_name(directory_name=None, default=None):
    if directory_name is None:
        if default is None:
            directory_path = Path(__file__).parent.parent.absolute()
        else:
            directory_path = Path(__file__).parent.parent.absolute() / default
    else:
        directory_path = Path(directory_name)
    directory_path.mkdir(parents=True, exist_ok=True)
    return directory_path


def process_default_path_prefix_input(path, prefix):
    if path is None:
        path = Path.cwd()
    prefix_sep = "_"
    if prefix is None or len(prefix) == 0:
        prefix = ""
        prefix_sep = ""
    else:
        if prefix[-1] == prefix_sep:
            prefix_sep = ""
    return path, prefix, prefix_sep


def read_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def read_toml(file_path):
    with open(file_path, "rb") as f:
        data = tomllib.load(f)
    return data


def read_config_file(file_path):
    supported_formats = ["JSON", "TOML"]
    reading_functions = [read_json, read_toml]
    for func in reading_functions:
        try:
            data = func(file_path)
            return data
        except (json.decoder.JSONDecodeError, tomllib.TOMLDecodeError):
            pass
    # If we arrive here, there has been an issue in all reading functions
    raise ValueError(
        "File "
        + file_path
        + " is not valid in any of the supported formats ("
        + ",".join(supported_formats)
        + ")"
    )

