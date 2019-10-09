#!/usr/bin/python3
#
# Created: 2019-06-04 16:00:00
# Main author:
#     - Marc Dorval <marc.dorval@silabs.com>
#

# Standard library imports
import logging
import os
import sys
import time

logging.basicConfig(level=logging.INFO)


class AbstractConnection(object):
    link = None
    connection = None
    nickname = ''
    trace = False

    def configure(self, *args, **kwargs):
        raise NotImplementedError()

    def write(self, text):
        raise NotImplementedError()

    def read(self):
        raise NotImplementedError()

    def run(self, cmd, wait_ms=0):
        raise NotImplementedError()


class Uart(AbstractConnection):

    def __init__(self, nickname="uart", port=None, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0.1, user='', password=''):
        try:
            import serial
        except ImportError:
            print("'serial'     is not installed. UART connection impossible")
        else:
            logging.getLogger("serial").setLevel(logging.WARNING)
            print('loaded serial')
        object.__init__(self)
        self.nickname = nickname
        self.conn = 'UART ' + str(port) + '/' + str(baudrate) + '/' + str(bytesize) + '/' + parity + '/' + str(stopbits)
        self.user = user
        self.password = password
        self.hostname = 'foo'
        self.prompt = 'bar'
        if port:
            self.configure(port, baudrate, bytesize, parity, stopbits, timeout)
            return

    def configure(self, port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0.1):
        import serial
        self.connection = None
        self.link = None
        self.trace = False
        try:
            self.link = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout, write_timeout=0.1)
            self.connection = port
            if self is None:
                raise Exception("%s %s" % (self.nickname, 'Can not connect to ' + port))
            for n in range(0, 4):
                dut_reply = self.run('', 0)
                if 'login:' in dut_reply:
                    print("sending login '" + self.user + "'")
                    dut_reply = self.run(self.user)
                if 'assword:' in dut_reply:
                    print("sending password '" + self.password + "'")
                    dut_reply = self.run(self.password)
                    break
            dut_reply = self.run('hostname')
            le = len(dut_reply.split("\n"))
            self.prompt = dut_reply.split("\n")[le-1]
            self.hostname = self.prompt.split("@")[0]
        except serial.serialutil.SerialException as oops:
            if 'PermissionError' in str(oops):
                uart_error = port + ' is present, but already used. Use \'uarts()\' to list available COM ports'
                logging.error("%s %s" % (self.nickname, str(uart_error)))
            if 'FileNotFoundError' in str(oops):
                uart_error = ' No ' + port + ' COM port. Use \'uarts()\' to list available COM ports after connecting.'
                uart_error += '\nCurrently available ports:\n' + uarts()
                logging.error("%s: %s" % (self.nickname, str(uart_error)))
                #print(uarts())

    def write(self, text):
        if self.link is not None:
            if self.trace:
                print("UART sending  | ", end='' )
                print(text)
            self.link.write(bytes(str(text).strip() + '\r', 'utf-8'))

    def read(self, wait_ms=0):
        lines = []
        line = ''
        line_count = 0
        if self.link is not None:
            while True:
                read_line = self.link.readline()
                line = read_line.decode("utf-8", "strict").strip()
                if self.trace:
                    print("UART received | ", end='')
                    print(line)
                if line == '':
                    check_line = read_line.decode("utf-8", "strict").strip()
                    if check_line == '':
                        return "\n".join(lines)
                # Skip empty 'prompt' lines (when remote is a direct shell console)
                if self.prompt != line:
                    lines.append(line)
        return "\n".join(lines)

    def run(self, cmd, wait_ms=0):
        self.write(cmd)
        res = ''
        time.sleep(wait_ms/1000)
        lines = self.read(wait_ms).split('\n')
        if lines[0] == cmd:
            # Skip echo of 'cmd' (when remote is a direct shell console)
            del lines[0]
        res = '\n'.join(lines)
        return res


