import logging
import logging.handlers
import os


PATH = "./rule_finder.log"


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)



handler = logging.handlers.RotatingFileHandler(PATH, mode='a')
formatter = logging.Formatter('RuleFinder | {funcName} | {asctime} | {levelname:8s} | {message}',datefmt='%Y-%m-%d %H:%M:%S',style='{')
handler.setFormatter(formatter)


logger.addHandler(handler)