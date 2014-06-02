#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This contains a class to create a simple logger to use for notification
"""

import logging
import logging.config

from pyDuplicate import const


__author__ = 'tellendil'


class Logger:
    """
    This is a singleton class used to send logger informations on different places
    """
    __instance = None

    def __new__(cls):
        if Logger.__instance is None:
            Logger.__instance = object.__new__(cls)
            Logger.__instance.__config_logger__()
        return Logger.__instance

    @staticmethod
    def get_logger():
        """
        returns the logger configured
        """
        return Logger.__instance.__logger

    def __config_logger__(self):
        logger = logging.getLogger(const.LOGGER)
        logger.setLevel(const.LOGGER_LEVEL)

        for handler in const.HANDLERS:
            hand = handler["class"](handler["args"])
            hand.setLevel(handler["level"])
            hand.setFormatter(logging.Formatter(handler["format"]))
            logger.addHandler(hand)

        self.__logger = logger
