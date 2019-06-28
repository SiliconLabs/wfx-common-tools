#!/bin/bash

# Install necessary resources from paramiko (Python SSH access)
#  including scp (to copy files) and fs.sshfs (to allow remote access to files)
set -euo pipefail

set -x

[ $(id -u) != 0 ] && echo "this script must be run as root" && exit 1

apt-get update
apt-get install libffi-dev python3-pip
apt-get install libssl-dev
pip3 install -U pip
pip3 install -U setuptools
pip3 install -U pynacl
pip3 install -U paramiko ipython==6
pip3 install -U ifaddr
pip3 install -U pyserial

