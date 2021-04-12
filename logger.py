import logging
# import sys
from logging.handlers import TimedRotatingFileHandler


FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "my_app.log"

# def get_console_handler():
#     console_handler = logging.StreamHandler(sys.stdout)
#     console_handler.setFormatter(FORMATTER)
#     return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight', encoding='utf-8')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(__name__):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger
