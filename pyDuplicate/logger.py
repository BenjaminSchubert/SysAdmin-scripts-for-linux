#!/usr/bin/python3
#!Coding: UTF-8

import logging
import logging.config

from pyDuplicate import const


__author__ = 'tellendil'


class Logger:
    __instance = None

    def __new__(cls):
        if Logger.__instance is None:
            Logger.__instance = object.__new__(cls)
            Logger.__instance.__configLogger__()
        return Logger.__instance

    @staticmethod
    def get_logger():
        return Logger.__instance.__logger

    def __configLogger__(self):
        logger = logging.getLogger(const.LOGGER)
        logger.setLevel(const.LOGGER_LEVEL)

        for handler in const.HANDLERS:
            hand = handler["class"](handler["args"])
            hand.setLevel(handler["level"])
            hand.setFormatter(logging.Formatter(handler["format"]))
            logger.addHandler(hand)

        self.__logger = logger


def main():
    Logger().get_logger().warn("test")
    Logger().get_logger().warn("test1")
    Logger().get_logger().warn("test2")


if __name__ == "__main__":
    main()