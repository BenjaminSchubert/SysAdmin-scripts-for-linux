#!/bin/python3
# -*- coding: utf-8 -*-

"""
This little script is used to automatically start or stop some programs when a marker is set in a file
"""

from subprocess import Popen
from os.path import getmtime, exists
from time import sleep
from sys import stderr
from sys import path
import configparser

CONFIG_PATH = None
CONFIG_NAME = "/pyprogramhandler.conf"


def start(configuration):
    """
    Launches every program listed in the values of the parameter
    @param configuration: dict
    @rtype : NULL
    """
    for i in configuration.values():
        Popen([i])


def stop(configuration):
    """
    Stops every program listed in the values of the parameter
    @param configuration: dict
    @return: NULL
    """
    for i in configuration.values():
        Popen(["pkill", i.split("/")[-1]])


def configure():
    """
    Parses the configuration file
    @return: dict
    """
    conf_path = None
    config_paths = [str(CONFIG_PATH) + CONFIG_NAME, path[0].replace("bin", "etc") + CONFIG_NAME, path[0] + CONFIG_NAME]

    for conf_path in config_paths:
        try:
            with open(conf_path, "r"):
                break
        except (FileNotFoundError, TypeError):
            conf_path = None

    if conf_path is None:
        stderr.write("No configuration file found, exiting\n")
        exit(1)
    config = configparser.ConfigParser()
    config.read(conf_path)

    conf = {}
    for sec in config.sections():
        for option in config.options(sec):
            conf[sec + "_" + option] = config.get(sec, option)

    return conf


def main():
    """
    parses configuration, waits for file to change and starts or stops programs accordingly
    @return: never
    """
    configuration = configure()

    marker = "/tmp/startupPy"
    if not exists(marker):
        open(marker, 'a').close()
    last_modified = 0
    running = False
    sleep(1)

    while True:
        if exists(marker) and getmtime(marker) > last_modified:
            last_modified = getmtime(marker)
            with open(marker, 'r') as file:
                data = file.read()
            if "start" in data and not running:
                start(configuration)
                running = not running
            elif "stop" in data and running:
                stop(configuration)
                running = not running
            else:
                open(marker, "w").close()

        sleep(600)


if __name__ == "__main__":
    main()
