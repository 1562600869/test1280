import json
import os
import shutil
import tempfile

DATA_PATH = os.path.expanduser("~/.stage_mgr.json")


def _default_data():
    return {"stages": {}, "applications": {}}


def load():
    if not os.path.exists(DATA_PATH):
        return _default_data()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "stages" not in data:
        data["stages"] = {}
    if "applications" not in data:
        data["applications"] = {}
    return data


def save(data):
    dir_path = os.path.dirname(DATA_PATH)
    fd, tmp_path = tempfile.mkstemp(suffix=".json", dir=dir_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        shutil.move(tmp_path, DATA_PATH)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def transaction(fn):
    def wrapper(*args, **kwargs):
        data = load()
        result = fn(data, *args, **kwargs)
        save(data)
        return result
    return wrapper
