#!/bin/bash

# Install necessary resources from paramiko (Python SSH access)
#  including scp (to copy files) and fs.sshfs (to allow remote access to files)
set -euo pipefail

set -x

[ $(id -u) != 0 ] && echo "this script must be run as root" && exit 1

apt-get update
apt-get install libffi-dev python3-pip
apt-get install libssl-dev
pip3 install pip==19.1
pip3 install setuptools==41.0.1
pip3 install pynacl
pip3 install pygments==2.3.1
pip3 install paramiko==2.4.2
pip3 install ipython==6
pip3 install ifaddr==0.1.6
pip3 install pyserial==2.6

