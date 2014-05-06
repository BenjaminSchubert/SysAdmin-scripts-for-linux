#!/usr/bin/python3

import subprocess
import socket
import configparser
from sys import stderr, path

CONFIG_PATH = None
CONFIG_NAME = "/pyArchup.conf"


def check_updates(command):
    pr = subprocess.Popen(command, stdout=subprocess.PIPE)
    output = pr.stdout.read()
    if not pr.wait():
        return output.decode("UTF-8").split("\n")
    else:
        pass


def parse_packages(pa):
    return [p.split("/")[1].split(" ")[0] for p in pa[:-1]]


def notify_update(packages, title, icon, timeout, urgency, notifier_address):
    message = "- " + "\n- ".join(packages)

    send = "TITLE={} MESSAGE={} ICON={} TIMEOUT={} URGENCY={}".format(title, message, icon, timeout, urgency)

    my_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    my_socket.connect(notifier_address)
    my_socket.send(send.encode("UTF-8"))


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
    packages_to_update = check_updates([configuration["package_manager_command"],
                                        configuration["package_manager_arguments"]])
    if packages_to_update != "":
        packages = parse_packages(packages_to_update)
        notify_update(packages, title=configuration["notification_name"],
                      icon=configuration["notification_icon"],
                      timeout=int(configuration["notification_timeout"]),
                      urgency=int(configuration["notification_urgency"]),
                      notifier_address=configuration["notification_notifier_address"])
    else:
        exit(0)


if __name__ == "__main__":
    main()
