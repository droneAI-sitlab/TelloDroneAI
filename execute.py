"""
Module per eseguire azioni del drone basate su testo riconosciuto.
Contiene funzioni organizzate per categoria di azione.
"""

import re
import time
from datetime import datetime

import cv2


class DroneActionExecutor:
    """Gestore centralizzato delle azioni del drone."""

    def __init__(self, tello_client):
        """
        Inizializza l'executor con il client Tello.
        
        Args:
            tello_client: Istanza del drone Tello
        """
        self.tello_client = tello_client
        self.commands = get_command_keywords()

    # ============== AZIONI DI VOLO ==============

    def takeoff(self):
        """Decollo del drone."""
        try:
            self.tello_client.takeoff()
            return True
        except Exception as e:
            print(f"Errore durante il decollo: {e}")
            return False

    def land(self):
        """Atterraggio del drone."""
        try:
            self.tello_client.land()
            return True
        except Exception as e:
            print(f"Errore durante l'atterraggio: {e}")
            return False

    def move_forward(self, distance=None):
        """Movimento in avanti."""
        try:
            move_distance = int(distance or 30)
            self.tello_client.move_forward(move_distance)
            return True
        except Exception as e:
            print(f"Errore movimento avanti: {e}")
            return False

    def move_backward(self, distance=None):
        """Movimento indietro."""
        try:
            move_distance = int(distance or 30)
            self.tello_client.move_back(move_distance)
            return True
        except Exception as e:
            print(f"Errore movimento indietro: {e}")
            return False

    def move_left(self, distance=None):
        """Movimento a sinistra."""
        try:
            move_distance = int(distance or 30)
            self.tello_client.move_left(move_distance)
            return True
        except Exception as e:
            print(f"Errore movimento sinistra: {e}")
            return False

    def move_right(self, distance=None):
        """Movimento a destra."""
        try:
            move_distance = int(distance or 30)
            self.tello_client.move_right(move_distance)
            return True
        except Exception as e:
            print(f"Errore movimento destra: {e}")
            return False

    def move_up(self, distance=None):
        """Movimento verso l'alto."""
        try:
            move_distance = int(distance or 30)
            self.tello_client.move_up(move_distance)
            return True
        except Exception as e:
            print(f"Errore movimento alto: {e}")
            return False

    def move_down(self, distance=None):
        """Movimento verso il basso."""
        try:
            move_distance = int(distance or 30)
            self.tello_client.move_down(move_distance)
            return True
        except Exception as e:
            print(f"Errore movimento basso: {e}")
            return False

    def rotate_clockwise(self, angle=None):
        """Rotazione in senso orario."""
        try:
            rotate_angle = int(angle or 90)
            self.tello_client.rotate_clockwise(rotate_angle)
            return True
        except Exception as e:
            print(f"Errore rotazione oraria: {e}")
            return False

    def rotate_counterclockwise(self, angle=None):
        """Rotazione in senso antiorario."""
        try:
            rotate_angle = int(angle or 90)
            self.tello_client.rotate_counter_clockwise(rotate_angle)
            return True
        except Exception as e:
            print(f"Errore rotazione antioraria: {e}")
            return False

    # ============== AZIONI FOTOCAMERA ==============

    def take_photo(self, filename=None):
        """Scatto fotografico."""
        try:
            frame = self.tello_client.get_frame_read().frame
            if frame is None:
                return False
            output_file = filename or f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(output_file, frame)
            return True
        except Exception as e:
            print(f"Errore scatto foto: {e}")
            return False

    def start_recording(self):
        """Avvio registrazione video."""
        print("Registrazione non implementata in questa versione")
        return False

    def stop_recording(self):
        """Arresto registrazione video."""
        print("Registrazione non implementata in questa versione")
        return False

    def get_battery_level(self):
        """Ottiene il livello della batteria."""
        try:
            return self.tello_client.get_battery()
        except Exception as e:
            print(f"Errore lettura batteria: {e}")
            return None

    # ============== AZIONI SPECIALI ==============

    def perform_flip(self, direction=None):
        """Esecuzione di una capriola."""
        try:
            flip_direction = (direction or "forward").lower()
            if flip_direction in ("forward", "f"):
                self.tello_client.flip_forward()
            elif flip_direction in ("back", "backward", "b"):
                self.tello_client.flip_back()
            elif flip_direction in ("left", "l"):
                self.tello_client.flip_left()
            elif flip_direction in ("right", "r"):
                self.tello_client.flip_right()
            else:
                self.tello_client.flip_forward()
            return True
        except Exception as e:
            print(f"Errore durante il flip: {e}")
            return False

    def set_speed(self, speed=None):
        """Impostazione della velocità di movimento."""
        try:
            target_speed = int(speed or 20)
            self.tello_client.set_speed(target_speed)
            return True
        except Exception as e:
            print(f"Errore impostazione velocità: {e}")
            return False

    def hover(self, duration=None):
        """Mantieni il drone fermo in aria."""
        try:
            wait_seconds = float(duration or 1.0)
            if wait_seconds > 0:
                time.sleep(wait_seconds)
            return True
        except Exception as e:
            print(f"Errore hover: {e}")
            return False

    def emergency_stop(self):
        """Arresto d'emergenza del drone."""
        try:
            self.tello_client.emergency()
            return True
        except Exception as e:
            print(f"Errore arresto di emergenza: {e}")
            return False

    def _normalize_action_name(self, action):
        if not action:
            return None

        action_text = str(action).strip().lower()
        alias_map = {
            "take_off": "takeoff",
            "decollo": "takeoff",
            "atterra": "land",
            "move_back": "move_backward",
            "back": "move_backward",
            "move_left": "move_left",
            "left": "move_left",
            "move_right": "move_right",
            "right": "move_right",
            "forward": "move_forward",
            "move_forward": "move_forward",
            "up": "move_up",
            "down": "move_down",
            "rotate_cw": "rotate_clockwise",
            "rotate_ccw": "rotate_counterclockwise",
            "stop": "emergency_stop",
        }
        return alias_map.get(action_text, action_text)

    def execute_action(self, action, argument=None):
        """Esegue una singola azione con argomento opzionale."""
        normalized = self._normalize_action_name(action)
        method = getattr(self, normalized, None)
        if not method or not callable(method):
            return False, f"Azione non supportata: {action}"

        try:
            if argument is None or normalized in ("takeoff", "land", "start_recording", "stop_recording", "emergency_stop"):
                result = method()
            else:
                result = method(argument)

            if isinstance(result, bool):
                return result, "ok" if result else f"Azione fallita: {normalized}"

            return True, result
        except Exception as e:
            return False, str(e)

    def execute_sequence(self, commands, delay_between=0.8):
        """
        Esegue più comandi in sequenza.

        Ogni comando può avere uno di questi formati:
        - {"action": "move_left", "argument": 100}
        - {"azione": "move_left", "argomento": 100}
        - ["move_left", 100]
        """
        if not isinstance(commands, list) or not commands:
            return {
                "success": False,
                "message": "commands deve essere un array non vuoto",
                "results": [],
            }

        results = []
        overall_success = True

        for index, command in enumerate(commands):
            action = None
            argument = None

            if isinstance(command, dict):
                action = command.get("action") or command.get("azione")
                argument = command.get("argument")
                if argument is None:
                    argument = command.get("argomento")
            elif isinstance(command, list) and len(command) > 0:
                action = command[0]
                if len(command) > 1:
                    argument = command[1]

            if not action:
                overall_success = False
                results.append(
                    {
                        "index": index,
                        "action": action,
                        "argument": argument,
                        "success": False,
                        "message": "Formato comando non valido",
                    }
                )
                continue

            success, message = self.execute_action(action, argument)
            if not success:
                overall_success = False

            results.append(
                {
                    "index": index,
                    "action": action,
                    "argument": argument,
                    "success": success,
                    "message": message,
                }
            )

            if index < len(commands) - 1 and delay_between > 0:
                time.sleep(float(delay_between))

        return {
            "success": overall_success,
            "message": "Sequenza completata" if overall_success else "Sequenza completata con errori",
            "results": results,
        }

    # ============== MAPPING TESTO -> AZIONE ==============

    def execute_command(self, text):
        """
        Esegue un'azione basata sul testo riconosciuto.
        
        Args:
            text (str): Testo riconosciuto dall'OCR
            
        Returns:
            bool: True se l'azione è stata eseguita, False altrimenti
        """
        if not text:
            return False
        
        text_upper = text.upper()
        
        for keyword, action in self.commands.items():
            if keyword.upper() in text_upper:
                argument = None
                if action in ("move_forward", "move_backward", "move_left", "move_right", "move_up", "move_down"):
                    argument = parse_distance_from_text(text)
                elif action in ("rotate_clockwise", "rotate_counterclockwise"):
                    argument = parse_angle_from_text(text)
                elif action == "set_speed":
                    argument = parse_speed_from_text(text)

                success, _ = self.execute_action(action, argument)
                return success
        
        return False

    def get_available_commands(self):
        """
        Ritorna la lista dei comandi disponibili.
        
        Returns:
            list: Lista di comandi supportati
        """
        return list(self.commands.keys())


