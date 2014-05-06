#!/usr/bin/python3
#!Coding: UTF-8

from os import walk
from os.path import join, isfile, getsize, isdir

import logger
import const


def tree_walk_with_size(_dir):
    files = []
    for (dir_name, sub_dirs, file_names) in walk(_dir):
        sub_dirs[:] = [x for x in sub_dirs if x not in const.FOLDERS_NOT_TO_CHECK]
        for name in file_names:
            file_path = join(dir_name, name)
            if isfile(file_path) and not file_path.endswith(const.EXTENSIONS_NOT_TO_CHECK):
                files.append((file_path, getsize(file_path)))
    return files


def order_files_by_size(weighted_files):
    dict_files = {}
    for fi in weighted_files:
        if fi[1] == 0:
            continue  # we don't care about files of size 0

        indices = fi[1]
        if not indices in dict_files:
            dict_files[indices] = [fi[0]]
        else:
            dict_files[indices].append(fi[0])
    return dict_files


def handle_bad_folders(folders, force):
    bad_folders = [x for x in folders if not isdir(x)]
    if bad_folders and not force:
        logger().get_logger().error(
            "Some of the directories you gave are wrong, please check :\n {0}".format(
                '\n '.join(map(str, bad_folders))))
        exit(1)
    elif bad_folders and force:
        folders = [x for x in folders if x not in bad_folders]
    return folders