#!/usr/bin/env python3
import argparse
import logging
import os
import os.path
from shutil import move
from tempfile import mkstemp

from termcolor import colored

from strings import multi_replace_curry


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Replace old pattern with new pattern in all files in path recursively')
    parser.add_argument("path", help="the path to start recursively")
    parser.add_argument("old_pattern", help="the old pattern to be replaced by")
    parser.add_argument("new_pattern", help="the new pattern to be replaced with")
    parser.add_argument('--dry_run', action='store_true', help="show what would happen without doing it")

    args = parser.parse_args()

    f = multi_replace_curry([(args.old_pattern, args.new_pattern)])
    replace_files(args.path, new_string_func=f, dry_run=args.dry_run)

    if args.dry_run:
        print()
        logging.info(colored("Please note that the above doesn't happen as it's a dry_run", 'cyan'))


def replaceable(file_path, new_string_func):
    try:
        with open(file_path, 'r') as file:
            old_string = file.read()
            new_string = new_string_func(old_string)
            return old_string != new_string
    except OSError as e:
        logging.error(colored("%s" % e, 'yellow'))


def replace_files(directory, new_string_func, dry_run):
    try:
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            if os.path.isdir(file_path):
                replace_files(file_path, new_string_func, dry_run)
            else:
                try:
                    if replaceable(file_path, new_string_func):
                        replace(file_path, new_string_func, dry_run)
                    else:
                        logging.debug("Skipping %s" % file_path)
                except UnicodeDecodeError:
                    logging.debug(colored("Ignoring non 'utf-8' file: %s" % file_name, 'yellow'))
    except FileNotFoundError:
        logging.error(colored("No such directory: %s" % directory, 'yellow'))


def replace(file_path, new_string_func, dry_run):
    temp_path = make_temp_file(file_path, new_string_func)
    if not dry_run:
        os.remove(file_path)
        move(temp_path, file_path)
    else:
        os.remove(temp_path)


def make_temp_file(file_path, new_string_func):
    try:
        fh, temp_path = mkstemp()

        with open(temp_path, 'w') as new_file:
            with open(file_path, 'r') as old_file:
                line_number = 1
                for line in old_file:
                    new_line = new_string_func(line)
                    new_file.write(new_line)

                    if new_line != line:
                        logging.info("%s:%d: %s => %s" % (
                            file_path, line_number, colored(line.lstrip().rstrip(), 'blue'),
                            colored(new_line.lstrip().rstrip(), 'green')))
                    line_number += 1

        return temp_path
    finally:
        os.close(fh)


if __name__ == '__main__':
    main()
