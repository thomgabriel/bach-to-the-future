import logging
import traceback
import sys
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_db(name, extension='.csv',level=logging.INFO, getHandler = False):
    """Setup writer that formats data to csv, supports multiple instances with no overlap."""
    formatter = logging.Formatter(fmt='%(asctime)s,%(message)s', datefmt='%d-%m-%y,%H:%M:%S')
    date = datetime.today().strftime('%Y-%m-%d')
    log_path = str('data/' + name + '_' + date + extension)

    handler = RotatingFileHandler(log_path, maxBytes=100000000, backupCount=1)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    if getHandler:
        return logger, handler
    else:
        return logger

def setup_logger():
    '''Prints logger info to terminal'''
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger