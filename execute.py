"""
Module per eseguire azioni del drone basate su testo riconosciuto.
Contiene funzioni organizzate per categoria di azione.
"""


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
        pass

    def move_down(self, distance=None):
        """Movimento verso il basso."""
        pass

    def rotate_clockwise(self, angle=None):
        """Rotazione in senso orario."""
        pass

    def rotate_counterclockwise(self, angle=None):
        """Rotazione in senso antiorario."""
        pass

    # ============== AZIONI FOTOCAMERA ==============

    def take_photo(self, filename=None):
        """Scatto fotografico."""
        pass

    def start_recording(self):
        """Avvio registrazione video."""
        pass

    def stop_recording(self):
        """Arresto registrazione video."""
        pass

    def get_battery_level(self):
        """Ottiene il livello della batteria."""
        pass

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
        pass

    def hover(self, duration=None):
        """Mantieni il drone fermo in aria."""
        pass

    def emergency_stop(self):
        """Arresto d'emergenza del drone."""
        pass

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
                method = getattr(self, action, None)
                if method and callable(method):
                    method()
                    return True
        
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
    pass


def parse_angle_from_text(text):
    """
    Estrae l'angolo da una stringa di testo.
    
    Args:
        text (str): Testo contenente il valore di angolo
        
    Returns:
        float or None: Angolo estratto o None
    """
    pass


def parse_speed_from_text(text):
    """
    Estrae la velocità da una stringa di testo.
    
    Args:
        text (str): Testo contenente il valore di velocità
        
    Returns:
        float or None: Velocità estratta o None
    """
    pass


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
    }
