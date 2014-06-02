#!/usr/bin/python3
#! coding: UTF-8

"""
This is the main script for the module. It puts everything together
"""

from argparse import ArgumentParser
import sys

import duplicateFinder
import fileHandler
import const
import logger


def parse():
    """
    Creates a parser for command lines attributes and parses them
    :return: folders, force, handle_hard_links, exclude_dir, exclude_extension
    """
    parser = ArgumentParser(description="a duplicate file finder and processor")
    parser.add_argument('-f', '--force', action="store_true", dest='force', help="Use this do disable interactive mode.\
     If used, the program will ignore any errors, be careful")
    parser.add_argument('--hardlinks', action="store_true", dest="handle_hard_links", help="Use this to exclude\
     hardlinks from the count of duplicates.")
    parser.add_argument('-d', '--exclude-dir', action="append", type=str, help="Theses folders won't be checked")
    parser.add_argument('-e', '--exclude-extension', action="append", type=str,
                        help="Files with this extension won't be checked")
    parser.add_argument("folders", nargs="+", type=str, help="the folder[s] you want to scan")
    args = parser.parse_args()
    return args.folders, args.force, args.handle_hard_links, args.exclude_dir, args.exclude_extension


def process_duplicates(worker):
    """
    Creates a KeyboardInterrupt handler on top of the process processing the files. It asks if the user is sure to quit
    before effectively stopping the script
    :param worker: the thread to wait on
    """
    try:
        worker.join()
    except KeyboardInterrupt:
        worker.wait()
        if input("Are you sure you want to quit? All progress will be lost : [y/N]") not in "Yy":
            print("Resuming process")
            worker.resume()
            process_duplicates(worker)
        else:
            sys.exit()


def treat(folders, handle_hard_links):
    """
    This creates the logger, lists all files to check and search for duplicates
    :param folders: the folders in which to search files
    :param handle_hard_links: if yes or no two files hardlinked are to be treated are duplicates or no
    """
    logger.Logger().get_logger().info("Listing all Files")
    all_files = []
    for directory in folders:
        all_files = all_files + fileHandler.tree_walk_with_size(directory)
    logger.Logger().get_logger().info("Ordering All Files")
    ordered_files = fileHandler.order_files_by_size(all_files)

    worker = duplicateFinder.DuplicateFinder(ordered_files, handle_hard_links)
    worker.setDaemon(True)
    worker.start()
    process_duplicates(worker)
    doubles = worker.get_duplicates()
    hard_linked_files = worker.get_hard_linked()
    logger.Logger().get_logger().info("Processing finished")
    return doubles, hard_linked_files


def main():
    """
    Parses the command line, check if folders are valid and check for duplicates. print them
    """
    (folders, force, handle_hard_links, exclude_dirs, exclude_extensions) = parse()

    if exclude_dirs is not None:
        const.FOLDERS_NOT_TO_CHECK += tuple(exclude_dirs)
    if exclude_extensions is not None:
        const.EXTENSIONS_NOT_TO_CHECK += tuple(exclude_extensions)

    folders = fileHandler.handle_bad_folders(folders, force)

    doubles, hard_linked = treat(folders, handle_hard_links)

    print(doubles)
    print(hard_linked)


if __name__ == "__main__":
    main()
