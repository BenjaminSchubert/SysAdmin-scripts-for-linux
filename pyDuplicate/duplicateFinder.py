#!/usr/bin/python
#! Coding: UTF-8

import threading
from math import floor
from hashlib import sha512
import time
import os
from itertools import groupby

import logger
import const


class DuplicateFinder(threading.Thread):
    def __init__(self, files, treat_hard_links):
        super(DuplicateFinder, self).__init__()
        self.waiting = threading.Event()
        self.files = files
        self.__doubles__ = []
        self.__hard_linked_files__ = []
        self.completed = len(self.files)
        self.processed = 0
        self.treat_hard_links = treat_hard_links

    def wait(self):
        self.waiting.set()

    def resume(self):
        self.waiting.clear()

    def get_duplicates(self):
        if self.is_alive():
            return []
        else:
            return self.__doubles__

    def get_hard_linked(self):
        if self.is_alive():
            return []
        else:
            return self.__hard_linked_files__

    @staticmethod
    def hash(fi):
        sha = sha512()
        with open(fi, 'rb') as file:
            for chunk in iter(lambda: file.read(128 * sha.block_size), b''):
                sha.update(chunk)
        return sha.hexdigest()

    def find_duplicates(self, files, offset=0, read=100):
        order_files = {}
        for fi in files:
            try:
                with open(fi, "rb") as f:
                    f.seek(offset)
                    data = f.read(read)
                if not data in order_files:
                    order_files[data] = [fi]
                else:
                    order_files[data].append(fi)

            except PermissionError:
                logger.Logger().get_logger().warning("Couldn't open file %s, not enough permissions", fi)
            except FileNotFoundError:
                logger.Logger().get_logger().warning("%s disappeared as I was using it", fi)

        doubles = [order_files[x] for x in order_files if len(x) != read and len(order_files[x]) > 1]
        to_remove = [x for x in order_files if len(x) != read]
        for x in to_remove:
            del order_files[x]

        for x in order_files:
            if read < const.MAX_MEMORY:
                doubles += self.find_duplicates(order_files[x], offset=read, read=read * 10)
            else:
                files_shas = {}
                for fi in order_files[x]:
                    ha = self.hash(fi)
                    if ha in files_shas:
                        files_shas[ha].append(fi)
                    else:
                        files_shas[ha] = [fi]
                for x in files_shas:
                    if len(files_shas[x]) > 1:
                        doubles += [files_shas[x]]
        return doubles

    def handle_hard_links(self):
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

        for hl in hard_linked:
            for to_remove in hl[1:]:
                for double in self.__doubles__:
                    if to_remove in double:
                        double.remove(to_remove)

        self.__hard_linked_files__ = hard_linked

    def run(self):
        for fi in self.files:
            while self.waiting.isSet(): time.sleep(10)
            print("Processing : [" + ("#" * floor(self.processed * 50 / self.completed)).ljust(50, " ") + "]", end="\r")
            self.__doubles__ += self.find_duplicates(self.files[fi])
            self.processed += 1

        if self.treat_hard_links and len(self.__doubles__) != 0:
            self.handle_hard_links()

