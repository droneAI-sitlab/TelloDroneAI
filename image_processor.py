from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass
class ProcessResult:
    frame: Optional[np.ndarray]
    note: str


def process_frame(
    frame: np.ndarray,
    size: Optional[Tuple[int, int]] = None,
    contrast_alpha: float = 1.05,
    contrast_beta: int = 2,
) -> ProcessResult:
    """
    Applica tutte le elaborazioni video centralizzate.
    - Converte da BGR a RGB.
    - Resize opzionale.
    - Leggera normalizzazione del contrasto.
    """
    if frame is None or frame.size == 0:
        # Frame non valido: ritorna None per evitare errori a valle.
        return ProcessResult(frame=None, note="frame vuoto")

    # OpenCV fornisce BGR: convertiamo in RGB per uniformare il workflow.
    processed = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    if size is not None:
        # Resize opzionale per ridurre il peso dello stream.
        processed = cv2.resize(processed, size)

    # Contrasto leggermente aumentato per migliorare la leggibilita'.
    processed = cv2.convertScaleAbs(processed, alpha=contrast_alpha, beta=contrast_beta)

    return ProcessResult(frame=processed, note="ok")
