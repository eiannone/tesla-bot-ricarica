# Telegram bot per ricarica programmata Tesla
Bot Telegram che avvia o termina la ricarica di auto Tesla in maniera programmata.
Esempio:

![Schermata bot](https://raw.githubusercontent.com/eiannone/tesla-bot-ricarica/main/schermata.jpg)

NOTA: Questo repository contiene solo la parte di codice che gestisce il bot Telegram, mentre i comandi di ricarica veri e propri sono in uno script separato.
In futuro verranno integrati anche quelli.

# Prerequisiti
* **Creare Bot Telegram e ottenere token**. Il bot di Telegram deve essere creato interagendo con @BotFather (vedere ad esempio queste indicazioni: https://www.html.it/pag/394635/creare-telegram-bot/)
* **Aprire una chat col bot e ottenere id**. E' necessario ottenere l'identificativo della propria chat privata con il bot, sulla quale verranno inviate le risposte e gli aggiornamenti. Un metodo è quello di mandare un messaggio al bot e poi aprire l'url seguente (sostituendo *##TokenBot##* con il token ottenuto al punto precedente): `https://api.telegram.org/bot##TokenBOT##/getUpdates`. L'identificativo della chat è la proprietà "id" dell'oggetto "chat".
* **Attivare Webhook per il bot**. La ricezione dei messaggi da parte del bot avviene mediante la funzione Webhook (qui le indicazioni per attivarla: https://core.telegram.org/bots/webhooks). L'argomento è un po' complesso, fare riferimento al paragrafo successivo per alcune ulteriori indicazioni.
* **Installare script tesla-ricarica**. Lo script che effettua la ricarica va scaricato e installato a parte, si trova qui: https://github.com/eiannone/tesla-ricarica/


# Istruzioni attivazione webhook
## 1. Certificato TLS
La connessione tramite webhook avviene tramite protocollo https, quindi è necessario che lo script venga eseguito su un server ospitato su un dominio dotato di certificato SSL/TLS.
Se lo script è ospitato su un server on line, accessibile tramite protocollo https, allora non è necessario fare nulla, altrimenti deve essere installato un certificato, oppure può essere generato un certificato "self-signed".

### Generazione certificato self-signed
Installare openssl. Su linux:
```bash
sudo apt install openssl
```
Su windows: scaricare la libreria da qui: https://wiki.openssl.org/index.php/Binaries

Generare certificato:
```
openssl req -newkey rsa:2048 -sha256 -nodes -keyout chiave_privata.key -x509 -days 3650 -out chiave_pubblica.pem
```
In fase di generazione del certificato, specificare il dominio su cui il bot sarà ospitato, come nell'esempio seguente:
```
Common Name (e.g. server FQDN or YOUR name) []:pippo.it
```
Istruzioni dettagliate qui: http://www.megalab.it/7090/come-generare-certificati-digitali-con-openssl-windows-e-linux

## 2. Predisposizione web server
Assicurarsi che il server su cui verrà installato lo script sia accessibile pubblicamente tramite protocollo https su una delle seguenti porte: 443, 80, 88 oppure 8443.

### Port-forwarding se il server è in casa
Se il server è all'interno di una rete casalinga, sarà necessario esporre la porta pubblicamente tramite un'apposita configurazione di port-forwarding sul router di casa.
La configurazione dipende dal modello di router, quindi è necessario trovare le istruzioni di port-forwarding specifiche per il proprio modello.

### DNS dinamico se l'ip non è statico
Se il proprio fornitore di connessione internet non fornisce un un indirizzo ip statico, è necessario utilizzare un servizio di DNS dinamico, che consente di accedere al server utilizzando sempre lo stesso url.
E' possibile ottenere questo servizio gratuitamente tramite diversi siti, come https://dyndns.it/ oppure https://www.dynu.com/

## 3. Attivazione webhook
Una volta identificato l'url pubblico del server su cui sarà installato il bot di telegram, è necessario attivare la funzione webhook.
Per attivare i webhook nel caso di bot ospitato su server dotato di certificato TLS normale (non self-signed) è sufficiente andare a questo url:
```
https://api.telegram.org/bot<bot-token>/setWebhook?url=<url-telegram-bot>
```
Sostituire `<bot-token>` con il token del proprio bot (ad esempio `123456789:ABCDEFGHIJKLMNOPQRSTUVZ`) e `<url-telegram-bot>` con l'indirizzo a cui il bot riceverà gli aggiornamenti sui messaggi inviati tramite telegram.

Nel caso di server con certificato self-signed, è necessario inviare anche la chiave pubblica (il file `chiave_pubblica.pem` generato tramite openssl).
Su linux è possibile usare curl con il seguente comando:
```
curl -F "url=<url-telegram-bot>" -F "certificate=@chiave_pubblica.pem" https://api.telegram.org/bot<bot-token>/setWebhook
```
