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
# hockerslurm.py:
# Various Hocker methods to be called if the user is running a Slurm job.

import os, subprocess

def decodeBytes(output):
    return output.decode().strip()

def createRunCMD(slurm_Job_ID, user_Home, cid, user_CWD, user_Image, args):
    dockerRunCMD = '/usr/bin/docker run '
    mountDirectory = '{}:{}'.format(user_Home, user_Home)

    # Add the docker --env-file option to the run command 
    if args.get('--env-file') is not None:
        dockerRunCMD += '--env-file {} '.format(args.get('--env-file'))
    
    if os.path.exists('/tmp/hocker/{}'.format(slurm_Job_ID)):
        dockerRunCMD += '--env-file /tmp/hocker/{} '.format(slurm_Job_ID)
    else:
        print('Hocker: Slurm prolog script cannot get Slurm environment variables.')
        print('\tSlurm enviornment variables will not be set inside of container.\n')
    
    dockerRunCMD += '--name={} -itd -v {} --workdir="{}" {}'.format(cid, 
                        mountDirectory, user_CWD, user_Image)
    return dockerRunCMD

def slurmStdErr(slurm_Job_ID):
    # Run diff on scontrol output to see if the user has specified an error file
    # using sbatch -e option
    diffCMD = """diff <(scontrol show jobid -v {} | grep StdOut | cut -d "=" -f 2) \
        <(scontrol show jobid -v {} | grep StdErr | cut -d "=" -f 2)""".format(slurm_Job_ID, slurm_Job_ID)
    # Run the diff command using /bin/bash to use its process substitution for diff
    p = subprocess.Popen(diffCMD, shell=True, stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, executable='/bin/bash')

    # If the user has specified an error file, redirect Hocker stderr to that file
    if decodeBytes(p.communicate()[0]) != "":
        return True
    return False

def getSlurmStdErr(slurm_Job_ID):
    p = subprocess.Popen('scontrol show jobid -v ' + slurm_Job_ID + ' | grep StdErr | cut -d "=" -f 2', 
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return decodeBytes(p.communicate()[0])