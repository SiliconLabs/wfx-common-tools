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
__version__ = "0.2"

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
            print('%s: Configuring a SSH connection to host %s for user %s (port %d)' % (nickname, host, user, port))
            password = kwargs['password'] if 'password' in kwargs else None
            self.link = Ssh(nickname, host=host, user=user, port=port, password=password)

        if not self.link:
            if 'port' in kwargs:
                port = kwargs['port']
                print('%s: Configuring a UART connection using %s' % (nickname, port))
                self.link = Uart(nickname, port=port)
                if self.link is None:
                    if port in uarts():
                        raise Exception(port + ' is detected but is not available. Check for other applications using ' + port)

        if not self.link:
            if not kwargs:
                print('%s: Configuring a Direct connection' % nickname)
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
        print('settings result: ' + self.settings('--Config 3W_NOT_COMBINED_BLE', mode=mode))
        print('priority result: ' + self.priority('--PriorityMode BALANCED', mode=mode))
        print('state    result: ' + self.state('--State OFF', mode=mode))
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
    dut.settings('--Config 3W_BLE --RequestSignalActiveLevel LOW --FirstSlotTime 123', mode=mode)
    dut.settings('--PtaMode 1W_COEX_MASTER', mode=mode)
    dut.settings('--PtaMode 2W', mode=mode)
    dut.settings('--PtaMode 3W', mode=mode)
    dut.settings('--PtaMode 4W', mode=mode)
    dut.settings('--RequestSignalActiveLevel LOW', mode=mode)
    dut.settings('--PrioritySignalActiveLevel LOW', mode=mode)
    dut.settings('--FreqSignalActiveLevel LOW', mode=mode)
    dut.settings('--GrantSignalActiveLevel HIGH', mode=mode)
    dut.settings('--CoexType GENERIC', mode=mode)
    dut.settings('--CoexType BLE', mode=mode)
    dut.settings('--DefaultGrantState NO_GRANT', mode=mode)
    dut.settings('--SimultaneousRxAccesses TRUE', mode=mode)
    dut.settings('--PrioritySamplingTime 3', mode=mode)
    dut.settings('--TxRxSamplingTime 4', mode=mode)
    dut.settings('--FreqSamplingTime 5', mode=mode)
    dut.settings('--GrantValidTime 6', mode=mode)
    dut.settings('--FemControlTime 7', mode=mode)
    dut.settings('--FirstSlotTime 8', mode=mode)
    dut.settings('--PeriodicTxRxSamplingTime 9', mode=mode)
    dut.settings('--CoexQuota 1000', mode=mode)
    dut.settings('--WlanQuota 1234', mode=mode)
    dut.state('--State OFF')
    dut.state('--State ON')
    dut.priority('--PriorityMode BALANCED')
    return 0


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        sys.stderr.write("This tools was developed for Python 3 and was not tested with Python 2.x\n")
    if len(sys.argv) > 1:
        sys.exit(command_line_main())
    else:
        sys.exit(command_line_test())
