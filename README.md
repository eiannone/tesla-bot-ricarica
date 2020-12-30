# Telegram bot per ricarica programmata Tesla
Bot Telegram che avvia o termina la ricarica di auto Tesla in maniera programmata.
Esempio:

![Schermata bot](https://raw.githubusercontent.com/eiannone/tesla-bot-ricarica/main/schermata.jpg)

NOTA: Questo repository contiene solo la parte di codice che gestisce il bot Telegram, mentre i comandi di ricarica veri e propri sono in uno script separato.
In futuro verranno integrati anche quelli.

# Prerequisiti
* Lo script che effettua la ricarica va scaricato e installato a parte, si trova qui: https://github.com/eiannone/tesla-ricarica/
* Token associato al Bot Telegram. Il bot di Telegram deve essere creato interagendo con @BotFather (vedere ad esempio queste indicazioni: https://www.html.it/pag/394635/creare-telegram-bot/)
* Identificativo della propria chat privata con il bot, sulla quale verranno inviate le risposte e gli aggiornamenti. Un metodo è quello di mandare un messaggio al bot e poi aprire l'url seguente (sostituendo *##TokenBot##* con il token ottenuto al punto precedente): `https://api.telegram.org/bot**TokenBOT**/getUpdates`. L'identificativo della chat è la proprietà "id" dell'oggetto "chat".
* Se lo script del bot viene eseguito su un dominio privo di certificato TLS (ad esempio un PC o un server a casa propria), deve essere generato un certificato "Self signed" che servirà per le connessioni in ingresso da parte di Telegram.
