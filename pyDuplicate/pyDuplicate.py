#!/usr/bin/python3
#! coding: UTF-8

from argparse import ArgumentParser
import sys

from pyDuplicate import fileHandler, const
from pyDuplicate.duplicateFinder import DuplicateFinder
from pyDuplicate.logger import Logger


def parse():
    parser = ArgumentParser(description="a duplicate file finder and processor")
    parser.add_argument('-f', '--force', action="store_true", dest='force', help="Use this do disable interactive mode.\
     If used, the program will ignore any errors, be careful")
    parser.add_argument('-d', '--exclude-dir', action="append", type=str, help="Theses folders won't be checked")
    parser.add_argument('-e', '--exclude-extension', action="append", type=str,
                        help="Files with this extension won't be checked")
    parser.add_argument("folders", nargs="+", type=str, help="the folder[s] you want to scan")
    args = parser.parse_args()
    return args.folders, args.force, args.exclude_dir, args.exclude_extension


def process_duplicates(worker):
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


def treat(folders):
    Logger().get_logger().info("Listing all Files")
    all_files = []
    for directory in folders:
        all_files = all_files + fileHandler.tree_walk_with_size(directory)
    Logger().get_logger().info("Ordering All Files")
    ordered_files = fileHandler.order_files_by_size(all_files)

    worker = DuplicateFinder(ordered_files)
    worker.setDaemon(True)
    worker.start()
    process_duplicates(worker)
    doubles = worker.get_duplicates()
    Logger().get_logger().info("Processing finished")
    return doubles


def main():
    (folders, force, exclude_dirs, exclude_extensions) = parse()

    if exclude_dirs is not None:
        const.FOLDERS_NOT_TO_CHECK += tuple(exclude_dirs)
    if exclude_extensions is not None:
        const.EXTENSIONS_NOT_TO_CHECK += tuple(exclude_extensions)

    folders = fileHandler.handle_bad_folders(folders, force)

    doubles = treat(folders)

    print(doubles)


if __name__ == "__main__":
    main()