from time import time, localtime
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


class BotServer(HTTPServer):
    def __init__(self, hook_url: str, token: str, chat_id: int = 0):
        """Constructor.  May be extended, do not override."""
        url = urlparse(hook_url)
        self.address = (url.hostname, url.port or 80)
        self.path = url.path
        self.token = token
        self.chat_id = chat_id
        self.restrict_chat_id = (chat_id > 0)

        HTTPServer.__init__(self, self.address, _BotRequestHandler, False)

    def start(self, cert_file: str, key_file: str = None):
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
            self.serve_forever(1)
        except KeyboardInterrupt:
            pass
        self.server_close()
        log("Arresto bot server")

    def on_web_hook(self, req_handler: _BotRequestHandler):
        try:
            if self.path and req_handler.path != self.path:
                raise Exception("Percorso non valido")

            req = json.loads(req_handler.rfile.read(int(req_handler.headers['Content-Length'])))
            chat_id = int(req['message']['from']['id'])
            if not self.restrict_chat_id:
                self.chat_id = chat_id
            elif chat_id != self.chat_id:
                raise Exception(f"Mittente non valido: {chat_id}")

            req_handler.send_ok()
            if callable(onMessage):
                onMessage(req['message']['text'])
        except Exception as ex:
            req_handler.send_bad_request()
            log("*** Errore [" + type(ex).__name__ + "]: " + str(ex) + " ***")

    def send_message(self, msg: str, chat_id: int = 0):
        post(f"https://api.telegram.org/bot{self.token}/sendMessage", json={
            "chat_id": chat_id if chat_id > 0 else self.chat_id,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        })
        log(f"Inviato messaggio: '{msg}'")
