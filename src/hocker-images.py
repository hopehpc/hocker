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
# hocker-images.py:
# Returns the authorized images available on the current node (by default)
# or a different node if specified. 

"""

Usage:
    hocker images
    hocker images [--node=<node-hostname>]
    hocker images [-h | --help]

Options:
    --node=<node-hostname>  Show the authorized images on node <node-hostname>.
    -h, --help              Show this screen.

"""

from docopt import docopt
from subprocess import call
import os, sys, hockernode

if __name__ == '__main__':
    args = docopt(__doc__)

    if args.get('--node') is None:
        nodeHostname = os.uname()[1]
    else:
        nodeHostname = args.get('--node')

    hockernode.checkNode(nodeHostname)
    sys.exit(print('\n'.join(hockernode.getImages(nodeHostname))))