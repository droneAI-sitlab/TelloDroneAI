# TelloDroneAI

Interfaccia Flask per stream video Tello + invio comandi in sequenza.

## Formato comandi sequenziali

L'endpoint `POST /api/commands` accetta un array di comandi.

Formato consigliato:

```json
{
	"commands": [
		{ "action": "takeoff" },
		{ "action": "move_left", "argument": 100 },
		{ "action": "move_forward", "argument": 80 },
		{ "action": "land" }
	]
}
```

Sono supportati anche:

- chiavi italiane: `azione` e `argomento`
- comandi come array: `["move_left", 100]`

## Chat comandi nella UI

Nella pagina principale è presente una sezione **Chat comandi** che permette di inviare:

- testo libero separato da virgole, esempio: `takeoff, move_left 100, land`
- JSON array completo

La chat mostra il risultato di ogni comando della sequenza (ok/errore).

