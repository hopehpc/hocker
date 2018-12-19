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
# hocker-run.py:
# Runs a user command inside of a Docker container. Starts the 
# container as that user with the user's information. Provides
# various options that are useful in a high performance
# computing environment.

"""

Usage:
    hocker run <image> <command> 
    hocker run [options] <image> <command> 
    hocker run (-h | --help)

Options:
    --shell=<shell>                 Specify the shell to use (e.g., sh, csh) [default: /bin/bash].
    --env-file=<file>               Load environment variables from <file>.
    -l, --log                       Save the Docker log to the current working directory.
    -v, --verbose                   Show verbose output.
    -h, --help                      Show this screen.

"""

from docopt import docopt
from pwd import getpwnam
from subprocess import call
import os, sys, subprocess, uuid, getpass, pwd, grp, glob
import hockernode, hockerslurm, hockerrun

# The user data files to copy to the container
USER_ACCT_DATA = ['/etc/passwd', '/etc/group']

def reincarnate(user_UID, user_GID):
    def result():
        os.setgid(user_GID)
        os.setuid(user_UID)
    return result

def decodeBytes(output):
    return output.decode().strip()

def checkForError(p, err, verbose, container_ID=None, slurm_Std_Err=None):
    if p.returncode != 0:
        stdErr = '### Error ###:\n\n{}\n\n'.format(decodeBytes(err))
        if slurm_Std_Err:
            with open(slurm_Std_Err, "a") as f:
                f.write(stdErr)
        else:
            print(stdErr)
        print('Hocker: Exiting due to error\n')
        if container_ID:
            stopAndRemoveContainer(container_ID, verbose)
        sys.exit(1)

def stopAndRemoveContainer(container_ID, verbose, user_CWD=None, log=None):
    if verbose:
        print('Hocker: Stopping container\n')
    p = subprocess.Popen('/usr/bin/docker stop {}'.format(container_ID), shell=True, 
                        stdout=subprocess.PIPE).communicate()
    if log:    
        if verbose:
            print("Hocker: Creating log file\n")
        dockerInspectCMD = 'docker inspect {} > {}/{}-hocker.log'.format(container_ID, user_CWD, container_ID[0:8])
        p = subprocess.Popen(dockerInspectCMD, shell=True, 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
    if verbose:
        print('Hocker: Removing container\n')
    p = subprocess.Popen('/usr/bin/docker rm {}'.format(container_ID), shell=True, 
                        stdout=subprocess.PIPE).wait()

def main(args):
    # Intitialization
    dockerUID = None
    dockerGID = None 
    slurmJobID = None
    slurmStdErr = None
    userImage = None
    userCMD = None
    verbose = False

    # Check for Docker on the Hocker host
    p = subprocess.Popen('/usr/bin/docker --version', shell=True, 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode !=0:
        print('Hocker: Docker is not found in /usr/bin! Please verify that Docker is installed')
        sys.exit(1)

    # Get the UID and GID of the dockerroot user and docker group
    try:
        dockerUID = pwd.getpwnam('dockerroot').pw_uid
        dockerGID = grp.getgrnam('docker').gr_gid
    except KeyError:
        print('Hocker: There must exist a user "dockerroot" and a group "docker"')
        sys.exit(2)
    if not [g.gr_name for g in grp.getgrall() if 'dockerroot' in g.gr_mem] == ['docker']:
        print('Hocker: The user "dockerroot" must be a member of ONLY the "docker" group')
        sys.exit(1)
    
    # Check if the user is running a Slurm job
    try:
        # Get the Slurm job ID from the environment variable
        slurmJobID = os.environ['SLURM_JOB_ID']
        print('Hocker: Slurm job ID {}\n'.format(slurmJobID))

        if hockerslurm.slurmStdErr(slurmJobID):
            slurmStdErr = hockerslurm.getSlurmStdErr(slurmJobID)
    except KeyError as e:
        pass

    # Get the current system and user information
    nodeHostname = os.uname()[1]
    username = getpass.getuser()
    userUID = str(getpwnam(username).pw_uid)
    userGID = str(getpwnam(username).pw_gid)
    userCWD = os.getcwd()
    cid = str(uuid.uuid4())
    userHome = pwd.getpwuid(getpwnam(username).pw_uid).pw_dir

    # Get the user's command and check for verbosity
    userCMD = args.get('<command>')
    verbose = args.get('--verbose')

    # Check if the user's image is authorized on the node it is being run on
    userImage = args.get('<image>')
    hockernode.checkImage(nodeHostname, userImage, verbose)

    # Set the user to root to run Docker commands
    os.setuid(0)
    os.setuid(0)

    # Create the Docker run command to start the container
    if slurmJobID:
        dockerRunCMD = hockerslurm.createRunCMD(slurmJobID, userHome, cid, userCWD, userImage, args)
    else:
        dockerRunCMD = hockerrun.createRunCMD(userHome, cid, userCWD, userImage, args)

    # Start the container as dockerroot
    if verbose:
        print("Hocker: Starting container from image \'{}\' for user \'{}\'\n".format(userImage, username))

    p = subprocess.Popen(dockerRunCMD, preexec_fn=reincarnate(dockerUID, dockerGID), shell=True, 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    checkForError(p, err, verbose, slurmStdErr)

    # Get the container ID from the docker run command
    containerID = decodeBytes(out)

    # Copy user data from the host machine to the container
    for f in USER_ACCT_DATA:
        copyCMD = '/usr/bin/docker cp {} {}:{}'.format(f, containerID, f)
        subprocess.Popen(copyCMD, preexec_fn=reincarnate(dockerUID, dockerGID), shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
    # Note: running the docker copy command for each data file causes this error:
    #                   WARNING: Error loading config file:/home/user/.docker/config.json - stat
    #                   /home/user/.docker/config.json: permission denied
    # The docker copy command is trying to copy the configuration file from the user's directory, but cannot 
    # find it because it doesn't exist. This error doesn't affect any docker commands, and the files are still
    # copied to the container. However, the current implementation surpresses the error message from the above 
    # processes. To view the standard out/error of the docker cp commands, implement the following:
    #for f in USER_ACCT_DATA:
    #    copyCMD = '/usr/bin/docker cp {} {}:{}'.format(f, containerID, f)
    #    p = subprocess.Popen(copyCMD, preexec_fn=reincarnate(dockerUID, dockerGID), shell=True,
    #                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #    out, err = p.communicate()
    #    print(decodeBytes(err))

    # Create the Docker command to run the user's job as the user
    userExecCMD = '/usr/bin/docker exec -u {} {} {} -c \'{}\''.format(userUID, 
                        containerID, args.get('--shell'), userCMD)

    # Run the user's command in the container using docker exec
    if verbose:
        print("Hocker: Executing container command \'{}\'\n".format(userCMD))

    p = subprocess.Popen(userExecCMD, preexec_fn=reincarnate(dockerUID, dockerGID), shell=True, 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    # Print the output from the container
    if decodeBytes(out) != "":
        print(decodeBytes(out) + '\n')

    checkForError(p, err, verbose, containerID, slurmStdErr)
    stopAndRemoveContainer(containerID, verbose, userCWD, args.get('--log'))

if __name__ == "__main__":
    args = docopt(__doc__, options_first=False)
    main(args)