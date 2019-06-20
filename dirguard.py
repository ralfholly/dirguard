#! /usr/bin/env python3

import os
import os.path
import sys
import argparse

# pylint:disable=redefined-outer-name

class DirEntry:
    def __init__(self, name, size, time):
        self.name = name
        self.size = size
        self.time = time

    def __repr__(self):
        return "DirEntry(%s, %s, %s)" % (self.name, self.size, self.time)


    def __str__(self):
        return "%s (size=%s, time=%s)" % (self.name, self.size, self.time)


def make_sorted_dir_list(dir_list):
    return sorted(dir_list, key=lambda dir_entry: dir_entry.time)


def dir_size(dir_list):
    total_size = sum([entry.size for entry in dir_list])
    return total_size


def dir_entry_count(dir_list):
    return len(dir_list)


def delete_oldest_entry(sorted_dir_list, **kwargs):
    if sorted_dir_list:
        oldest_index = 0 
        file_delete_fun = kwargs.get("file_delete_fun")
        if kwargs.get("verbose"):
            print("Deleting %s" % sorted_dir_list[oldest_index])
        if file_delete_fun:
            file_delete_fun(sorted_dir_list[oldest_index])
        del sorted_dir_list[oldest_index]


def cleanup_for_size(sorted_dir_list, max_size, **kwargs):
    assert max_size >= 1
    if kwargs.get("verbose"):
        print("Current directory size: %d" % dir_size(sorted_dir_list))
    while dir_entry_count(sorted_dir_list) and dir_size(sorted_dir_list) > max_size:
        delete_oldest_entry(sorted_dir_list, **kwargs)
    if kwargs.get("verbose"):
        print("Current directory size: %d" % dir_size(sorted_dir_list))
        print("Entries left: %d" % dir_entry_count(sorted_dir_list))


def cleanup_for_entry_count(sorted_dir_list, max_entries, **kwargs):
    assert max_entries >= 1
    if kwargs.get("verbose"):
        print("Current number of entries: %d" % dir_entry_count(sorted_dir_list))
    while dir_entry_count(sorted_dir_list) > max_entries:
        delete_oldest_entry(sorted_dir_list, **kwargs)
    if kwargs.get("verbose"):
        print("Current number of entries: %d" % dir_entry_count(sorted_dir_list))
    return sorted_dir_list


def make_dir_list_from_directory(path):
    dir_stack = [path]
    dir_list = []
    while dir_stack:
        current_dir_path = dir_stack.pop()
        for f in os.listdir(current_dir_path):
            qualified_name = os.path.join(current_dir_path, f)
            if os.path.isfile(qualified_name):
                stat = os.stat(qualified_name)
                dir_list.append(DirEntry(qualified_name, stat.st_size, stat.st_mtime))
            elif os.path.isdir(qualified_name):
                dir_stack.append(qualified_name)

    return make_sorted_dir_list(dir_list)


def fatal(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def delete_dir_entry_from_disk(dir_entry):
    os.remove(dir_entry.name)


def main():
    parser = argparse.ArgumentParser(description="Enforces size limits on directories", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("mode", choices=["count", "size"], help="Enforce max. count of files or max. size of directory")
    parser.add_argument("value", metavar="N", type=int, help="Constraint value (count of files or directory size in bytes)")
    parser.add_argument("-d", "--dir-path", type=str, help="Path to directory")
    parser.add_argument('--verbose', action="store_true", help="Verbose output")
    parser.add_argument('--recursive', action="store_true", help="Recurse into subdirectories (only for mode \'size\'")

    args = parser.parse_args()
    if args.value <= 0:
        fatal("Value must be a positiv integer")

    if not os.path.isdir(args.dir_path):
        fatal("Directory '%s' not found" % args.dir_path)

    if args.mode != "size" and args.recursive:
        fatal("Recursive processing only supported for mode 'size'")

    dir_list = make_dir_list_from_directory(args.dir_path)

    if args.mode == "size":
        cleanup_for_size(dir_list, args.value, file_delete_fun=delete_dir_entry_from_disk, verbose=args.verbose)
    elif args.mode == "count":
        cleanup_for_entry_count(dir_list, args.value, file_delete_fun=delete_dir_entry_from_disk, verbose=args.verbose)
    else:
        assert False


if __name__ == '__main__':
    main()
