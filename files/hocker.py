#!/usr/bin/python3
#
# Hocker - a secure HPC solution for running Docker containers at Hope College.
#
# Hocker version 1.0
# Author: Zachary Snoek, Hope College
# Contact: zachary.snoek@hope.edu
#
# Based on Socker 16.12 developed by the Universiy of Oslo
# Original Socker code obtained from https://github.com/unioslo/socker
#
# hocker.py:
# Main argument parser for Hocker. Parses the Hocker command and
# then calls the command and passes the rest of the arguments
# to it.

"""Hocker: a secure HPC solution for running Docker containers at Hope College.

Usage:
    hocker <command> [<args>...]
    hocker [-v | --version]
    hocker [-h | --help]

Options:
    -v, --version   Show the current version of Hocker.
    -h, --help      Show this screen.

Commands:
    run             Run a command in a Docker container.
    images          Show the authorized images on a node.

Run 'hocker <command> --help' for more information on a command.

"""

from subprocess import call
from docopt import docopt
import sys

# The location of the Hocker symlink in /usr/bin
HOCKER_LN = '/usr/bin/hocker'
# The relative path to added_files in hocker.spec
ADDED_FILES = '/usr/bin/hocker1.0/files/'

if __name__ == '__main__':
    args = docopt(__doc__,
                  version='Hocker version 1.0',
                  options_first=True)
    argv = [args['<command>']] + args['<args>']

    if args['<command>'] == 'run':
        sys.exit(call([ADDED_FILES + 'hocker-run.py'] + argv))
    elif args['<command>'] == 'images':
        sys.exit(call([ADDED_FILES + 'hocker-images.py'] + argv)) 
    elif args['<command>'] in ['help', None]:
        sys.exit(call([HOCKER_LN, '--help']))
    else:
        sys.exit('\'{}\' is not a Hocker command. See \'hocker --help\'.'.format(args['<command>']))