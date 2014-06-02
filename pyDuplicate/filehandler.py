#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This file contains functions to handle files, list, order, and removing some
"""

from os import walk
from os.path import join, isfile, getsize, isdir

import logger
import const


def tree_walk_with_size(_dir):
    """
    Takes a directory and returns a list of file with their weight
    :param _dir: the root directory where to list all files contained in it
    :return: list of tuple containing (file, file's size)
    """
    files = []
    for (dir_name, sub_dirs, file_names) in walk(_dir):
        sub_dirs[:] = [x for x in sub_dirs if x not in const.FOLDERS_NOT_TO_CHECK]
        for name in file_names:
            file_path = join(dir_name, name)
            if isfile(file_path) and not file_path.endswith(const.EXTENSIONS_NOT_TO_CHECK):
                files.append((file_path, getsize(file_path)))
    return files


def order_files_by_size(weighted_files):
    """
    Orders a list of files by their weight
    :param weighted_files: a list of tuples (file, file's size)
    :return: a dict with keys being file's size and values the file with that size
    """
    dict_files = {}
    for file in weighted_files:
        if file[1] == 0:
            continue  # we don't care about files of size 0

        indices = file[1]
        if not indices in dict_files:
            dict_files[indices] = [file[0]]
        else:
            dict_files[indices].append(file[0])
    return dict_files


def handle_bad_folders(folders, force=False):
    """
    Checks if every folder in the list given exists. If not : exits if force is false, else it is removed from the list
    :param folders: folders list to check
    :param force: boolean (default : False)
    :return: list of correct folders
    """
    bad_folders = [str(x) for x in folders if not isdir(x)]
    if bad_folders and not force:
        logger().get_logger().error(
            "Some of the directories you gave are wrong, please check :\n {0}".format(
                '\n '.join(bad_folders)))
        exit(1)
    elif bad_folders and force:
        folders = [x for x in folders if x not in bad_folders]
    return folders
