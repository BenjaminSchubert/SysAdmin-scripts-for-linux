#!/usr/bin/python3
#!Coding: UTF-8

__author__ = 'tellendil'

from sys import stderr, path
import os
import curses
import configparser


CONFIG_PATH = None
CONFIG_NAME = "/pyBackup.conf"


class Backup():
    def __init__(self, configuration):
        self.__destination__ = configuration["backup_destination"]
        self.__backup_list__ = self.__parse_backup_list__()

    def __parse_backup_list__(self):
        return sorted([name.replace("-", " at ") for name in os.listdir(self.__destination__)], reverse=True)[1:]

    def get_backup_list(self):
        return self.__backup_list__


class Window():
    def __init__(self, backup):
        pass


def graphical_handler(screen, backup):
    backups_to_display = backup.get_backup_list()
    for b in backups_to_display:
        screen.addstr(b+"\n")
    screen.refresh()
    screen.getkey()


def launch(backup):
    curses.wrapper(graphical_handler, backup)


def configure():
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
    configuration = configure()
    my_backup = Backup(configuration)
    launch(my_backup)


if __name__ == "__main__":
    main()