import threading
import time

import cv2
import numpy as np
from djitellopy import tello
from flask import Flask, Response, render_template

from config_loader import config
from image_processor import process_frame


# Istanza Flask per servire UI e stream MJPEG.
app = Flask(__name__)

# Lock e cache del client Tello per inizializzazione thread-safe.
tello_lock = threading.Lock()
tello_client = None

# Parametri stream in un solo punto.
FRAME_SIZE = (640, 360)
TARGET_FPS = 30.0


def get_tello_client():
	"""
	Inizializza il client Tello una sola volta e avvia lo stream.
	Ritorna l'istanza condivisa per tutte le richieste.
	"""
	global tello_client

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
				result = process_frame(frame, size=FRAME_SIZE)
				if result.frame is None:
					continue

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

				yield (
					b"--frame\r\n"
					b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
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
