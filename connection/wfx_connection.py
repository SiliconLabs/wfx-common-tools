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
    debug_color = "\033[95m"
    error_color = "\033[91m"
    write_color = "\033[94m"
    read_color  = "\033[92m"
    set_color   = "\033[93m"
    reset_color = "\033[0;0m"

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

    def __init__(self, nickname="uart", port=None, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1, user='', password='', trace=False):
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
        print(self.error_color + "user: " + self.user + self.reset_color)
        if self.user != '':
            # 'OS' UART relies on the prompt to return, so a high timeout is not and issue
            self.max_response_ms = 5000
        else:
            # 'RTOS' UART can only end a 'read' upon a timeout.
            # 'timeout' is the read timout of the port. It is not critical
            # Following each read the wait is increased by self.max_response_ms, so this value is critical
            #  self.max_response_ms may need to be adapted, depending on the RTOS response times
            # If it's too small some messages may be lost
            # If it's too high each 'read' is long
            self.max_response_ms = 100
            timeout = 20/1000
        self.trace = trace
        self.debug = False
        self.last_write = ''
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
        self.write('cd ~')
        time.sleep(500/1000)
        #res = self.read_raw()
        res = self.link.read_all().decode("utf-8")
        split_res = res.split('\n')
        res_len = len(split_res)
        last_res = split_res[res_len-1]
        if len(last_res) > 2:
            self.prompt = split_res[res_len-1].rstrip()
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
            if self.debug:
                print("  DEBUG   " + self.nickname + self.debug_color + " write " + self.debug_color + text + self.reset_color + "...")
            if self.trace:
                print("UART sending  '"  + self.write_color + text.rstrip() + self.reset_color + "'")
            self.last_write = text
            self.link.write(bytes(str(text).rstrip() + '\n', 'utf-8'))
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
                            print("UART received <" + read_line.rstrip() + ">")
                    return res
        return res

    def read_raw_line(self):
        res = 'no uart link!'
        if self.link is not None:
            res = ''
            r = self.link.readline()
            try:
                line = r.decode("utf-8")
            except:
                print(self.error_color + "UART ERROR decoding line" + self.reset_color)
                line = ''
            if len(line):
                if self.trace:
                    print("UART received <"  + self.read_color + line.rstrip() + self.reset_color + ">")
                return line.rstrip()
        return res

    def read(self, wait_ms=0):
        lines = []
        start = time.time_ns()
        if self.link is not None:
            stop_time = start + (self.max_response_ms*1E6)
            if self.user != '':
                # OS target: wait for prompt
                while True:
                    line = self.read_raw_line()
                    if len(line):
                        # return when receiving the prompt
                        if line.rstrip() == self.prompt:
                            if self.debug:
                                print("  DEBUG   " + self.nickname + self.debug_color + " prompt received after " + str((time.time_ns()-start)/1E6) + self.reset_color)
                                ...
                            break
                        else:
                            lines.append(line)
                            stop_time = start + (self.max_response_ms*1E6)
                    else:
                        # skip empty lines
                        if self.debug:
                            print("  DEBUG   " + self.nickname + self.debug_color + " empty... after " + str((time.time_ns()-start)/1E6) + self.reset_color)
                            ...
                        ...
                    now = time.time_ns()
                    if now > stop_time:
                        print(self.error_color + "read timeout after " + str((now-start)/1E6) + self.write_color + " last_write: " + self.last_write + self.reset_color)
                        break
            else:
                # RTOS target, exit on timeout
                while time.time_ns() < stop_time:
                    line = self.read_raw_line()
                    if len(line):
                        lines.append(line.rstrip())
                        stop_time = time.time_ns() + (self.max_response_ms*1E6)
                        if self.debug:
                            print("  DEBUG   " + self.nickname + self.debug_color + " line received after " + str((time.time_ns()-start)/1E6) + self.reset_color)
                            ...
        if self.debug:
            print("  DEBUG   " + self.nickname + self.debug_color + " full message received after " + str((time.time_ns()-start)/1E6) + self.reset_color)
            ...
        return "\n".join(lines)

    def run(self, cmd, wait_ms=0):
        self.write(cmd)
        res = ''
        time.sleep(wait_ms/1000)
        lines = self.read().split('\n')
        if lines[0].rstrip() == cmd.rstrip():
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
                for line in text.rstrip().split('\n'):
                    print(str.format("%-8s S>>|  " % self.nickname), end='')
                    print(line)
            self.link.write(bytes(text.rstrip() + '\n', 'utf-8'))

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
                for line in text.rstrip().split('\n'):
                    print(str.format("%-8s S>>|  " % self.nickname), end='')
                    print(line)
            self.link.write(bytes(text.rstrip() + '\n', 'utf-8'))

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
            for line in text.rstrip().split('\n'):
                print(str.format("%-8s D>>|  " % self.nickname), end='')
                print(line)
        self.command_res = os.popen(text).read().rstrip()

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
                user = kwargs['user'] if 'user' in kwargs else ''
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
                for line in text.rstrip().split('\n'):
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
            for line in cmd.rstrip().split('\n'):
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
    com_ports = os.popen('python -m serial.tools.list_ports').read().replace(' ', '').rstrip().split('\n')
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
    return res.rstrip()


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

    # RTOS/uart: port + no 'user', no 'password'
    #dut = WfxConnection('RTOS_uart', port='COM19')
    # Linux/uart: port + 'user' & 'password'
    #dut = WfxConnection('Linux_uart', port='COM19', user='pi', password='default_password')
    #dut = WfxConnection('Linux_ssh', host='rns-SD3-rc7, user='pi', password='default_password')
    # TELNET target: host & port = 'telnet' + 'user' & 'password'
    #dut = WfxConnection('telnet', host='10.5.124.249', user='pi', port='telnet', password='default_password')
    dut = Direct('myPC')
    u = dut.run('uname -a')
    if 'GNU/Linux' in u:
        print("---\ndut uname -a: " + u + "\n---")
    dut.link.trace = True
    print(dut.run('cat $(which wfx_test_agent)'))
    dut.close()
