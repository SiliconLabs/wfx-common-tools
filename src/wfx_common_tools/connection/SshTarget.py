#!/usr/bin/python3
#
# Created: 2019-10-09 11:00:00
# Main author:
#     - Marc Dorval <marc.dorval@silabs.com>
#

# Standard library imports
import sys
import time
import socket
import logging

# Third party imports
import paramiko

# Local application imports


class SshTarget(paramiko.client.SSHClient):
    def __init__(self, host, name=None, wait=False, user="root", port=22, password=None, pkey=None):
        super().__init__()
        self.user = user
        self.host = host
        self.port = port
        self.password = password
        self.pkey = pkey
        self.name = name if name else host
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.result = None
        self.error = None
        self.local_trace = False
        if len(self.name) > 10:
            self.name = "…" + self.name[-9:]
        self.__connect(wait)

    def __connect(self, wait=False):
        cmd_name = "%-6s" % self.name
        err = None
        self.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        start = now = time.time()
        while start + 10 > now:
            try:
                self.connect(self.host, username=self.user, port=self.port, timeout=1, banner_timeout=1,
                             auth_timeout=1, password=self.password, pkey=self.pkey)
                peer = self.get_transport().getpeername()
                logging.info("%-13s I'm connected to %s:%d as %s" % (cmd_name, peer[0], peer[1], self.user))
                return
            except socket.timeout:
                if not wait:
                    break
                if err != socket.timeout:
                    logging.info("%-13s I %s" % (cmd_name, "didn't boot yet. Wait."))
                    err = socket.timeout
            except paramiko.ssh_exception.NoValidConnectionsError:
                if not wait:
                    break
                if err != paramiko.ssh_exception.NoValidConnectionsError:
                    logging.info("%-13s %s" % (cmd_name, "boot nearly finished"))
                    err = paramiko.ssh_exception.NoValidConnectionsError
            except paramiko.ssh_exception.SSHException:
                self.__send_key(self.password)
                return self.__connect()
            now = time.time()
        logging.info("%-13s I can't connect to %s:%d as %s" % (cmd_name, self.host, self.port, self.user))
        raise Exception("%s: Cannot connect over SSH to %s:%d as %s" % (cmd_name, self.host, self.port, self.user))

    def __send_key(self, original_pwd):
        # This is very specific to the Raspberry PI, where SSH using a password for root is not possible.
        # Therefore we try to log using the 'pi' account to add our public key and copy it to the root account
        a = paramiko.Agent()
        ks = a.get_keys()
        k = ks[0].get_base64()
        for pwd in {'default_password', original_pwd}:
            if pwd is not None:
                print("Trying to add the tester public key to /root/.ssh/authorized_keys using \'" + pwd + "\'")
                try:
                    tmp_dut = SshTarget(self.host, name='tmp_dut', port=self.port, user='pi', password=pwd)
                    print(type(tmp_dut))
                    tmp_dut.write('sudo mkdir -p /root/.ssh')
                    tmp_dut.write('echo ' + 'ssh-rsa ' + str(k) + '> ~/.ssh/authorized_keys2')
                    tmp_dut.write('sudo tee -a /root/.ssh/authorized_keys < ~/.ssh/authorized_keys2')
                except paramiko.ssh_exception.SSHException:
                    pass

    def write(self, text):
        if self is not None:
            cmd = b"/bin/sh --login -c " + text  # Provide a login shell to set the environment and locate scripts
            self.stdin, self.stdout, self.stderr = self.exec_command(cmd, environment={'ENV': '/etc/profile'})

    def read(self):
        self.result = str(self.stdout.read(), "utf-8").strip()
        self.error = str(self.stderr.read(), "utf-8").strip()
        if not self.result:
            return "ERROR: " + self.error
        else:
            return self.result


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        sys.stderr.write("This tools was developed for Python 3 and wasn't tested with Python 2.x\n")
        sys.exit(0)

    print('You\'re using a ', sys.platform, 'platform')
