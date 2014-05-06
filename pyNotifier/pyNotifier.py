#!/usr/bin/python3
#!Coding: UTF-8

__author__ = 'tellendil'

import socket
import threading
from sys import stderr, path
from os import remove
import configparser

from gi.repository import Notify


CONFIG_PATH = None
CONFIG_NAME = "/pyNotifier.conf"


class NotifierThread(threading.Thread):
    def __init__(self, socket):
        super().__init__()
        self.socket = socket

    def decodeNotification(self, text):
        keywords = ["TITLE=", "MESSAGE=", "ICON=", "URGENCY=", "TIMEOUT="]
        entries = {}
        for key in keywords:
            val = text.find(key)
            if val >= 0: entries[val] = key

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
        finished = False
        text = ""
        while not finished:
            message = self.socket.recv(100)
            if message == b'':
                finished = True
            else:
                text += message.decode("UTF-8")

        (title, message, icon, urgency, timeout) = self.decodeNotification(text)
        Notify.init(title)
        send = Notify.Notification.new(title, message, icon)
        send.set_urgency(urgency)
        send.set_timeout(timeout)
        send.show()


class Server():
    def __init__(self, file, timeout):
        super().__init__()
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socketAddress = file
        try:
            self.socket.bind(self.socketAddress)
        except OSError:
            stderr.write("Could not bind to address {}\n".format(file))
            exit(1)
        self.socket.settimeout(timeout)

    def start(self):
        self.socket.listen(5)
        while True:
            try:
                (clientSocket, address) = self.socket.accept()
                NotifierThread(clientSocket).start()
            except socket.timeout:
                pass
            except KeyboardInterrupt:
                break

        self.socket.close()
        remove(self.socketAddress)


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
    config = configure()
    server = Server(str(config["socket_path"]), float(config["socket_timeout"]))
    server.start()


if __name__ == "__main__":
    main()