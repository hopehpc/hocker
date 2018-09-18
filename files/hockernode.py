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
# hockernode.py:
# System image and node methods for hocker-run.py and hocker-images.py.

import os, sys, glob

# The directory containing lists of images authorized to run on each compute node
# If Slurm is not being used, this directory must still contain an entry for the host machine
AUTHORIZED_IMAGES_DIR = '/admin/hocker-images/'

def getImages(node_hostname):
    try:
        with open(getNodes().get(node_hostname)) as f:
            images = [line.rstrip('\n') for line in f if line.rstrip('\n') != ""]
            if len(images) == 0:
                raise Exception()
            return images
    except:
        print('Hocker: No authorized images to run. Hocker cannot be used on node {}.\nContact cit@hope.edu to request an image.\n'.format(node_hostname))
        sys.exit(1)

def checkImage(node_hostname, image, verbose):
    if verbose:
        print('Hocker: Verifying image \'{}\' on node \'{}\'\n'.format(image, node_hostname))
    if not image in getImages(node_hostname):
        print('Hocker: The image \'{}\' is not authorized for node {}.\nContact cit@hope.edu to request this image.\n'.format(image, node_hostname))
        sys.exit(1)

def getNodes():
    return {os.path.basename(file): file for file in glob.glob(AUTHORIZED_IMAGES_DIR + "*")}

def checkNode(node_hostname):
    if node_hostname not in getNodes():
        print('Hocker: Node \'{}\' does not exist on this system.\n'.format(node_hostname))
        sys.exit(2)