import config as cfg
import json
from urllib.parse import urlparse, parse_qs

from simple_websocket_server import WebSocketServer, WebSocket


# Generate a unique uid that gets embedded in components.html for frontend
# Both frontend and server connect to ws using the same uid
# server sends commands like localStorage_get_key, localStorage_set_key
class SimpleChat(WebSocket):
    uid: str = None
    clients: dict = dict()

    def handle(self):
        cfg.logger.debug('Websocket server handle: ', self.uid, self.data, self.address)

        # Echo back
        try:
            obj = json.loads(self.data)
            if 'cmd' in obj and obj['cmd'] == 'echo':
                self.send_message(self.data)
        except Exception as e:
            cfg.logger.warning(f'exception in handle, ignoring: {e}')

        for client in self.clients[self.uid]:
            if client != self:
                client.send_message(self.data)

    def connected(self):
        cfg.logger.debug('WebSocketServer connected: ', self.address, self.request.path)
        self.uid = self.request.path
        try:
            parsed_url = urlparse(self.request.path)
            d = parse_qs(parsed_url.query)
            if 'uid' in d and len(d['uid']) > 0:
                self.uid = d['uid'][0]
            else:
                self.send_message('No uid found')
                self.close(1, 'No uid found')
                return
        except Exception:
            self.send_message('Exception')
            self.close(2, 'Exception')
            return

        if self.uid not in self.clients:
            self.clients[self.uid] = []
        self.clients[self.uid].append(self)

    def handle_close(self):
        cfg.logger.debug('WebSocketServer: handle_close: ', self.uid, self.address)
        self.clients[self.uid].remove(self)
        print(self.address, 'closed')


def main():
    port = cfg.configuration["WEBSOCKET_SERVER_PORT"]
    server = WebSocketServer('0.0.0.0', port, SimpleChat)
    server.serve_forever()


if __name__ == '__main__':
    main()
