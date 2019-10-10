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

    def close(self):
        raise NotImplementedError()


class Uart(AbstractConnection):

    def __init__(self, nickname="uart", port=None, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0.1, user='', password='', trace=False):
        try:
            import serial
        except ImportError:
            print("'serial'     is not installed. UART connection impossible")
        else:
            logging.getLogger("serial").setLevel(logging.WARNING)
            #print("imported 'serial'")
        object.__init__(self)
        self.nickname = nickname
        self.conn = 'UART ' + str(port) + '/' + str(baudrate) + '/' + str(bytesize) + '/' + parity + '/' + str(stopbits)
        self.user = user
        self.password = password
        self.hostname = 'foo'
        self.prompt = 'bar'
        self.max_response_ms = 500
        self.trace = trace
        if port:
            self.configure(port, baudrate, bytesize, parity, stopbits, timeout)
            return

    def test_connectivity(self):
        # send once to flush possible errors
        self.write('')
        time.sleep(500/1000)
        self.write('')
        time.sleep(500/1000)
        try:
            res = self.read_raw()
        except:
            print("error on first write/read, retrying...")
            self.write('')
            time.sleep(0.5)
            try:
                res = self.read_raw()
            except:
                print("'ERROR: " + self.nickname + " can NOT connect")
                return 0
        if 'login:' in res:
            self.log_in()
        print(self.nickname + " connected")
        return 1

    def log_in(self):
        print("sending login '" + self.user + "'...")
        self.write(self.user)
        time.sleep(500/1000)
        login_res = self.link.read_all().decode("utf-8")
        print("login res : " + login_res)
        if 'assword:' in login_res:
            print("sending password '" + self.password + "'...")
            self.write(self.password)
            time.sleep(500/1000)
            password_res = self.link.read_all().decode("utf-8")
            print("password_res : " + password_res)

    def get_prompt(self):
        self.write('')
        time.sleep(500/1000)
        #res = self.read_raw()
        res = self.link.read_all().decode("utf-8")
        split_res = res.split('\n')
        res_len = len(split_res)
        last_res = split_res[res_len-1]
        if len(last_res) > 2:
            self.prompt = split_res[res_len-1].strip()
            print(self.nickname + " prompt set to '" + self.prompt + "'")

    def configure(self, port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1):
        import serial
        self.connection = None
        self.link = None
        self.prompt = None
        try:
            self.link = serial.serial_for_url(url=port, baudrate=baudrate, bytesize=bytesize, parity=parity,
                                      stopbits=stopbits, timeout=timeout, write_timeout=None)
            self.connection = port
            if self is None:
                raise Exception("%s %s" % (self.nickname, 'Can not connect to ' + port))

            # from https://pyserial.readthedocs.io/en/latest/appendix.html#faq:
            # A delay after opening the port, before the first write(), is recommended in this situation. E.g. a time.sleep(1)
            time.sleep(1)
            self.test_connectivity()
            if self.user != '':
                self.get_prompt()

        except serial.serialutil.SerialException as oops:
            if 'PermissionError' in str(oops):
                uart_error = port + ' is present, but already used. Use \'uarts()\' to list available COM ports'
                logging.error("%s %s" % (self.nickname, str(uart_error)))
            if 'FileNotFoundError' in str(oops):
                uart_error = ' No ' + port + ' COM port. Use \'uarts()\' to list available COM ports after connecting.'
                uart_error += '\nCurrently available ports:\n' + uarts()
                logging.error("%s: %s" % (self.nickname, str(uart_error)))
                print(uart_error)

    def write(self, text):
        if self.link is not None:
            if self.trace:
                print("UART sending  '", end='' )
                print(text.strip(), end='')
                print("'")
            self.link.write(bytes(str(text).strip() + '\n', 'utf-8'))
            self.link.flush()
            time.sleep(5/1000)

    def read_raw(self):
        res = 'no uart link yet'
        if self.link is not None:
            start = time.time_ns()
            stop_time = start + self.max_response_ms*1000
            while time.time_ns() < stop_time:
                res = self.link.read_all().decode("utf-8")
                if len(res):
                    for read_line in res.split('\n'):
                        if self.trace:
                            print("UART received <" + read_line.strip() + ">")
                    return res
        return res

    def read_raw_lines(self):
        res = 'no uart link!'
        if self.link is not None:
            res = self.link.readline().decode("utf-8")
            if len(res):
                for read_line in res.split('\n'):
                    if self.trace:
                        print("UART received <" + read_line.strip() + ">")
                return res
        return res

    def read(self, wait_ms=0):
        lines = []
        if self.link is not None:
            start = time.time_ns()
            if self.user != '':
                # OS target: wait for prompt 
                stop_time = start + (self.max_response_ms*1E6)
                while True:
                    read_lines = self.read_raw_lines()
                    for line in read_lines.split('\n'):
                        if len(line):
                            # return when receiving the prompt
                            if line.strip() == self.prompt:
                                # print("prompt received after " + str((time.time_ns()-start)/1E6))
                                return "\n".join(lines)
                            else:
                                lines.append(line)
                        else:
                            # skip empty lines
                            # print("empty... after " + str((time.time_ns()-start)/1E6))
                            ...
                    now = time.time_ns()
                    if now > stop_time:
                        print("read timeout after " + str((now-start)/1E6))
                        break
            else:
                # RTOS target, exit on timeout
                stop_time = start + self.max_response_ms*1E6
                while time.time_ns() < stop_time:
                    read_lines = self.read_raw_lines()
                    for line in read_lines.split('\n'):
                        line = line.strip()
                        if len(line):
                            lines.append(line)
                            break
        return "\n".join(lines)

    def run(self, cmd, wait_ms=0):
        self.write(cmd)
        res = ''
        time.sleep(wait_ms/1000)
        lines = self.read(wait_ms).split('\n')
        if lines[0].strip() == cmd.strip():
            # Skip echo of 'cmd' (when remote is a direct shell console)
            del lines[0]
        res = '\n'.join(lines)
        return res

    def close(self):
        if self.link is not None:
            self.link.close()
            time.sleep(1)


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

        # TELNET
        if 'host' in kwargs:
            port = kwargs['port'] if 'port' in kwargs else ""
            if port == 'telnet':
                host = kwargs['host']
                user = kwargs['user']
                password = kwargs['password'] if 'password' in kwargs else None
                print('%s: Configuring a Telnet connection to host %s for user %s' % (nickname, host, user))
                self.link = Telnet(nickname, host=host, user=user, password=password)

        # SSH
        if not self.link:
            if 'host' in kwargs:
                host = kwargs['host']
                port = kwargs['port'] if 'port' in kwargs else 22
                user = kwargs['user'] if 'user' in kwargs else 'root'
                password = kwargs['password'] if 'password' in kwargs else None
                print('%s: Configuring a SSH connection to host %s port %d for user %s' % (nickname, host, port, user))
                self.link = Ssh(nickname, host=host, user=user, port=port, password=password)

        # UART
        if not self.link:
            if 'port' in kwargs:
                port = kwargs['port']
                user = kwargs['user'] if 'user' in kwargs else 'root'
                password = kwargs['password'] if 'password' in kwargs else ''
                self.trace = kwargs['trace'] if 'trace' in kwargs else False
                print('%s: Configuring a UART connection using %s for user %s' % (nickname, port, user))
                self.link = Uart(nickname, port=port, user=user, password=password, trace=self.trace)
                if self.link is None:
                    if port in uarts():
                        raise Exception(port + ' is detected but is not available. Check for other applications using ' + port)

        # DIRECT
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

    def close(self):
        self.link.close()

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

    # RTOS/uart: no 'user', no 'password'
    #uart = WfxConnection('RTOS', port='COM19')
    # Linux/uart: 'user' & 'password'
    #uart = WfxConnection('Uart', port='COM19', user='pi', password='default_password')
    # TELNET target: host & port = 'telnet' + 'user' & 'password'
    #tel = WfxConnection('telnet', host='10.5.124.249', user='pi', port='telnet', password='default_password')
    #me = Direct('WinPC')
    #for m in [110, 100, 95, 90, 80, 70, 60, 50, 40, 30, 20, 10, 5, 0]:
    for m in [2, 1, 0]:
        uart = WfxConnection('Glory', port='COM26', baudrate=115200, user='root', password='')
        u = uart.run('uname -a')
        if 'GNU/Linux' in u:
            print("---\nuart uname -a: " + u + "\n---")
            print(uart.run('dmesg | tail'))
            print(uart.run('ip address show wlan0'))
            print(uart.run('wfx_test_agent --help'))
            break
        else:
            print("---\nERROR ! uart uname -a: " + u + "\n---")
        uart.close()
    for m in [2, 1, 0]:
        uart = WfxConnection('Pi', port='COM19', baudrate=115200, user='pi', password='default_password')
        u = uart.run('uname -a')
        if 'GNU/Linux' in u:
            print("---\nuart uname -a: with " + u + "\n---")
            print(uart.run('dmesg | tail'))
            print(uart.run('ip address show wlan0'))
            print(uart.run('wfx_test_agent --help'))
            break
        else:
            print("---\nERROR ! uart uname -a: with " + u + "\n---")
            break
        uart.close()
    for m in [2, 1, 0]:
        ssh = WfxConnection('Pi', host='rns-SD3-rc7', user='pi', password='default_password')
        u = ssh.run('uname -a')
        if 'GNU/Linux' in u:
            print("---\nssh uname -a: with " + u + "\n---")
            print(ssh.run('dmesg | tail'))
            print(ssh.run('ip address show wlan0'))
            print(ssh.run('wfx_test_agent --help'))
            break
        else:
            print("---\nERROR ! ssh uname -a: with " + u + "\n---")
            break
        ssh.close()