class Telnet(AbstractConnection):

    def __init__(self, name=None, user="pi", host="10.5.124.249", password=None):
        self.nickname = name if name else 'telnet'
        self.conn = 'TELNET ' + user + '@' + host
        super().__init__()
        if host:
            self.configure(user=user, host=host, password=password)

    def configure(self, user="pi", host="10.5.124.249", password=None):
        import telnetlib
        self.link = telnetlib.Telnet(user)
        self.link.read_until("login: ")
        self.link.write(user + "\n")
        if password:
            self.link.read_until("Password: ")
            self.link.write(password + "\n")

    def write(self, text):
        if self.link is not None:
            if self.trace:
                for line in text.strip().split('\n'):
                    print(str.format("%-8s S>>|  " % self.nickname), end='')
                    print(line)
            self.link.write(bytes(text.strip() + '\n', 'utf-8'))

    def read(self):
        if self.link is not None:
            res = self.link.read_all()
            if self.trace:
                for line in res.split('\n'):
                    print(str.format("<<S %8s|  " % self.nickname), end='')
                    print(line)
            return res
        else:
            return ''

    def run(self, cmd, wait_ms=0):
        self.write(cmd)
        time.sleep(wait_ms/1000.0)
        return self.read()


class Ssh(AbstractConnection):

    def __init__(self, name=None, user="pi", host="10.5.124.249", port=22, password=""):
        self.nickname = name if name else 'ssh'
        self.conn = 'SSH ' + user + '@' + host + ':' + str(port)
        super().__init__()
        if host:
            self.configure(user=user, host=host, port=port, password=password)

    def configure(self, user="pi", host="10.5.124.249", port=22, password="default_password"):
        import SshTarget
        self.link = SshTarget.SshTarget(user=user, host=host, name=self.nickname, port=port, password=password)

    def write(self, text):
        if self.link is not None:
            if self.trace:
                for line in text.strip().split('\n'):
                    print(str.format("%-8s S>>|  " % self.nickname), end='')
                    print(line)
            self.link.write(bytes(text.strip() + '\n', 'utf-8'))

    def read(self):
        if self.link is not None:
            res = self.link.read()
            if self.trace:
                for line in res.split('\n'):
                    print(str.format("<<S %8s|  " % self.nickname), end='')
                    print(line)
            return res
        else:
            return ''

    def run(self, cmd, wait_ms=0):
        self.write(cmd)
        time.sleep(wait_ms/1000.0)
        return self.read()


class Direct(AbstractConnection):

    def __init__(self, name=None):
        self.nickname = name if name else 'direct'
        self.command_res = None
        self.conn = 'Direct'
        super().__init__()

    def configure(self, *args, **kwargs):
        pass

    def write(self, text):
        if self.trace:
            for line in text.strip().split('\n'):
                print(str.format("%-8s D>>|  " % self.nickname), end='')
                print(line)
        self.command_res = os.popen(text).read().strip()

    def read(self):
        if self.command_res:
            res = self.command_res
            if self.trace:
                for line in res.split('\n'):
                    print(str.format("<<D %8s|  " % self.nickname), end='')
                    print(line)
            return res
        else:
            return ''

    def run(self, cmd, wait_ms=None):
        self.write(cmd)
        return self.read()


