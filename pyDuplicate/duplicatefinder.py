#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This contains a class made to run on a list of files and return duplicates found.
"""

import threading
from math import floor
from hashlib import sha512
import time
import os
from itertools import groupby

import logger
import const


class DuplicateFinder(threading.Thread):
    """
    This class extends threading.Thread and is meant to find duplicates in the files passed as parameter.
    A second parameter, a boolean, can be passed to check for hardlinks (default: False)
    """
    def __init__(self, files, treat_hard_links=False):
        super(DuplicateFinder, self).__init__()
        self.waiting = threading.Event()
        self.files = files
        self.__doubles__ = []
        self.__hard_linked_files__ = []
        self.completed = len(self.files)
        self.processed = 0
        self.treat_hard_links = treat_hard_links

    def wait(self):
        """
        Pauses the thread
        """
        self.waiting.set()

    def resume(self):
        """
        Restarts the thread
        """
        self.waiting.clear()

    def get_duplicates(self):
        """
        Returns an empty list while the thread is running, returns the duplicates afterwards
        :return: list of duplicates
        """
        if self.is_alive():
            return []
        else:
            return self.__doubles__

    def get_hard_linked(self):
        """
        Returns an empty list while the thread is running, returns the hard linked files afterwards
        :return: list of hardlinked files
        """
        if self.is_alive():
            return []
        else:
            return self.__hard_linked_files__

    @staticmethod
    def hash(file):
        """
        Calculates the sha512 of the file passed in parameter
        :param file: the file from which to compute the sha
        :return: the sha in hexadecimal
        """
        sha = sha512()
        with open(file, 'rb') as my_file:
            for chunk in iter(lambda: my_file.read(128 * sha.block_size), b''):
                sha.update(chunk)
        return sha.hexdigest()

    def find_duplicates(self, files, offset=0, read=100):
        """
        Goes through the files and find doubles
        :param files: the files to check
        :param offset: the place where to begin reading the file
        :param read: the number of bytes to read
        :return: a dictionary of list of duplicates
        """
        order_files = {}
        for file in files:
            try:
                with open(file, "rb") as my_file:
                    my_file.seek(offset)
                    data = my_file.read(read)
                if not data in order_files:
                    order_files[data] = [file]
                else:
                    order_files[data].append(file)

            except PermissionError:
                logger.Logger().get_logger().warning("Couldn't open file {}, not enough permissions".format(file))
            except FileNotFoundError:
                logger.Logger().get_logger().warning("{} disappeared as I was using it".format(file))

        doubles = [order_files[file] for file in order_files if len(file) != read and len(order_files[file]) > 1]
        to_remove = [file for file in order_files if len(file) != read]
        for remove in to_remove:
            del order_files[remove]

        for file in order_files:
            if read < const.MAX_MEMORY:
                doubles += self.find_duplicates(order_files[file], offset=read, read=read * 10)
            else:
                files_shas = {}
                for my_file in order_files[file]:
                    ha = self.hash(my_file)
                    if ha in files_shas:
                        files_shas[ha].append(my_file)
                    else:
                        files_shas[ha] = [my_file]
                for sha in files_shas:
                    if len(files_shas[sha]) > 1:
                        doubles += [files_shas[sha]]
        return doubles

    def handle_hard_links(self):
        """
        Goes through the list of duplicates and check if some are hard linked and removes them from the duplicates list
        """
        hard_linked = []
        same_device = []

        for double in self.__doubles__:
            for _, g in groupby(double, lambda u: os.stat(u)[2]):
                l = list(g)
                if len(l) > 1:
                    same_device.append(l)

        for same in same_device:
            for _, g in groupby(same, lambda u: os.stat(u)[1]):
                l = list(g)
                if len(l) > 1:
                    hard_linked.append(l)

        for hard_link in hard_linked:
            for to_remove in hard_link[1:]:
                for double in self.__doubles__:
                    if to_remove in double:
                        double.remove(to_remove)

        self.__hard_linked_files__ = hard_linked

    def run(self):
        """
        Goes through the list of files, and check for doubles. Shows an indicator of the process
        """
        for file in self.files:
            while self.waiting.isSet():
                time.sleep(10)
            print("Processing : [" + ("#" * floor(self.processed * 50 / self.completed)).ljust(50, " ") + "]", end="\r")
            self.__doubles__ += self.find_duplicates(self.files[file])
            self.processed += 1

        if self.treat_hard_links and len(self.__doubles__) != 0:
            self.handle_hard_links()

