from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict

import yaml


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")


@dataclass
class AppConfig:
    data: Dict[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]


DEFAULT_CONFIG: Dict[str, Any] = {
    "app": {
        "name": "TelloDroneAI",
        "environment": "development",
    },
    "flask": {
        "host": "127.0.0.1",
        "port": 5000,
        "debug": True,
    },
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str = CONFIG_PATH) -> AppConfig:
    if not os.path.exists(path):
        return AppConfig(DEFAULT_CONFIG)

    with open(path, "r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    merged = _deep_merge(DEFAULT_CONFIG, raw)
    return AppConfig(merged)


config = load_config()
