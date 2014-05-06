#!/bin/python3

from subprocess import *
from os.path import getmtime, exists
from time import sleep


def start():
    Popen(["sudo", "/usr/bin/systemctl", "start", "btsync@tellendil"])
    Popen(["/usr/bin/skype"])
    Popen(["/usr/bin/pidgin"])
    if is_charging():  # If only launched if charging
        Popen(["sudo", "/usr/bin/systemctl", "start", "clamd"])
        Popen(["sudo", "/usr/bin/systemctl", "start", "dropbox@tellendil"])


def stop():
    Popen(["sudo", "/usr/bin/systemctl", "stop", "btsync@tellendil"])
    Popen(["sudo", "/usr/bin/systemctl", "stop", "dropbox@tellendil"])
    Popen(["sudo", "/usr/bin/systemctl", "stop", "clamd"])
    Popen(["pkill", "pidgin"])
    Popen(["pkill", "skype"])


def is_charging():
    x = Popen(["acpi", "-b"], stdout=PIPE)
    answer = x.communicate()[0].decode("UTF-8")
    if x.wait() != 0:
        exit(1)
    else:
        return True if (not "Discharging" in answer) else False


def main():
    marker = "/tmp/startupPy"
    if not exists(marker):
        open(marker, 'a').close()
    last_modified = 0
    running = False
    sleep(60)

    while True:
        if exists(marker) and getmtime(marker) > last_modified:
            last_modified = getmtime(marker)
            with open(marker, 'r') as f:
                data = f.read()
            if "start" in data and not running:
                start()
                running = not running
            elif "stop" in data and running:
                stop()
                running = not running
            else:
                open(marker, "w").close()

        sleep(600)


if __name__ == "__main__":
    main()
