import threading
import time

import cv2
import numpy as np
from colorama import Fore, Style, init as colorama_init
from djitellopy import tello
from flask import Flask, Response, render_template

from config_loader import config
from image_processor import ImageProcessor
from execute import DroneActionExecutor


# Istanza Flask per servire UI e stream MJPEG.
app = Flask(__name__)

# Lock e cache del client Tello per inizializzazione thread-safe.
tello_lock = threading.Lock()
tello_client = None
action_executor = None

# Parametri stream in un solo punto.
stream_cfg = config.get("stream", {})
FRAME_SIZE = (
	int(stream_cfg.get("width", 640)),
	int(stream_cfg.get("height", 360)),
)
TARGET_FPS = float(stream_cfg.get("target_fps", 30.0))

# Processor condiviso per tutte le richieste.
processor = ImageProcessor(config)

# Abilita colori ANSI su Windows.
colorama_init(autoreset=True)


def get_tello_client():
    """
    Inizializza il client Tello una sola volta e avvia lo stream.
    Ritorna l'istanza condivisa per tutte le richieste.
    """
    global tello_client
    global action_executor

    with tello_lock:
        if tello_client is None:
            client = tello.Tello()
            client.connect()
            try:
                # Stop preventivo in caso di stream gia' attivo.
                client.streamoff()
            except Exception:
                pass
            client.streamon()
            # Tempo minimo per agganciare il decoder.
            time.sleep(1.0)
            tello_client = client
            action_executor = DroneActionExecutor(client)
    return tello_client


def generate_mjpeg():
    """
    Generatore MJPEG per lo stream video in pagina.
    Esegue: lettura frame -> elaborazione -> overlay FPS -> encode JPEG.
    """
    width, height = FRAME_SIZE
    min_interval = 1.0 / TARGET_FPS
    last_sent = time.perf_counter()
    fps = 0.0

    while True:
        try:
            client = get_tello_client()
            frame_read = client.get_frame_read()

            while True:
                frame = frame_read.frame
                if frame is None:
                    time.sleep(0.01)
                    continue

                # Tutte le elaborazioni del frame sono nel processor.
                result = processor.process_frame(frame, size=FRAME_SIZE)
                if result.frame is None:
                    continue

                text_results = result.results.get("text_detections", [])
                if text_results:
                    print(f"\n{Fore.GREEN}[OCR]{Style.RESET_ALL} Risultati rilevati")
                    print(f"{Fore.GREEN}{'-' * 48}{Style.RESET_ALL}")
                    for idx, item in enumerate(text_results, start=1):
                        text = item.get("text", "")
                        conf = item.get("confidence", 0)
                        bbox = item.get("bbox", [])
                        print(f"{Fore.CYAN}{idx:02d}.{Style.RESET_ALL} \"{text}\" {Fore.YELLOW}(conf: {conf:.2f}){Style.RESET_ALL}")
                        print(f"    {Fore.LIGHTBLACK_EX}bbox: {bbox}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}{'-' * 48}{Style.RESET_ALL}")

                    # Concatena tutti i testi in una singola stringa e esegui il comando
                    all_texts = " ".join(item.get("text", "") for item in text_results)
                    if action_executor:
                        if action_executor.execute_command(all_texts):
                            print(f"{Fore.MAGENTA}[AZIONE]{Style.RESET_ALL} Comando eseguito: {all_texts}")
                        else:
                            print(f"{Fore.YELLOW}[AZIONE]{Style.RESET_ALL} Nessun comando riconosciuto")

                # Calcolo FPS sulla frequenza reale di invio.
                now = time.perf_counter()
                delta = now - last_sent
                if delta < min_interval:
                    time.sleep(min_interval - delta)
                    now = time.perf_counter()
                    delta = now - last_sent

                fps = (0.9 * fps) + (0.1 * (1.0 / max(delta, 1e-6)))
                last_sent = now

                # Overlay FPS (unico overlay lasciato nel main).
                cv2.putText(
                    result.frame,
                    f"FPS {int(fps)}",
                    (12, 22),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (52, 211, 153),
                    2,
                    cv2.LINE_AA,
                )

                ok, buffer = cv2.imencode(".jpg", result.frame)
                if not ok:
                    continue
                frame_bytes = buffer.tobytes()

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )
        except Exception:
            # Fallback visivo + tentativo di riavvio stream.
            fallback = np.zeros((height, width, 3), dtype=np.uint8)
            cv2.putText(
                fallback,
                "Stream non disponibile",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            ok, buffer = cv2.imencode(".jpg", fallback)
            if ok:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
                )
            try:
                client = get_tello_client()
                client.streamoff()
                time.sleep(0.3)
                client.streamon()
                time.sleep(1.0)
            except Exception:
                pass
            time.sleep(0.5)


@app.route("/")
def index():
    """Pagina principale con UI e tag <img> che carica /stream."""
    return render_template("index.html")


@app.route("/stream")
def stream():
    """Endpoint MJPEG per l'elemento <img> nella UI."""
    return Response(generate_mjpeg(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    # Avvio server Flask con parametri da config.
    host = config["flask"]["host"]
    port = config["flask"]["port"]
    debug = config["flask"].get("debug", True)
    app_name = config["app"].get("name", "TelloDroneAI")

    print(f"\n{'=' * 60}")
    print(f"  {app_name}")
    print(f"{'=' * 60}")
    print(f"  Server:   http://{host}:{port}")
    print(f"  Debug:    {debug}")
    print(f"{'=' * 60}\n")

    # threaded=True serve per gestire la risposta streaming senza bloccare la UI.
    app.run(host=host, port=port, debug=debug, use_reloader=False, threaded=True)
