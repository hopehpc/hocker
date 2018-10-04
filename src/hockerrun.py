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
# hockerrun.py:
# Creates the docker run command if the user is not running a Slurm job.
# Essentially the same as creatRunCMD in hockerslurm, but created to allow
# more flexibility with the docker run command in the future.

def createRunCMD(user_Home, cid, user_CWD, user_Image, args):
    dockerRunCMD = '/usr/bin/docker run '
    mountDirectory = '{}:{}'.format(user_Home, user_Home)

    # Add the docker --env-file option to the run command 
    if args.get('--env-file') is not None:
        dockerRunCMD += '--env-file {} '.format(args.get('--env-file'))

    dockerRunCMD += '--name={} -itd -v {} --workdir="{}" {}'.format(cid, 
                        mountDirectory, user_CWD, user_Image)
    return dockerRunCMD