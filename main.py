import telegram_bot
from apscheduler.schedulers.background import BackgroundScheduler
import json
from os import path
import time
import subprocess
import re
from datetime import datetime, timedelta

# Url del web server che verrà contattato da Telegram
BOT_URL = "https://0.0.0.0:443/bot-ricarica"
# Token del Bot Telegram
BOT_TOKEN = "123456789:ABCDEFGHIJKLMNOPQRSTUVZ"
# (opzionale) Identificativo della chat a cui limitare la ricezione/invio dei comandi
BOT_CHAT_ID = 0

# Percorso del file .pem con il certificato TLS/SSL
PEM_FILE = "./file_certificato.pem"
# Percorso del file .key con la chiave privata. Opzionale se la chiave privata è già inclusa nel file .pem
KEY_FILE = None

# Comando da eseguire per l'avvio/interruzione della ricarica
CMD_RICARICA = ["node", "/home/pi/tesla-ricarica/ricarica.js"]

# File in cui verranno salvate le pianificazioni attive
SCHEDULED_JOBS_FILE = "./jobs.json"

bot = telegram_bot.BotServer(BOT_URL, BOT_TOKEN, BOT_CHAT_ID)
scheduler = BackgroundScheduler()
schedule = json.load(open(SCHEDULED_JOBS_FILE)) if path.exists(SCHEDULED_JOBS_FILE) else {"start": "", "stop": ""}


def log(msg):
    now = time.time()
    year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
    print("[%04d-%02d-%02d %02d:%02d:%02d] %s" % (year, month, day, hh, mm, ss, msg), flush=True)


def ricarica(tipo):
    bot.send_message("%s ricarica..." % ("Avvio" if tipo == "start" else "Arresto"))
    subprocess.call(CMD_RICARICA + [tipo])
    schedule[tipo] = ""
    with open(SCHEDULED_JOBS_FILE, "w") as outfile:
        json.dump(schedule, outfile)


def msg_ricevuto(msg):
    log(f"Ricevuto messaggio: '{msg}'")
    msg = msg.lower().strip()
    m = re.search(r"(avvia|ricarica|stop|interrompi|arresta) all(?:e |')([\d]+)[:.]?([\d]{2}|)", msg)
    if m:
        start = (m.group(1) == "avvia" or m.group(1) == "ricarica")
        ore = int(m.group(2))
        minuti = int(m.group(3)) if m.group(3) else 0
        dt = datetime.now().replace(hour=ore, minute=minuti, second=0)
        if dt < datetime.now():
            dt += timedelta(days=1)

        tipo = "start" if start else "stop"
        # Se già presente stessa richiesta, la sostituisce
        if scheduler.get_job(tipo):
            scheduler.remove_job(tipo)
            bot.send_message("(pianificazione %s esistente annullata)" % ("avvio" if start else "arresto"))

        scheduler.add_job(ricarica, 'date', run_date=dt, args=[tipo], id=tipo)
        schedule[tipo] = dt.strftime("%Y-%m-%d %H:%M:%S")
        with open(SCHEDULED_JOBS_FILE, "w") as outfile:
            json.dump(schedule, outfile)
        bot.send_message("Ok. La ricarica verrà %s alle ore %s" %
                         (("avviata" if start else "interrotta"), dt.strftime("%-H:%M del %d/%m/%Y")))
    elif msg.startswith("annull"):
        m = re.search(r"annull[oa] (avvio|ricarica|stop|interrompi|arresta|interruzione)", msg)
        start = (m.group(1) == "avvio" or m.group(1) == "ricarica")
        tipo = "start" if start else "stop"
        if scheduler.get_job(tipo):
            scheduler.remove_job(tipo)
            bot.send_message("Pianificazione %s esistente annullata" % ("avvio" if start else "arresto"))
        else:
            bot.send_message("Nessuna pianificazione %s da annullare!" % ("avvio" if start else "arresto"))
        schedule[tipo] = ""
    elif msg in ["lista", "pianificazione", "elenco", "programma", "stato"]:
        if schedule["start"] == "" and schedule["stop"] == "":
            risposta = "Nessuna pianificazione in programma"
        else:
            risposta = "Pianificazione:"
            if schedule["start"] != "":
                dt_start = datetime.strptime(schedule["start"], "%Y-%m-%d %H:%M:%S")
                risposta += "\r\nAvvio previsto alle %s" % dt_start.strftime("%-H:%M")
            if schedule["stop"] != "":
                dt_stop = datetime.strptime(schedule["stop"], "%Y-%m-%d %H:%M:%S")
                risposta += "\r\nArresto previsto alle %s" % dt_stop.strftime("%-H:%M")
        bot.send_message(risposta)
    else:
        bot.send_message("Non ho capito!")


telegram_bot.onLog = log
telegram_bot.onMessage = msg_ricevuto

scheduler.start()
# Verifica se esistono delle pianificazioni ancora da elaborare
for j_tipo, strDt in schedule.items():
    if strDt == "":
        continue
    d = datetime.strptime(strDt, "%Y-%m-%d %H:%M:%S")
    scheduler.add_job(ricarica, 'date', run_date=d, args=[j_tipo], id=j_tipo)
    bot.send_message("La ricarica verrà %s alle ore %s" %
                     (("avviata" if j_tipo == "start" else "interrotta"), d.strftime("%-H:%M del %d/%m/%Y")))

bot.start(PEM_FILE, KEY_FILE)
