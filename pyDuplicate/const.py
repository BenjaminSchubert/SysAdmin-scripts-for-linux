#!/usr/bin/python3
# -*- coding: utf-8 -*-

#TODO change this in a configuration file

"""
This contains several configuration constants to avoid having a configuration file (may be done later on)
"""

import logging
import sys

import rainbow_logging_handler
from psutil import phymem_usage


__author__ = 'tellendil'

########################
## LOGGER INFORMATION ##
########################

LOGGER = "pyDuplicateLogger"
LOGGER_LEVEL = "NOTSET"

HANDLER_CONSOLE = {
    "class": rainbow_logging_handler.RainbowLoggingHandler,
    "args": sys.stderr,
    "level": "INFO",
    "format": "%(levelname)s : %(message)s"

}

HANDLER_FILE = {
    "class": logging.FileHandler,
    "args": "duplicate.log",
    "level": "WARN",
    "format": "%(asctime)s : %(levelname)s : %(message)s"

}
HANDLERS = [HANDLER_CONSOLE, HANDLER_FILE]

##################
## USAGE CONSTS ##
##################
MAX_MEMORY = phymem_usage()[0] / (4 * 8)  # 4 for 1/4 of the ram, but *8 as we use bytes and not bits

EXTENSIONS_NOT_TO_CHECK = (".log",)
FOLDERS_NOT_TO_CHECK = (
    ".config", ".local", ".cache", ".mozilla", ".PyCharm30", ".eclipse", ".opera", ".filezilla", "git", ".gnupg")
