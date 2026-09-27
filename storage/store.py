import json
import os
from datetime import date as date_cls
from typing import Optional

import config

PROFILE_FILE = "profile.json"
INTAKE_LOG_FILE = "intake_log.json"


def _path(filename: str) -> str:
    return os.path.join(config.DATA_DIR, filename)


def _read_json(filename: str, default):
    path = _path(filename)
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(filename: str, data) -> None:
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(_path(filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_profile() -> Optional[dict]:
    return _read_json(PROFILE_FILE, None)


def save_profile(profile: dict) -> None:
    _write_json(PROFILE_FILE, profile)


def today_str() -> str:
    return date_cls.today().isoformat()


def append_intake(entry: dict, day: Optional[str] = None) -> None:
    day = day or today_str()
    log = _read_json(INTAKE_LOG_FILE, {})
    log.setdefault(day, []).append(entry)
    _write_json(INTAKE_LOG_FILE, log)


def get_intake(day: Optional[str] = None) -> list:
    day = day or today_str()
    log = _read_json(INTAKE_LOG_FILE, {})
    return log.get(day, [])


def delete_intake(index: int, day: Optional[str] = None) -> Optional[dict]:
    """按 1 开始的序号删除当天某条记录，返回被删的记录；序号越界返回 None。"""
    day = day or today_str()
    log = _read_json(INTAKE_LOG_FILE, {})
    entries = log.get(day, [])
    if index < 1 or index > len(entries):
        return None
    removed = entries.pop(index - 1)
    log[day] = entries
    _write_json(INTAKE_LOG_FILE, log)
    return removed


def update_intake(index: int, entry: dict, day: Optional[str] = None) -> bool:
    """按 1 开始的序号整体替换当天某条记录；序号越界返回 False。"""
    day = day or today_str()
    log = _read_json(INTAKE_LOG_FILE, {})
    entries = log.get(day, [])
    if index < 1 or index > len(entries):
        return False
    entries[index - 1] = entry
    log[day] = entries
    _write_json(INTAKE_LOG_FILE, log)
    return True
