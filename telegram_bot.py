from time import time, localtime, sleep
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from ssl import wrap_socket
from requests import post
import json

onMessage = None
onLog = None


def log(msg):
    if callable(onLog):
        onLog(msg)
    else:
        now = time()
        year, month, day, hh, mm, ss, x, y, z = localtime(now)
        print("[%04d-%02d-%02d %02d:%02d:%02d] %s" % (year, month, day, hh, mm, ss, msg))


class BotRicarica:
    def __init__(self, token: str, chat_id: int = 0, hook_url: str = None):
        self.token = token
        self.chat_id = chat_id
        self.restrict_chat_id = (chat_id > 0)
        self.server = _BotServer(self, hook_url) if hook_url else None

    def start(self, cert_file: str = None, key_file: str = None):
        if self.server and cert_file:
            self.server.start(cert_file, key_file, 1)
        else:
            # Avvio polling
            log("Avvio bot server (getUpdates)")
            update_id = None
            while True:
                try:
                    resp = post("https://api.telegram.org/bot%s/getUpdates" % self.token, timeout=30, json={
                        "offset": update_id,
                        "timeout": 10
                    })
                    if resp.status_code != 200:
                        raise Exception(resp.reason + " (" + str(resp.status_code) + ")")
                    res = json.loads(resp.content.decode('utf-8'))
                    if not res["ok"]:
                        raise Exception(resp.content.decode('utf-8'))
                    for r in res["result"]:
                        update_id = r['update_id'] + 1
                        self.receive_message(r['message']['text'], r['message']['chat']['id'])
                except KeyboardInterrupt:
                    log("Arresto bot server")
                    break
                except Exception as ex:
                    log("*** Errore [" + type(ex).__name__ + "]: " + str(ex) + " ***")
                    sleep(5)

    def receive_message(self, msg: str, chat_id: int):
        if not self.restrict_chat_id:
            self.chat_id = chat_id
        elif chat_id != self.chat_id:
            raise Exception("Mittente non valido: %s" % chat_id)
        log("Ricevuto messaggio: '%s'" % msg)
        if callable(onMessage):
            onMessage(msg)

    def send_message(self, msg: str, chat_id: int = 0):
        post("https://api.telegram.org/bot%s/sendMessage" % self.token, json={
            "chat_id": chat_id if chat_id > 0 else self.chat_id,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        })
        log("Inviato messaggio: '%s'" % msg)


class _BotRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        log("%s (%s) %s" % (self.headers["Host"], self.address_string(), fmt % args))

    def send_response(self, code, message=None):
        self.log_message('"%s" %s', self.requestline, str(code))
        self.send_response_only(code, message)

    def send_ok(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')

    def send_bad_request(self):
        self.send_response(400)
        self.send_header("Content-length", "0")
        self.end_headers()

    def do_GET(self):
        self.send_bad_request()

    def do_POST(self):
        self.server.on_web_hook(self)


class _BotServer(HTTPServer):
    def __init__(self, controller: BotRicarica, hook_url: str):
        """Constructor.  May be extended, do not override."""
        self.bot_controller = controller
        url = urlparse(hook_url)
        self.address = (url.hostname, url.port or 80)
        self.path = url.path
        HTTPServer.__init__(self, self.address, _BotRequestHandler, False)

    def start(self, cert_file: str, key_file: str = None, poll_interval: int = 1):
        try:
            self.server_bind()
            self.server_activate()
            self.socket = wrap_socket(self.socket, server_side=True, certfile=cert_file, keyfile=key_file)
        except:
            log("*** Errore. Impossibile avviare il server. ***")
            self.server_close()
            raise

        log("Avvio bot server - %s:%s" % self.address)
        try:
            self.serve_forever(poll_interval)
        except KeyboardInterrupt:
            pass
        self.server_close()
        log("Arresto bot server")

    def on_web_hook(self, req_handler: _BotRequestHandler):
        try:
            if self.path and req_handler.path != self.path:
                raise Exception("Percorso non valido")

            req = json.loads(req_handler.rfile.read(int(req_handler.headers['Content-Length'])))
            self.bot_controller.receive_message(req['message']['text'], int(req['message']['from']['id']))
            req_handler.send_ok()
        except Exception as ex:
            req_handler.send_bad_request()
            log("*** Errore [" + type(ex).__name__ + "]: " + str(ex) + " ***")
