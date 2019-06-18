#! /usr/bin/env python3

import os
import os.path
import sys
import argparse


class DirEntry:
    def __init__(self, name, size, time):
        self.name = name
        self.size = size
        self.time = time

    def __repr__(self):
        return "DirEntry(%s, %s, %s)" % (self.name, self.size, self.time)


def dir_size(dir_list):
    total_size = sum([entry.size for entry in dir_list])
    return total_size


def dir_entry_count(dir_list):
    return len(dir_list)


def oldest_entry(dir_list):
    if dir_list:
        min_index = 0
        min_time = dir_list[0].time

        for index, entry in enumerate(dir_list[1:]):
            if entry.time < min_time:
                min_index = index + 1
                min_time = entry.time

        return min_index
    return None


def delete_oldest_entry(dir_list, **kwargs):
    entry_index = oldest_entry(dir_list)
    if entry_index is not None:
        file_delete_fun = kwargs.get("file_delete_fun")
        if file_delete_fun:
            file_delete_fun(dir_list[entry_index])
        del dir_list[entry_index]


def cleanup_for_size(dir_list, max_size, **kwargs):
    assert max_size >= 1
    while dir_entry_count(dir_list) and dir_size(dir_list) > max_size:
        delete_oldest_entry(dir_list, **kwargs)


def cleanup_for_entry_count(dir_list, max_entries, **kwargs):
    assert max_entries >= 1
    while dir_entry_count(dir_list) > max_entries:
        delete_oldest_entry(dir_list, **kwargs)


def make_dir_list_from_directory(path):
    dir_list = []
    for f in os.listdir(path):
        qualified_name = os.path.join(path, f)
        if os.path.isfile(qualified_name):
            stat = os.stat(qualified_name)
            dir_list.append(DirEntry(qualified_name, stat.st_size, stat.st_mtime))

    return dir_list


def fatal(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def delete_dir_entry_from_disk(dir_entry):
    os.remove(dir_entry.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enforces size limits on directories", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("mode", choices=["count", "size"], help="Enforce max. count of files or max. size of directory")
    parser.add_argument("value", metavar="N", type=int, help="Constraint value (count of files or directory size in bytes)")
    parser.add_argument("-d", "--dir-path", type=str, help="Path to directory")
    parser.add_argument('--verbose', type=bool, help='Verbose output', default=False)

    args = parser.parse_args()
    if args.value <= 0:
        fatal("Value must be a positiv integer")

    if not os.path.isdir(args.dir_path):
        fatal("Directory '%s' not found" % args.dir_path)

    dir_list = make_dir_list_from_directory(args.dir_path)

    if args.mode == "size":
        cleanup_for_size(dir_list, args.value, file_delete_fun=delete_dir_entry_from_disk, verbose=args.verbose)
    elif args.mode == "count":
        cleanup_for_entry_count(dir_list, args.value, file_delete_fun=delete_dir_entry_from_disk, verbose=args.verbose)
    else:
        assert False
