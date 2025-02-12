import logging
import logging.handlers


PATH = "./rule_finder.log"
logger = logging.getLogger("aimdm")
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(PATH, mode='a')
formatter = logging.Formatter(
    'RuleFinder | {funcName} | {asctime} | {levelname:8s} | {message}',
    datefmt='%Y-%m-%d %H:%M:%S', style='{')
handler.setFormatter(formatter)

logger.addHandler(handler)

configuration = {
    # Data profiling report will be stored in the following directory under "reports"
    "WWW_ROOT": "/usr/share/nginx/html",
    "remote_url": '127.0.0.1',
    # Change to 8000
    "remote_port": '5000',
    # Port for the web socket server
    "WEBSOCKET_SERVER_URL": "wss://linode.liquidco.in"
}