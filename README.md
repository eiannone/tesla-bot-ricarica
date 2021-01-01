# Bot Telegram per ricarica programmata Tesla
Bot Telegram che avvia o termina la ricarica di auto Tesla in maniera programmata.
Esempio:

![Schermata bot](https://raw.githubusercontent.com/eiannone/tesla-bot-ricarica/main/schermata.jpg)

*NOTA: Questo repository contiene solo la parte di codice che gestisce il bot Telegram, mentre i comandi di ricarica veri e propri sono in uno script separato.*

# Prerequisiti
* **Python 3**: https://www.python.org/downloads/
* **Creare Bot Telegram e ottenere token**. Il bot di Telegram deve essere creato interagendo con @BotFather (vedere ad esempio queste indicazioni: https://www.html.it/pag/394635/creare-telegram-bot/)
* *(Opzionale)* **Inviare messaggio al bot e ottenere id chat**. Impostando l'id della chat nello script è possibile l'imitare l'interazione con il bot alla sola propria  conversazione privata con il bot. Un metodo per ottenere l'id è quello di inviare un messaggio al bot e poi aprire l'url seguente (sostituendo *##TokenBot##* con il token ottenuto al punto precedente): `https://api.telegram.org/bot##TokenBOT##/getUpdates`. L'identificativo della chat è la proprietà "id" dell'oggetto "chat".
* **Installare script tesla-ricarica**. Lo script che effettua la ricarica va scaricato e installato a parte, si trova qui: https://github.com/eiannone/tesla-ricarica/

Nel caso in cui si voglia usare la funzione WebHook di Telegram, è necessario attivarla preventivamente. Maggiori informazioni nella pagina wiki: https://github.com/eiannone/tesla-bot-ricarica/wiki/Informazioni-per-attivazione-webhook

# Installazione e utilizzo
Copiare il contenuto in una cartella, oppure (con git installato) clonare il repository tramite il comando:
```
git clone https://github.com/eiannone/tesla-bot-ricarica
```
Aprire il file `main.py` e compilare i parametri di configurazione indicati di seguito:
```python
# Token del Bot Telegram
BOT_TOKEN = "123456789:ABCDEFGHIJKLMNOPQRSTUVZ"
# (opzionale) Identificativo della chat a cui limitare la ricezione/invio dei comandi
BOT_CHAT_ID = 0
# Url per la funzione WebHook di Telegram ("None" per disabilitare il WebHook e usare invece getUpdates)
BOT_URL = None  # "https://0.0.0.0:443/bot-ricarica"

# SPECIFICARE I PARAMETRI SEGUENTI SOLO SE SI USA WEBHOOK
# Percorso del file .pem con il certificato TLS/SSL
PEM_FILE = './chiave_pubblica.pem' if BOT_URL else None
# Percorso del file .key con la chiave privata. Opzionale se la chiave privata è già inclusa nel file .pem
KEY_FILE = './chiave_privata.key' if BOT_URL else None

# Comando da eseguire per l'avvio/interruzione della ricarica
CMD_RICARICA = ["node", "/home/pi/tesla-ricarica/ricarica.js"]
```

Avviare il bot con il seguente comando:
```
python main.py
```
### Comandi disponibili
Il bot non distingue tra maiuscole e minuscole.
* **Stato** *(oppure "lista", "elenco", "pianificazione", "programma")*: Mostra la pianificazione attuale di avvio e/o termine della ricarica.
* **Avvia alle h:mm** *(oppure "ricarica alle h:mm")*: Imposta l'inizio della ricarica all'orario indicato (minuti opzionali).
* **Arresta alle h:mm** *(oppure "stop alle h:mm", oppure "interrompi alle h:mm")*: Imposta il termine della ricarica all'orario indicato (minuti opzionali).
* **Annulla avvio** *(oppure "annulla ricarica", "annulla arresta", "annulla stop", "annulla interruzione", "annulla interrompi")*: Annulla la pianificazione inserita di avvio o termine della ricarica.


