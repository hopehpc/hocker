# hocker
Hocker is a Python 3 wrapper to enable secure Docker container usage in an HPC cluster.
</br></br>

## Prerequisites
* NFS
</br></br>

## Modified Installation
This installation guide should be used to create a full installation of Hocker (i.e., an installation to be used on an HPC cluster), but
for installation cases such as:
* Sans btools and Slurm
* Sans btools (avec Slurm)
* Sans Slurm (avec btools)
</br></br>

### Sans btools and Slurm
1. Populate the authorized images directory (`/admin/hocker-images`) with files named for each compute node containing the 
names of the images available for each compute node
</br></br>
For example, in `/admin/hocker-images/node02`</br></br>
`myrepo/base:latest`</br>
`myrepo/ubuntu:16.04`</br>
`myrepo/python:3.4`</br></br>  

2. Copy the Hocker bundle directory (`/usr/bin/hocker1.0`) to all of the compute nodes</br></br>

3. Change permissions of the Hocker executable on all of the compute nodes</br></br>
`$ chgrp hocker /usr/bin/hocker1.0/hocker`</br>
`$ chmod 6750 /usr/bin/hocker1.0/hocker`</br></br>

4. Change permissions of the Hocker files on all of the compute nodes</br></br>
`$ chmod 700 /usr/bin/hocker1.0/files/*`</br></br>

5. Create a symlink from the hocker1.0 bundle on all of the compute nodes</br></br>
`$ ln -s /usr/bin/hocker1.0/hocker /usr/bin/hocker`</br></br>

6. Follow steps 1-3 of the *Common* instructions below</br></br>

### Sans btools (avec Slurm)
1. Follow steps 1-6 of the *Sans btools and Slurm* instructions above</br></br>

2. Create the directory `/tmp/hocker` to store environment variable files created by Hocker on all of the compute nodes</br></br>
`$ mkdir /tmp/hocker`</br></br>

3. Create a Slurm prolog script to create the files contained in `/tmp/hocker` on all of the compute nodes</br></br>
`$ vim /etc/slurm/hocker-prolog`</br>
   `#!/bin/bash`</br>
   `env | grep SLURM > /tmp/hocker/\SLURM_JOB_ID`</br></br>

4. Create a Slurm epilog script to remove the files contained in `/tmp/hocker` on all of the compute nodes</br></br>
`$ vim /etc/slurm/hocker-epilog`</br>
   `#!/bin/bash`</br>
   `rm /tmp/hocker/\$SLURM_JOB_ID`</br></br>

5. Add the Hocker prolog and epilog scripts to `/etc/slurm/slurm.conf` on all of the compute nodes</br></br>
`$ vim /etc/slurm/slurm.conf`</br>
  `Prolog=/etc/slurm/hocker-prolog`</br>
  `Epilog=/etc/slurm/hocker-epilog`</br></br>

6. Restart the slurmd service on all of the compute nodes</br></br>
`$ systemctl restart slurmd`</br></br>

6. Follow steps 1-3 of the *Common* instructions below</br></br>

### Sans Slurm (avec btools)
1. Populate the authorized images directory using the `bhosts` file</br></br>
`$ for host in 'grep -v \# /usr/local/sbin/bhosts'; do touch /admin/hocker-images/${host}; done`</br></br>

2. Copy the Hocker bundle directory to all of the compute nodes</br></br>
`$ bpushdir /usr/bin/hocker1.0/ /usr/bin/hocker1.0/`</br></br>

3. Change permissions of the Hocker executable on all of the compute nodes</br></br>
`$ bexec chgrp hocker /usr/bin/hocker1.0/hocker`</br>
`$ bexec chmod 6750 /usr/bin/hocker1.0/hocker`</br></br>

4. Change permissions of the Hocker files on all of the compute nodes</br></br>
`$ bexec chmod 700 /usr/bin/hocker1.0/files/*`</br></br>

5. Create a symlink from the Hocker executable on all of the compute nodes</br></br>
`$ bexec ln -s /usr/bin/hocker1.0/hocker /usr/bin/hocker`</br></br>

6. Follow steps 1-3 of the *Common* instructions below</br></br>

### Common
1. Add users to the Hocker group that are allowed access to Hocker</br></br>
`$ usermod -aG hocker user`</br></br>

2. Update user account data on all of the compute nodes</br></br>

   a. If using btools, use `bsync` to copy user data to all of the compute nodes</br></br>
        `$ bsync`</br></br>

3. Add `/admin/hocker-images` to `/etc/exports` so that the authorized images files are available on each compute node
</br></br>

## Conventions
* Hocker files</br>
  * The files contained in `/usr/bin/hocker1.0/files`</br>
* Hocker executable</br>
  * The executable created by PyInstaller (`/usr/bin/hocker1.0/hocker`)</br>
* Hocker bundle directory</br>
  * The bundled directory created by PyInstaller (`/usr/bin/hocker1.0`)</br>
* Authorized images files</br>
  * The files named for each compute node containing the names of the images available for each compute node</br>
* Authorized images directory</br>
  * The directory containing the authorized images files (`/admin/hocker-images`)
</br>
