from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List

import cv2
import yaml


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")


FONT_MAP = {
    "simplex": cv2.FONT_HERSHEY_SIMPLEX,
    "plain": cv2.FONT_HERSHEY_PLAIN,
    "duplex": cv2.FONT_HERSHEY_DUPLEX,
    "complex": cv2.FONT_HERSHEY_COMPLEX,
    "triplex": cv2.FONT_HERSHEY_TRIPLEX,
    "complex_small": cv2.FONT_HERSHEY_COMPLEX_SMALL,
    "script_simplex": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
    "script_complex": cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
}


def parse_text_languages(value: Any, default: str = "en") -> List[str]:
    if isinstance(value, list) and value:
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        langs = [part.strip() for part in value.split(",") if part.strip()]
        return langs or [default]
    return [default]


def parse_text_font(value: Any, default: int) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return FONT_MAP.get(value.lower().strip(), default)
    return default


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
    "stream": {
        "width": 640,
        "height": 360,
        "target_fps": 30.0,
    },
    "processing": {
        "convert_bgr_to_rgb": True,
        "input_color": "bgr",
        "output_color": "rgb",
        "enable_contrast": True,
        "contrast_alpha": 1.05,
        "contrast_beta": 2,
    },
    "text_detection": {
        "enabled": False,
        "language": "en",
        "gpu": False,
        "threshold": 0.7,
        "interval": 1.0,
        "box_color": [0, 255, 0],
        "box_thickness": 1,
        "text_color": [255, 0, 0],
        "text_font_scale": 0.5,
        "text_font_thickness": 1,
        "text_font": "simplex",
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
