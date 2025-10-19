import os
import json

with open("cookiecutter.json", "r+") as f:
    data = json.load(f)
    build_dir = data["build_directory"].replace("\\", "/")
    if build_dir.startswith("~"):
        build_dir = os.path.expanduser(build_dir)
    data["build_directory"] = build_dir.replace("\\", "/")
    f.seek(0)
    json.dump(data, f, indent=4)
    f.truncate()
