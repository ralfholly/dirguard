#! /usr/bin/env python3

import os
import os.path
import sys


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


def delete_oldest_entry(dir_list, file_delete_fun=None):
    entry_index = oldest_entry(dir_list)
    if entry_index is not None:
        if file_delete_fun:
            file_delete_fun(dir_list[entry_index])
        del dir_list[entry_index]


def cleanup_for_size(dir_list, max_size, file_delete_fun=None):
    while dir_entry_count(dir_list) and dir_size(dir_list) > max_size:
        delete_oldest_entry(dir_list, file_delete_fun)


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


if __name__ == '__main__':
    if len(sys.argv) != 3:
        fatal("Usage: %s <max-size> <dir>" % sys.argv[0])

    try:
        max_size = int(sys.argv[1])
    except ValueError:
        fatal("Please give a numeric value for <max-size>")
    if max_size <= 0:
        fatal("<max-size> must be a positiv integer")

    dir_path = sys.argv[2]
    if not os.path.isdir(dir_path):
        fatal("Directory '%s' not found" % dir_path)

    dir_list = make_dir_list_from_directory(dir_path)
    cleanup_for_size(dir_list, max_size, delete_dir_entry_from_disk)
