import logging
import logging.config
import os


def setup():
    if os.path.isfile("logging.ini"):
        logging.config.fileConfig("logging.ini")
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s [%(pathname)s/%(filename)s:%(funcName)s]",
        )
