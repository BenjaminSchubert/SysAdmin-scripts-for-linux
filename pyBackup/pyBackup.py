#!/usr/bin/python3
#!Coding: UTF-8

__author__ = 'tellendil'

from datetime import datetime
from sys import stderr, path
import subprocess
import shutil
import os
import time
from math import floor
import socket
import configparser

from psutil import disk_usage


CONFIG_PATH = None
CONFIG_NAME = "/pyBackup.conf.local"


class Timer():
    def __init__(self):
        self.__beginning__ = None

    def start_timer(self):
        self.__beginning__ = time.time()

    @staticmethod
    def __format_time__(time_sec):
        time_sec, t_seconds = divmod(time_sec, 60)
        time_sec, t_minutes = divmod(time_sec, 60)
        time_sec, t_hours = divmod(time_sec, 24)
        t_days = time_sec

        if t_days != 0:
            return "{days}D - {hours}:{minutes}:{seconds}".format(days=t_days, hours=t_hours, minutes=t_minutes,
                                                                  seconds=t_seconds)
        else:
            return "{hours}:{minutes}:{seconds}".format(hours=t_hours, minutes=t_minutes, seconds=t_seconds)

    def elapsed_time(self):
        if self.__beginning__ is None:
            return -1

        else:
            time_sec = floor(time.time() - self.__beginning__)
            return self.__format_time__(time_sec)


class Syncer():
    def __init__(self, configuration):
        self.source = configuration["backup_source"]
        self.destination = configuration["backup_destination"]
        self.exclude = configuration["rsync_command_exclude"]

        self.date = datetime.now().strftime(configuration["backup_date_format"])
        self.timer = Timer()

        self.notifier_address = configuration["Notification_socket_address"]
        self.timeout = configuration["Notification_timeout"]

        self.rsync_command = " ".join([
            "rsync",
            "-aAXHP",
            "--link-dest=" + self.destination + "/current",
            "--exclude={" + self.exclude + "}",
            self.source,
            self.destination + "/incomplete"
        ])

    def run(self):
        self.timer.start_timer()
        self.pre_sync()
        self.sync()
        self.post_sync()
        self.notify_end()

    def pre_sync(self):
        try:
            shutil.rmtree(self.destination + "/incomplete")
        except FileNotFoundError:
            return 0
        except PermissionError:
            self.handle_errors(["preSyncError"])

    def sync(self):
        rsync = subprocess.Popen(self.rsync_command, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, shell=True)
        errors = rsync.stderr.read().decode("UTF-8")[:-1].split("\n")
        exit_code = rsync.wait()
        if exit_code:
            self.handle_errors(errors)

    def post_sync(self):
        os.rename(self.destination + "/incomplete", self.destination + "/" + self.date)
        try:
            os.remove(self.destination + "/current")
        except FileNotFoundError:
            pass
        os.symlink(self.destination + "/" + self.date, self.destination + "/current")

    def notify_end(self):
        space_left = 100 - disk_usage(self.destination)[3]
        message = "Backup finished successfully !\nIt took {timeElapsed}.\n\nSpace left on disk : {space}%".format(
            timeElapsed=self.timer.elapsed_time(), space=space_left)
        title = "backup.py"
        timeout = self.timeout
        urgency = 1
        if space_left > 30:
            icon = "security-high"
        elif space_left > 15:
            icon = "security-low"
        else:
            icon = "software-update-urgent"

        send = "TITLE={} MESSAGE={} ICON={} TIMEOUT={} URGENCY={}".format(title, message, icon, timeout, urgency)

        my_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        my_socket.connect(self.notifier_address)
        my_socket.send(send.encode("UTF-8"))

    def handle_errors(self, errors):
        for e in errors:
            if "file has vanished" in e:
                pass
            elif "link_stat" in e and "No such file or directory (2)" in e:
                stderr.write("The source \"" + self.source + "\" doesn't exists\n")
                exit(1)
            elif "opendir" in e and "Permission denied (13)" in e:
                stderr.write("The source \"" + self.source + "\" is not readable\n")
                exit(2)
            elif "mkdir" in e and "failed" in e and "No such file or directory (2)" in e:
                stderr.write("The destination folder \"" + self.destination + "\" doesn't exists\n")
                exit(4)
            elif "ERROR: cannot stat destination" in e and "Permission denied (13)" in e:
                stderr.write("The destination folder \"" + self.destination + "\" is not writeable\n")
                exit(8)
            elif "preSyncError" in e:
                stderr.write("Cannot remove \"" + self.destination + "/incomplete\", aborting.\n")
                exit(16)
            else:
                stderr.write("An unexpected error occurred. Please contact developer\n")
                stderr.write(e + "\n")
                exit(-1)


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
    syncer = Syncer(configuration)
    syncer.run()


if __name__ == "__main__":
    main()