class WfxConnection(object):

    def __init__(self, nickname, **kwargs):
        self.nickname = nickname
        self.link = None
        self.trace = False

        if 'host' in kwargs:
            port = kwargs['port'] if 'port' in kwargs else ""
            if port == 'telnet':
                host = kwargs['host']
                #if 'user' not in kwargs:
                #    raise Exception("%s: Missing 'user'. Telnet Connection impossible to host %s" % (nickname, host))
                user = kwargs['user']
                print('%s: Configuring a Telnet connection to host %s for user %s' % (nickname, host, user))
                password = kwargs['password'] if 'password' in kwargs else None
                self.link = Telnet(nickname, host=host, user=user, password=password)

        if not self.link:
            if 'host' in kwargs:
                #if not loaded_paramiko:
                #    raise Exception("'paramiko'   is not installed. SSH connection impossible for " + nickname)
                host = kwargs['host']
                port = kwargs['port'] if 'port' in kwargs else 22
                user = kwargs['user'] if 'user' in kwargs else 'root'
                print('%s: Configuring a SSH connection to host %s for user %s' % (nickname, host, user))
                password = kwargs['password'] if 'password' in kwargs else None
                self.link = Ssh(nickname, host=host, user=user, port=port, password=password)

        if not self.link:
            if 'port' in kwargs:
                #if not loaded_serial:
                #    raise Exception("'serial'   is not installed. UART connection impossible for " + nickname)
                port = kwargs['port']
                user = kwargs['user'] if 'user' in kwargs else 'root'
                password = kwargs['password'] if 'password' in kwargs else ''
                print('%s: Configuring a UART connection using %s for user %s/%s' % (nickname, port, user, password))
                self.link = Uart(nickname, port=port, user=user, password=password)
                if self.link is None:
                    if port in uarts():
                        raise Exception(port + ' is detected but is not available. Check for other applications using ' + port)

        if not self.link:
            if not kwargs:
                print('%s: Configuring a Direct connection' % nickname)
                self.link = Direct(nickname)

    def write(self, text):
        if self.link is not None:
            if self.trace:
                for line in text.strip().split('\n'):
                    print(str.format("%-8s S>>|  " % self.nickname), end='')
                    print(line)
            self.link.write(text)

    def read(self):
        if self.link is not None:
            res = self.link.read()
            if self.trace:
                for line in res.split('\n'):
                    print(str.format("<<S %8s|  " % self.nickname), end='')
                    print(line)
            return res
        else:
            return ''

    def run(self, cmd, wait_ms=0):
        if self.trace:
            for line in cmd.strip().split('\n'):
                print(str.format("%-8s S>>|  " % self.nickname), end='')
                print(line)
        res = self.link.run(cmd, wait_ms)
        if self.trace:
            for line in res.split('\n'):
                print(str.format("<<S %8s|  " % self.nickname), end='')
                print(line)
        return res


# Functions allowing discovery of possible connections
def uarts():
    try:
        import serial
    except ImportError:
        return "'serial'     is not installed. UART connection impossible"
    com_ports = os.popen('python -m serial.tools.list_ports').read().replace(' ', '').strip().split('\n')
    res = ''
    for port in com_ports:
        try:
            serial.Serial(port)
        except serial.serialutil.SerialException as oops:
            if 'PermissionError' in str(oops):
                res += '%-5s (IN USE)\n' % port
        else:
            res += '%-5s (free)\n' % port
        finally:
            pass
    return res.strip()


def networks():
    try:
        import ifaddr
    except ImportError:
        return "ifaddr not installed. Can't list networks"
    adapters = ''
    all_adapters = ifaddr.get_adapters()
    for adapter in all_adapters:
        for ip in adapter.ips:
            if '::' not in str(ip.ip) and '169.' not in str(ip.ip):
                ip_add = ip.ip + "/" + str(ip.network_prefix)
                adapters += str.format("%-20s %s\n" % (ip_add, adapter.nice_name))
    return adapters


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        sys.stderr.write("This tools was developed for Python 3 and wasn't tested with Python 2.x\n")
        sys.exit(0)

    print('You\'re using a ', sys.platform, 'platform')

    print(uarts())
    print(networks())

    #uart = WfxConnection('Uart', port='COM7', user='root', password='')
    uartpi = WfxConnection('Uart', port='COM19', user='pi', password='default_password')
    #tel = Telnet('telnet', host='10.5.124.249', user='pi', port='telnet', password='default_password')
    me = Direct('WinPC')

    uart26 = WfxConnection('Uart', port='COM26', user='root', password='')
    eth = Ssh('master', host='rns-SD3-rc7', user='pi', port=22, password='default_password')

    print("me     path: " + me.run('path'))
    print("uart26 uname -a: " + uart26.run('uname -a'))
    print("eth    uname -a: " + eth.run('uname -a'))
    print("uartpi uname -a: " + uartpi.run('uname -a'))