# ============== FUNZIONI HELPER ==============

def parse_distance_from_text(text):
    """
    Estrae la distanza da una stringa di testo.
    
    Args:
        text (str): Testo contenente il valore di distanza
        
    Returns:
        float or None: Distanza estratta o None
    """
    if not text:
        return None
    match = re.search(r"(\d+)", str(text))
    if not match:
        return None
    return int(match.group(1))


def parse_angle_from_text(text):
    """
    Estrae l'angolo da una stringa di testo.
    
    Args:
        text (str): Testo contenente il valore di angolo
        
    Returns:
        float or None: Angolo estratto o None
    """
    if not text:
        return None
    match = re.search(r"(\d+)", str(text))
    if not match:
        return None
    return int(match.group(1))


def parse_speed_from_text(text):
    """
    Estrae la velocità da una stringa di testo.
    
    Args:
        text (str): Testo contenente il valore di velocità
        
    Returns:
        float or None: Velocità estratta o None
    """
    if not text:
        return None
    match = re.search(r"(\d+)", str(text))
    if not match:
        return None
    return int(match.group(1))


def get_command_keywords():
    """
    Ritorna il mapping tra parole chiave e azioni.
    
    Returns:
        dict: Dizionario {parola_chiave: azione}
    """
    return {
        "DECOLLA": "takeoff",
        "ATTERRA": "land",
        "FLIP": "perform_flip",
        "AVANTI": "move_forward",
        "INDIETRO": "move_backward",
        "DIETRO": "move_backward",
        "SINISTRA": "move_left",
        "DESTRA": "move_right",
        "SU": "move_up",
        "GIU": "move_down",
        "SALI": "move_up",
        "SCENDI": "move_down",
        "RUOTA DESTRA": "rotate_clockwise",
        "RUOTA SINISTRA": "rotate_counterclockwise",
        "VELOCITA": "set_speed",
        "STOP": "emergency_stop",
    }
