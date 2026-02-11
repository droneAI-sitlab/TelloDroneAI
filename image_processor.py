from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np

from config_loader import parse_text_font, parse_text_languages

try:
    import easyocr

    EASY_OCR_AVAILABLE = True
except Exception:
    easyocr = None
    EASY_OCR_AVAILABLE = False


@dataclass
class ProcessResult:
    frame: Optional[np.ndarray]
    note: str
    results: Dict[str, Any]


class ImageProcessor:
    def __init__(self, config: Any):
        processing_cfg = config.get("processing", {})
        self.enable_contrast = bool(processing_cfg.get("enable_contrast", True))
        self.contrast_alpha = float(processing_cfg.get("contrast_alpha", 1.05))
        self.contrast_beta = int(processing_cfg.get("contrast_beta", 2))

        td_cfg = config.get("text_detection", {})
        self.ocr_enabled = bool(td_cfg.get("enabled", False))
        self.ocr_interval = float(td_cfg.get("interval", 1.0))
        self.detection_threshold = float(td_cfg.get("threshold", 0.7))

        self.box_color = tuple(td_cfg.get("box_color", [0, 255, 0]))
        self.box_thickness = int(td_cfg.get("box_thickness", 1))

        self.font_color = tuple(td_cfg.get("text_color", [255, 0, 0]))
        self.font_scale = float(td_cfg.get("text_font_scale", 0.5))
        self.font_thickness = int(td_cfg.get("text_font_thickness", 1))
        self.font = parse_text_font(td_cfg.get("text_font", "simplex"), cv2.FONT_HERSHEY_SIMPLEX)

        self.lang_list = parse_text_languages(td_cfg.get("language", "en"), default="en")
        self.gpu_mode = bool(td_cfg.get("gpu", False))

        self.last_ocr_time = 0.0
        self.latest_ocr_results = []
        self.reader = None

        if self.ocr_enabled and EASY_OCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(self.lang_list, gpu=self.gpu_mode)
            except Exception:
                self.reader = easyocr.Reader(["en"], gpu=self.gpu_mode)
        elif self.ocr_enabled and not EASY_OCR_AVAILABLE:
            self.ocr_enabled = False

    def process_frame(
        self,
        frame: np.ndarray,
        size: Optional[Tuple[int, int]] = None,
    ) -> ProcessResult:
        """
        Applica tutte le elaborazioni video centralizzate.
        - Resize opzionale.
        - Leggera normalizzazione del contrasto.
        - OCR opzionale con overlay dei risultati.
        """
        if frame is None or frame.size == 0:
            return ProcessResult(frame=None, note="frame vuoto", results={"text_detections": []})

        working = frame
        if size is not None:
            working = cv2.resize(working, size)

        processed = cv2.cvtColor(working.copy(), cv2.COLOR_BGR2RGB)
        ocr_frame = processed.copy()

        if self.enable_contrast:
            processed = cv2.convertScaleAbs(processed, alpha=self.contrast_alpha, beta=self.contrast_beta)

        results = {"text_detections": []}
        if self.ocr_enabled and self.reader is not None:
            now = time.time()
            if now - self.last_ocr_time >= self.ocr_interval:
                self.latest_ocr_results = self.reader.readtext(ocr_frame)
                self.last_ocr_time = now

            for bbox, text, conf in self.latest_ocr_results:
                if conf < self.detection_threshold:
                    continue
                if not bbox or len(bbox) != 4:
                    continue

                try:
                    pts = np.array(bbox, dtype=np.int32)
                    x, y, w, h = cv2.boundingRect(pts)
                    cv2.rectangle(processed, (x, y), (x + w, y + h), self.box_color, self.box_thickness)
                    cv2.putText(
                        processed,
                        text,
                        (x, max(y - 5, 0)),
                        self.font,
                        self.font_scale,
                        self.font_color,
                        self.font_thickness,
                        cv2.LINE_AA,
                    )
                    results["text_detections"].append(
                        {
                            "text": text,
                            "confidence": float(conf),
                            "bbox": [[int(pt[0]), int(pt[1])] for pt in pts.tolist()],
                        }
                    )
                except Exception:
                    continue

        return ProcessResult(frame=processed, note="ok", results=results)
