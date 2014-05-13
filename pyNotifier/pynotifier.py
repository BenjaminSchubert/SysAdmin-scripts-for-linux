#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This scripts creates a server waiting to read from a socket.
When something arrives, it parses it and displays it on the desktop
"""
__author__ = 'tellendil'

import socket
import threading
from sys import stderr, path
from os import remove
import configparser

from gi.repository import Notify


CONFIG_PATH = None
CONFIG_NAME = "/pynotifier.conf"


class NotifierThread(threading.Thread):
    """
    This Class extends threading.thread to read on a server. It parses the result and shows it
    """

    def __init__(self, _socket):
        super().__init__()
        self.socket = _socket

    @staticmethod
    def decode_notification(text):
        """
        This decodes the notification
        Keywords searched are : "TITLE="; "MESSAGE=";"ICON=";"URGENCY=";"TIMEOUT="
        :param text: the string to decode and display
        :return: the parsed text
        """
        keywords = ["TITLE=", "MESSAGE=", "ICON=", "URGENCY=", "TIMEOUT="]
        entries = {}
        for key in keywords:
            val = text.find(key)
            if val >= 0:
                entries[val] = key

        order = sorted(entries.keys())
        result = {}
        for i in range(len(order) - 1):
            item = entries[order[i]]
            beginning = order[i] + len(item)
            end = int(order[i + 1])
            result[item] = text[beginning:end]
            result[entries[order[i + 1]]] = text[end + len(entries[order[i + 1]]):]

        for key in keywords:
            if key not in result.keys():
                if key == "URGENCY=":
                    result["URGENCY="] = 1
                elif key == "TIMEOUT=":
                    result["TIMEOUT="] = 30
                else:
                    result[key] = ""

        return result["TITLE="].strip(), result["MESSAGE="].strip(), result["ICON="].strip(), int(
            result["URGENCY="]), int(result["TIMEOUT="])

    def run(self):
        """
        Reads the text incoming, decodes it and shows it
        """
        finished = False
        text = ""
        while not finished:
            message = self.socket.recv(100)
            if message == b'':
                finished = True
            else:
                text += message.decode("UTF-8")

        (title, message, icon, urgency, timeout) = self.decode_notification(text)
        Notify.init(title)
        send = Notify.Notification.new(title, message, icon)
        send.set_urgency(urgency)
        send.set_timeout(timeout)
        send.show()


class Server():
    """
    This is the server. It opens a socket, wait for a connection and create a new NotifierThread to handle it
    """

    def __init__(self, file, timeout):
        super().__init__()
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket_address = file
        try:
            self.socket.bind(self.socket_address)
        except OSError:
            stderr.write("Could not bind to address {}\n".format(file))
            exit(1)
        self.socket.settimeout(timeout)

    def start(self):
        """
        Starts the server
        """
        self.socket.listen(5)
        while True:
            try:
                (client_socket, _) = self.socket.accept()
                NotifierThread(client_socket).start()
            except socket.timeout:
                pass
            except KeyboardInterrupt:
                break

        self.socket.close()
        remove(self.socket_address)


def configure():
    """
    Reads the configuration file and parses it
    :return a dictionnary containing everything found in the configuration file
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
    Reads the configuration, and launch the server
    """
    config = configure()
    server = Server(str(config["socket_path"]), float(config["socket_timeout"]))
    server.start()


if __name__ == "__main__":
    main()
