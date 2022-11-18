#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""wfx_test_target.py
"""

import re
import sys
import time

sys.path.append('../connection')
sys.path.append('connection')

from wfx_connection import *
from pds_compress import compress_string
from wfx_pds_tree import *

pds_env = dict()
pds_env['TEST_FEATURE_ROOT'] = "/home/pi/siliconlabs/wfx-linux-tools/test-feature/"
pds_env['PDS_ROOT'] = pds_env['TEST_FEATURE_ROOT'] + "PDS/"
pds_env['PDS_CURRENT_FILE'] = "/tmp/current_pds_data.in"
pds_env['SEND_PDS_FILE'] = "/sys/kernel/debug/ieee80211/phy0/wfx/send_pds"
pds_env['PDS_DEFINITION_ROOT'] = ""
pds_env['PDS_DEFINITION_FILE'] = "definitions.in"
pds_env['required_options'] = []
pds_env['useful_options'] = []


class WfxTestTarget(object):
    global pds_env
    debug_color = "\033[95m"
    error_color = "\033[91m"
    write_color = "\033[94m"
    read_color  = "\033[92m"
    set_color   = "\033[93m"
    reset_color = "\033[0;0m"

    def __init__(self, nickname, **kwargs):
        self.trace = False
        self.human_trace = False
        self.compressed_trace = False
        self.nickname = nickname
        self.test_data = PdsTree()
        self.link = None
        self.required_options = pds_env['required_options']
        self.useful_options = pds_env['useful_options']
        self.fmac_cli = False

        if 'host' in kwargs:
            host = kwargs['host']
            port = kwargs['port'] if 'port' in kwargs else 22
            user = kwargs['user'] if 'user' in kwargs else 'root'
            pkey = kwargs['pkey'] if 'pkey' in kwargs else None
            print('%s: Configuring a SSH connection to host %s for user %s' % (nickname, host, user))
            password = kwargs['password'] if 'password' in kwargs else None
            self.link = Ssh(nickname, host=host, user=user, port=port, password=password, pkey=pkey)

        if not self.link:
            if 'port' in kwargs:
                port = kwargs['port']
                user = kwargs['user'] if 'user' in kwargs else ''
                password = kwargs['password'] if 'password' in kwargs else ''
                print('%s: Configuring a UART connection using %s/%s' % (nickname, port, user))
                self.link = Uart(nickname, port=port, user=user, password=password)
                if self.link is None:
                    if port in uarts():
                        raise Exception(port + ' is detected but is not available. Check for other applications using ' + port)

        if not self.link:
            print('%s: Configuring a Direct connection' % nickname)
            self.link = Direct(nickname)

        agent_version = self.run('wfx_test_agent read_agent_version')
        if 'no command found' in agent_version.lower():
            self.fmac_cli = True # 'wfx_test_agent' will be replaced by 'wifi test' in all commands
            agent_version = self.run('wfx_test_agent read_agent_version')
            if not 'no command found' in agent_version.lower():
                print(f"The dut is a FMAC CLI target... (agent_version == {agent_version})")
        else:
            self.fmac_cli = False

        if 'fw_version' in kwargs:
            fw_version = kwargs['fw_version']
            print("%s: fw_version forced (%s)" % (self.nickname, fw_version))
        else:
            fw_version = self.run('wfx_test_agent read_fw_version')
            if not re.match("\d+\.\d+\.\d+", fw_version):
                fw_version = self.test_data.max_fw_version
                print("%s: No fw_version retrieved from HW, using max_fw_version (%s)" % (self.nickname, fw_version))
            else:
                print("%s: fw_version retrieved from HW (%s)" % (self.nickname, fw_version))
            agent_version = self.run('wfx_test_agent --help')
            if agent_version == '':
                agent_error = ' No \'wfx_test_agent\' on ' + nickname + '. Communication is OK, but we miss the agent!!'
                raise Exception("%s %s" % (self.nickname, str(agent_error)))
        self.test_data.fill_tree(fw_version)
        print('%s: tree filled for FW%s' % (self.nickname, fw_version))

    def write(self, text):
        if self.link is not None:
            self.link.write(text)

    def read(self):
        if self.link is not None:
            return self.link.read()
        else:
            return ''

    def run(self, cmd, wait_ms=0):
        if self.link is not None:
            if self.fmac_cli:
                cmd = cmd.replace('wfx_test_agent', 'wifi test')
            return self.link.run(cmd, wait_ms).replace('\n>', '')
        else:
            return ''

    def _prepare_test_data(self, parameters):
        _subtree = self.test_data.sub_tree(parameters)
        pds_sections = _subtree.pretty()

        pds_string = "#include \"" + pds_env['PDS_DEFINITION_ROOT'] + pds_env['PDS_DEFINITION_FILE']\
                     + "\"\n\n" + pds_compatibility_text + pds_sections
        compressed_string = compress_string(pds_string)
        if self.human_trace:
            print('human readable: ' + pds_string)
        if self.compressed_trace:
            print('compressed  as: ' + compressed_string)
        if ":error:" in compressed_string:
            err = "WARNING: test data compression error! " + compressed_string + "\n"
            print(err)
            add_pds_warning(err)

        return compressed_string

    def _send_test_data(self, compressed_string):
        res = ''
        if ":error:" in compressed_string:
            res += "WARNING: No pds data sent! " + compressed_string + "\n"
            add_pds_warning("WARNING: No pds data sent! " + compressed_string + "\n")
        else:
            cmd = 'wfx_test_agent write_test_data  \"' + compressed_string + '\"'
            res = self.run(cmd)
        return res.strip()

    def _prepare_and__send_test_data(self, parameters, send_data):
        compressed_string = self._prepare_test_data(parameters)
        if send_data:
            self._send_test_data(compressed_string)

    def wfx_set_dict(self, param_dict, send_data=1):
        res = ''
        parameters = []
        for p, v in param_dict.items():
            parameter = str(p)
            value = str(v)
            res += parameter + '  '
            res += str(self.test_data.set(parameter, value)) + '     '
            parameters.append(parameter)
        if self.trace:
            print(str.format("%-8s SET|  " % self.nickname), self.set_color + res.strip() + self.reset_color)
        self._prepare_and__send_test_data(parameters, send_data)
        return res.strip()

    def wfx_get_list(self, param_list, mode='verbose'):
        res = ''
        if type(param_list) is str:
            my_list = []
            for item in param_list.split(","):
                my_list.append(str(item).strip())
            param_list = my_list
        if type(param_list) is set:
            my_list = []
            for list_item in param_list:
                for item in list_item.split(","):
                    my_list.append(str(item).strip())
            param_list = my_list
        for parameter in param_list:
            if mode == 'verbose':
                res += parameter + '  '
            res += self.test_data.get(parameter) + '     '
        return res.strip()


if __name__ == '__main__':
    print('You\'re using a ', sys.platform, 'platform')

    print(uarts())
    print(networks())

    eth = WfxTestTarget('Pi_186', host='10.5.124.249', user='pi', port=2186, password='default_password')
    uart_out = WfxTestTarget('OutSerial', port='COM8', fw_version='2.1.2')
    uart_in = WfxTestTarget('InSerial', port='COM19')
    me = WfxTestTarget('ThisPC')

    me.link.trace = False
    print(me.run('dir'))
    print(me.run('dir wfx_*.py'))

    uart_out.link.trace = True
    uart_in.link.trace = True
    eth.link.trace = True

    uart_out.write('Hello\nHave a nice day!')
    print(uart_in.read())

    uart_out.write('test_agent send_data 123456')
    print(uart_in.read())

    eth.write('uname -r')
    print(eth.read())

    print(eth.wfx_get_list({'NB_FRAME', 'RF_PORTS'}))
    eth.wfx_set_dict({'NB_FRAME': 0})
    print(eth.wfx_get_list({'NB_FRAME', 'RF_PORTS'}))

    time.sleep(2)
    eth.wfx_set_dict({"TEST_MODE": "tx_packet", "NB_FRAME": 100})
    print(eth.test_data.pretty())
    eth.wfx_set_dict({"TEST_MODE": "rx"})
    time.sleep(2)
    eth.wfx_set_dict({"TEST_MODE": "tx_packet", "NB_FRAME": 100})
