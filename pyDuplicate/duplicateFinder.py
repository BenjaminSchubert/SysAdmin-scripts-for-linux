#!/usr/bin/python
#! Coding: UTF-8

import threading
from math import floor
from hashlib import sha512
import time

from pyDuplicate.logger import Logger
from pyDuplicate import const


class DuplicateFinder(threading.Thread):
    def __init__(self, files):
        super(DuplicateFinder, self).__init__()
        self.waiting = threading.Event()
        self.files = files
        self.doubles = []
        self.completed = len(self.files)
        self.processed = 0

    def wait(self):
        self.waiting.set()

    def resume(self):
        self.waiting.clear()

    def get_duplicates(self):
        if self.is_alive():
            return []
        else:
            return self.doubles

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
                Logger().get_logger().warning("Couldn't open file %s, not enough permissions", fi)
            except FileNotFoundError:
                Logger().get_logger().warning("%s disappeared as I was using it", fi)

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

    def run(self):
        for fi in self.files:
            while self.waiting.isSet(): time.sleep(10)
            print("Processing : [" + ("#" * floor(self.processed * 50 / self.completed)).ljust(50, " ") + "]", end="\r")
            self.doubles += self.find_duplicates(self.files[fi])
            self.processed += 1


