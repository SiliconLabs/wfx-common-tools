#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set sw=4 expandtab:
#
# Created: 2019-08-06
# Main authors:
#     - Marc Dorval <marc.dorval@silabs.com>
#
# Copyright (c) 2019, Silicon Laboratories
# See license terms contained in COPYING file
#

# Use wfx_pta_data to prepare PTA bytes from input parameters
#  then send them to the target
#
#

from __future__ import print_function

# If you modify this file, please don't forget to increment version number.
__version__ = "0.2.1"

import sys

sys.path.append('../connection')

from wfx_connection import *
from wfx_pta_data import *

HI_STATUS_SUCCESS = '0'
HI_STATUS_FAILURE = '1'
HI_INVALID_PARAMETER = '2'
HI_ERROR_UNSUPPORTED_MSG_ID = '4'


class WfxPtaTarget(object):

    def __init__(self, nickname, **kwargs):
        self.nickname = nickname
        self.pta_data = None
        self.pta_mode = 'quiet'
        self.link = None

        if 'host' in kwargs:
            host = kwargs['host']
            port = kwargs['port'] if 'port' in kwargs else 22
            user = kwargs['user'] if 'user' in kwargs else 'root'
            print('%s: configuring a SSH connection to host %s for user %s (port %d)' % (nickname, host, user, port))
            password = kwargs['password'] if 'password' in kwargs else None
            self.link = Ssh(nickname, host=host, user=user, port=port, password=password)

        if not self.link:
            if 'port' in kwargs:
                port = kwargs['port']
                print('%s: configuring a UART connection using %s' % (nickname, port))
                self.link = Uart(nickname, port=port)
                if self.link is None:
                    if port in uarts():
                        raise Exception(port + ' is detected but is not available. Check for other applications using ' + port)

        if not self.link:
            if not kwargs:
                print('%s: configuring a Direct connection' % nickname)
                self.link = Direct(nickname)

    def write(self, text):
        if self.link is not None:
            #self.link.write(text.encode('ascii'))
            self.link.write(text)

    def read(self):
        if self.link is not None:
            return self.link.read()
        else:
            return ''

    def run(self, cmd, wait_ms=0):
        self.write(cmd)
        time.sleep(wait_ms/1000.0)
        return self.read()

    def pta_help(self):
        pta = WfxPtaData()
        pta.set_args('--help')
        return pta.data()

    def prepare_pta_data(self, args_text, mode):
        pta = WfxPtaData(mode)
        pta.set_args(args_text)
        self.pta_data = pta.data()

    def settings(self, options, mode='quiet'):
        return self.send_pta('settings', options, mode)

    def priority(self, options, mode='quiet'):
        return self.send_pta('priority', options, mode)

    def state(self, options, mode='quiet'):
        return self.send_pta('state', options, mode)

    def send_pta(self, command, options, mode='quiet'):
        self.prepare_pta_data(command + ' ' + options, mode)
        if self.pta_data is not None:
            send_result = self.link.run(r'wfx_exec wfx_hif_send_msg "' + self.pta_data + r'"')
            if send_result == HI_STATUS_SUCCESS:
                return 'HI_STATUS_SUCCESS'
            else:
                if send_result == HI_STATUS_FAILURE:
                    return 'HI_STATUS_FAILURE'
                elif send_result == HI_INVALID_PARAMETER:
                    return 'HI_INVALID_PARAMETER'
                elif send_result == HI_ERROR_UNSUPPORTED_MSG_ID:
                    return 'HI_ERROR_UNSUPPORTED_MSG_ID'
                else:
                    if str(send_result) != "":
                        return "ERROR: unknown_error_sending PTA data: '" + str(send_result) + "'"
                    else:
                        return "ERROR: unknown_error_sending PTA data"
        else:
            return "Error applying " + command + " '" + options + "'"

    def selftest(self, mode='verbose'):
        stored_trace = self.link.trace
        self.link.trace = True
        print('settings result: ' + self.settings('--config 3w_example', mode=mode))
        print('priority result: ' + self.priority('--priority_mode balanced', mode=mode))
        print('state    result: ' + self.state('--state off', mode=mode))
        self.link.trace = stored_trace


def command_line_main():
    if 'verbose' in sys.argv:
        mode = 'verbose'
    else:
        mode = 'quiet'
    dut = WfxPtaTarget('Local')
    if 'verbose' in sys.argv:
        dut.trace = True
        dut.link.trace = True
        sys.argv.remove('verbose')
        mode = 'verbose'
    else:
        mode = 'quiet'
    sys.exit(dut.send_pta(sys.argv[1], ' '.join(sys.argv[2:]), mode))


def command_line_test():
    print('You\'re using a ', sys.platform, 'platform')

    print(uarts())
    print(networks())

    eth = WfxPtaTarget('pi', host='rns-SD3-rc7', user='pi', port=22, password='default_password')
    uart = WfxPtaTarget('OutSerial', port='COM8')

    dut = eth

    me = WfxPtaTarget('ThisPC')
    me.link.trace = False
    print(me.run('dir wfx_*.py'))

    print(dut.run('uname -a'))
    dut.link.trace = True

    # print(dut.pta_help())
    mode = 'quiet'
    dut.settings('--config 3w_example --request_signal_active_level low --first_slot_time 123', mode=mode)
    dut.settings('--pta_mode 1w_coex_master', mode=mode)
    dut.settings('--pta_mode 2w', mode=mode)
    dut.settings('--pta_mode 3w', mode=mode)
    dut.settings('--pta_mode 4w', mode=mode)
    dut.settings('--request_signal_active_level low', mode=mode)
    dut.settings('--priority_signal_active_level low', mode=mode)
    dut.settings('--freq_signal_active_level low', mode=mode)
    dut.settings('--grant_signal_active_level high', mode=mode)
    dut.settings('--coex_type generic', mode=mode)
    dut.settings('--coex_type ble', mode=mode)
    dut.settings('--default_grant_state no_grant', mode=mode)
    dut.settings('--simultaneous_rx_accesses true', mode=mode)
    dut.settings('--priority_sampling_time 3', mode=mode)
    dut.settings('--tx_rx_sampling_time 4', mode=mode)
    dut.settings('--freq_sampling_time 5', mode=mode)
    dut.settings('--grant_valid_time 6', mode=mode)
    dut.settings('--fem_control_time 7', mode=mode)
    dut.settings('--first_slot_time 8', mode=mode)
    dut.settings('--periodic_tx_rx_sampling_time 9', mode=mode)
    dut.settings('--coex_quota 1000', mode=mode)
    dut.settings('--wlan_quota 1234', mode=mode)
    dut.state('--state off')
    dut.state('--state on')
    dut.priority('--priority_mode coex_maximized')
    dut.priority('--priority_mode coex_high')
    dut.priority('--priority_mode balanced')
    dut.priority('--priority_mode wlan_high')
    dut.priority('--priority_mode wlan_maximized')
    dut.priority('--coex_prio_low 7')
    dut.priority('--coex_prio_high 7')
    dut.priority('--grant_coex 1')
    dut.priority('--grant_wlan 1')
    dut.priority('--protect_coex 1')
    dut.priority('--protect_wlan_tx 1')
    dut.priority('--protect_wlan_rx 1')
    return 0


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        sys.stderr.write("This tools was developed for Python 3 and was not tested with Python 2.x\n")
    if len(sys.argv) > 1:
        sys.exit(command_line_main())
    else:
        sys.exit(command_line_test())
