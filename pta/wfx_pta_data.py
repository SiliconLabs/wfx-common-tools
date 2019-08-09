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

# Generate PTA bytes from input parameters
#

from __future__ import print_function

# If you modify this file, please don't forget to increment version number.
__version__ = "0.0"

import sys
import argparse


class PtaSettings(object):
    def __init__(self):
        super().__init__()
        self.pta_cmd = None


class WfxPtaData(object):

    HI_PTA_1W_WLAN_MASTER = 0
    HI_PTA_1W_COEX_MASTER = 1
    HI_PTA_2W = 2
    HI_PTA_3W = 3
    HI_PTA_4W = 4

    HI_PTA_LOW = 0
    HI_PTA_HIGH = 1

    HI_COEX_TYPE_GENERIC = 0
    HI_COEX_TYPE_BLE = 1

    HI_PTA_NO_GRANT = 0
    HI_PTA_GRANT = 1

    HI_PTA_FALSE = 0
    HI_PTA_TRUE = 1

    HI_PTA_PRIORITY_COEX_MAXIMIZED = 0x00000562
    HI_PTA_PRIORITY_COEX_HIGH = 0x00000462
    HI_PTA_PRIORITY_BALANCED = 0x00001461
    HI_PTA_PRIORITY_WLAN_HIGH = 0x00001851
    HI_PTA_PRIORITY_WLAN_MAXIMIZED = 0x00001A51

    settings_parameters = [
        #  Parameter, type, bytes, choices, default, help
        ('Config', str, 1, ['3W_NOT_COMBINED_BLE', '3W_COMBINED_BLE', '3W_NOT_COMBINED_ZIGBEE', '3W_COMBINED_ZIGBEE'],
         None, """
              Preset configurations for common use cases
                  (presets required non-default 'settings' options,
                  these can then be overwritten using options listed below)"""),
        ('PtaMode', int, 1, ['1W_WLAN_MASTER', '1W_COEX_MASTER', '2W', '3W', '4W'], 0, """
              PTA mode selection"""),
        ('RequestSignalActiveLevel', int, 1, ['LOW', 'HIGH'], HI_PTA_HIGH, """
              Active level on REQUEST signal, provided by Coex to request the RF"""),
        ('PrioritySignalActiveLevel', int, 1, ['LOW', 'HIGH'], HI_PTA_HIGH, """
              Active level on PRIORITY signal, provided by Coex to set the priority of the request"""),
        ('FreqSignalActiveLevel', int, 1, ['LOW', 'HIGH'], HI_PTA_HIGH, """
              Active level on FREQ signal, provided by Coex in 4-wire mode 
              when Coex and Wlan share the same band"""),
        ('GrantSignalActiveLevel', int, 1, ['LOW', 'HIGH'], HI_PTA_LOW, """
              Active level on GRANT signal, generated by PTA 
              to grant the RF to Coex"""),
        ('CoexType', int, 1, ['GENERIC', 'BLE'], HI_COEX_TYPE_GENERIC, """
              Coex type"""),
        ('DefaultGrantState', int, 1, ['NO_GRANT', 'GRANT'], HI_PTA_GRANT, """
              State of the GRANT signal before arbitration at GrantValidTime"""),
        ('SimultaneousRxAccesses', int, 1, ['0', '1'], HI_PTA_FALSE, """
          (uint8),  Boolean to allow both Coex and Wlan to receive concurrently, 
              also named combined mode"""),
        ('PrioritySamplingTime', int, 1, None, 9, """
          (uint8),  Time in microseconds from the Coex request to the sampling of the
          priority on PRIORITY signal (1 to 31),"""),
        ('TxRxSamplingTime', int, 1, None, 50, """
          (uint8),  Time in microseconds from the Coex request to the 
              sampling of the directionality on PRIORITY signal (PrioritySamplingTime to 63)"""),
        ('FreqSamplingTime', int, 1, None, 70, """
          (uint8),  Time in microseconds from the Coex request to the 
              sampling of the freq-match information on FREQ signal (1 to 127)"""),
        ('GrantValidTime', int, 1, None, 72, """
          (uint8),  Time in microseconds from Coex request to the 
              GRANT signal assertion (max(TxRxSamplingTime, FreqSamplingTime), to 0xFF),"""),
        ('FemControlTime', int, 1, None, 140, """
          (uint8),  Time in microseconds from Coex request to the 
              control of FEM (GrantValidTime to 0xFF),"""),
        ('FirstSlotTime', int, 1, None, 150, """
          (uint8),  Time in microseconds from the Coex request to the 
              beginning of reception or transmission (GrantValidTime to 0xFF),"""),
        ('PeriodicTxRxSamplingTime', int, 2, None, 1, """
          (uint16), Period in microseconds from FirstSlotTime of following samplings of the 
              directionality on PRIORITY signal (1 to 1023),"""),
        ('CoexQuota', int, 2, None, 0, """
          (uint16), Duration in microseconds for which RF is granted to Coex 
              before it is moved to Wlan"""),
        ('WlanQuota', int, 2, None, 0, """
          (uint16), Duration in microseconds for which RF is granted to Wlan 
              before it is moved to Coex""")
    ]

    priority_parameters = [
        #  Parameter, type, bytes,  choices, default, help
        ('PriorityMode', str, 4, ['COEX_MAXIMIZED', 'COEX_HIGH', 'BALANCED', 'WLAN_HIGH', 'WLAN_MAXIMIZED'], None, """
            COEX_MAXIMIZED = 0x0562 : Maximizes priority to COEX, WLAN connection is not ensured.  
            COEX_HIGH      = 0x0462 : High priority to COEX, targets low-latency to COEX. 
            BALANCED       = 0x1461 : Balanced PTA arbitration, WLAN acknowledge receptions are protected. 
            WLAN_HIGH      = 0x1851 : High priority to WLAN, protects WLAN transmissions. 
            WLAN_MAXIMIZED = 0x1A51 : Maximizes priority to WLAN""")
    ]

    state_parameters = [
        #  Parameter, type, bytes,  choices, default, help
        ('State', str, 4, ['ON', 'OFF'], 'OFF', """
            PTA state on/off""")
    ]

    def __init__(self, mode=None, **kwargs):
        self.g_settings = PtaSettings
        self.g_settings.pta_cmd = None
        self.sysargs = sys.argv[1:]
        self.mode = mode if mode else 'quiet'

    def set_args(self, args=None):
        if args is not None:
            self.sysargs = args.split(' ')
        else:
            self.sysargs = []

    def print_if_verbose(self, txt, end=None):
        if self.mode == 'verbose':
            print(txt, end=end)

    def data(self):
        self.print_if_verbose(self.sysargs)
        self.g_settings = PtaSettings
        self.g_settings.pta_cmd = None
        user_options = self.parse_cmdline(self, self.sysargs)
        # self.print_if_verbose(user_options)
        self.apply_options(self, user_options)
        return self.pta_bytes()

    @staticmethod
    def print_keys(self, c, name=None):
        for k in c.__dict__.keys():
            if '__' not in k:
                if name is None:
                    self.print_if_verbose("%-30s %s" % (k, c.__dict__[k]))
                else:
                    self.print_if_verbose("%s.%-30s %s" % (name, k, c.__dict__[k]))

    @staticmethod
    def parse_cmdline(self, args):
        parser = argparse.ArgumentParser(usage="%(prog)s <settings/priority/state> [options]...",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description="""
        Prepare and send PTA parameters depending on the selected pta_cmd
        """, epilog="""
        Examples:
        python wfx_pta.py settings --Config 3W_COMBINED_BLE
        python wfx_pta.py settings --Config 3W_NOT_COMBINED_BLE --FirstSlotTime 123
        python wfx_pta.py settings --Config 3W_NOT_COMBINED_BLE --FirstSlotTime 123 --PrioritySamplingTime 12
        python wfx_pta.py priority --PriorityMode BALANCED
        python wfx_pta.py state --State ON
        python wfx_pta.py state --State OFF
        """)
        parser.add_argument("pta_cmd", choices=['settings', 'priority', 'state'],
                            help="pta_cmd <settings/priority/state>")
        parser.add_argument('--version', action='version',
                            version='%(prog)s {version}'.format(version=__version__))

        parser_settings = parser.add_argument_group('settings options')
        for item in self.settings_parameters:
            _name, _type, _bytes, _choices, _default, _help = item
            if _default is None:
                parser_settings.add_argument('--' + _name, type=_type, default=_default, choices=_choices, help=_help)
            else:
                parser_settings.add_argument('--' + _name, type=_type, default=_default, choices=_choices, help=_help +
                                             ' (default ' + str(_default) + ')')

        parser_priority = parser.add_argument_group('priority options')
        for item in self.priority_parameters:
            _name, _type, _bytes, _choices, _default, _help = item
            parser_priority.add_argument('--' + _name, type=_type, default=_default, choices=_choices, help=_help)

        parser_state = parser.add_argument_group('state options')
        for item in self.state_parameters:
            _name, _type, _bytes, _choices, _default, _help = item
            parser_state.add_argument('--' + _name, type=_type, default=_default, choices=_choices, help=_help)

        return parser.parse_args(args)

    @staticmethod
    def settings_by_config(self, config):

        if config == '3W_COMBINED_ZIGBEE':
            self.print_if_verbose('Configuring for %s' % config)
            self.g_settings.PtaMode = self.HI_PTA_3W
            self.g_settings.CoexType = self.HI_COEX_TYPE_GENERIC
            self.g_settings.SimultaneousRxAccesses = self.HI_PTA_TRUE
            self.g_settings.PrioritySamplingTime = 10
            self.g_settings.TxRxSamplingTime = 30
            self.g_settings.GrantValidTime = 40
            self.g_settings.FemControlTime = 40
            self.g_settings.FirstSlotTime = 40
            self.g_settings.PeriodicTxRxSamplingTime = 1

        if config == '3W_NOT_COMBINED_ZIGBEE':
            self.print_if_verbose('Configuring for %s' % config)
            self.g_settings.PtaMode = self.HI_PTA_3W
            self.g_settings.CoexType = self.HI_COEX_TYPE_GENERIC
            self.g_settings.SimultaneousRxAccesses = self.HI_PTA_FALSE
            self.g_settings.PrioritySamplingTime = 10
            self.g_settings.GrantValidTime = 20
            self.g_settings.FemControlTime = 20

        if config == '3W_COMBINED_BLE':
            self.print_if_verbose('Configuring for %s' % config)
            self.g_settings.PtaMode = self.HI_PTA_3W
            self.g_settings.CoexType = self.HI_COEX_TYPE_BLE
            self.g_settings.SimultaneousRxAccesses = self.HI_PTA_TRUE
            self.g_settings.PrioritySamplingTime = 10
            self.g_settings.GrantValidTime = 72
            self.g_settings.FemControlTime = 140

        if config == '3W_NOT_COMBINED_BLE':
            self.print_if_verbose('Configuring for %s' % config)
            self.g_settings.PtaMode = self.HI_PTA_3W
            self.g_settings.CoexType = self.HI_COEX_TYPE_BLE
            self.g_settings.SimultaneousRxAccesses = self.HI_PTA_FALSE
            self.g_settings.PrioritySamplingTime = 10
            self.g_settings.GrantValidTime = 72
            self.g_settings.FemControlTime = 140

    @staticmethod
    def priority_setup(self, options):

        if options.PriorityMode == 'COEX_MAXIMIZED':
            self.g_settings.PriorityMode = self.HI_PTA_PRIORITY_COEX_MAXIMIZED
        if options.PriorityMode == 'COEX_HIGH':
            self.g_settings.PriorityMode = self.HI_PTA_PRIORITY_COEX_HIGH
        if options.PriorityMode == 'BALANCED':
            self.g_settings.PriorityMode = self.HI_PTA_PRIORITY_BALANCED
        if options.PriorityMode == 'WLAN_HIGH':
            self.g_settings.PriorityMode = self.HI_PTA_PRIORITY_WLAN_HIGH
        if options.PriorityMode == 'WLAN_MAXIMIZED':
            self.g_settings.PriorityMode = self.HI_PTA_PRIORITY_WLAN_MAXIMIZED

    @staticmethod
    def state_setup(self, options):

        if options.State == 'ON':
            self.g_settings.State = 1
            self.g_settings.State = 1
        if options.State == 'OFF':
            self.g_settings.State = 0

    @staticmethod
    def apply_options(self, options):
        # filling defaults and self.g_settings with default values
        defaults = self.parse_cmdline(self, args=['settings'])
        self.g_settings = self.parse_cmdline(self, args=['settings'])
        if options.Config is not None:
            self.settings_by_config(self, options.Config)
            # Tracing modified values after applying Config
            for k in self.g_settings.__dict__.keys():
                if '__' not in k:
                    if self.g_settings.__dict__[k] != defaults.__dict__[k]:
                        self.print_if_verbose("%-30s %8s => %8s (x%x)" %
                              (k, defaults.__dict__[k], self.g_settings.__dict__[k], int(self.g_settings.__dict__[k])))
        self.g_settings.pta_cmd = options.pta_cmd
        if options.pta_cmd == 'priority':
            self.priority_setup(self, options)
        if options.pta_cmd == 'state':
            self.state_setup(self, options)
        # Applying user options on top of current settings
        for k in options.__dict__.keys():
            if '__' not in k and k != 'Config':
                if options.__dict__[k] != defaults.__dict__[k]:
                    if self.g_settings.__dict__[k] != options.__dict__[k] and type(options.__dict__[k]) == int:
                        self.print_if_verbose("%-30s %8s -> %8s (x%s)" %
                              (k, self.g_settings.__dict__[k], options.__dict__[k], options.__dict__[k]))
                        self.g_settings.__dict__[k] = options.__dict__[k]

    def pta_bytes(self):
        header = []
        payload = list()
        nb_bytes = 4
        cmd_id = 0
        # self.print_if_verbose("PTA command: %s" % self.g_settings.pta_cmd)
        if self.g_settings.pta_cmd == 'settings':
            cmd_id = 0x002b
            for item in self.settings_parameters:
                _name, _type, _bytes, _choices, _default, _help = item
                if _name != 'Config':
                    self.print_if_verbose(str.format("%-30s %-10s " % (_name, self.g_settings.__dict__[_name])), end='')
                    if _bytes == 1:
                        payload.append(str.format(r"\x%02x" % int(self.g_settings.__dict__[_name] & 0xFF)))
                    if _bytes == 2:
                        payload.append(str.format(r"\x%02x" % int(self.g_settings.__dict__[_name] & 0x00FF)))
                        payload.append(str.format(r"\x%02x" % int(self.g_settings.__dict__[_name] & 0xFF00)))
                    self.print_if_verbose(''.join(payload[(nb_bytes-4):]))
                    nb_bytes += _bytes
        if self.g_settings.pta_cmd == 'priority':
            cmd_id = 0x002c
            for item in self.priority_parameters:
                _name, _type, _bytes, _choices, _default, _help = item
                self.print_if_verbose(str.format("%-30s %-10s " % (_name, self.g_settings.__dict__[_name])), end='')
                p = int(self.g_settings.__dict__[_name])
                payload.append(str.format(r"\x%02x" % ((p & 0x000000FF) >> 0)))
                payload.append(str.format(r"\x%02x" % ((p & 0x0000FF00) >> 8)))
                payload.append(str.format(r"\x%02x" % ((p & 0x00FF0000) >> 16)))
                payload.append(str.format(r"\x%02x" % ((p & 0xFF000000) >> 24)))
                self.print_if_verbose(''.join(payload[(nb_bytes - 4):]))
                nb_bytes += _bytes
        if self.g_settings.pta_cmd == 'state':
            cmd_id = 0x002d
            for item in self.state_parameters:
                _name, _type, _bytes, _choices, _default, _help = item
                self.print_if_verbose(str.format("%-30s %-10s " % (_name, self.g_settings.__dict__[_name])), end='')
                p = int(self.g_settings.__dict__[_name])
                payload.append(str.format(r"\x%02x" % ((p & 0x000000FF) >> 0)))
                payload.append(str.format(r"\x%02x" % ((p & 0x0000FF00) >> 8)))
                payload.append(str.format(r"\x%02x" % ((p & 0x00FF0000) >> 16)))
                payload.append(str.format(r"\x%02x" % ((p & 0xFF000000) >> 24)))
                self.print_if_verbose(''.join(payload[(nb_bytes-4):]))
                nb_bytes += _bytes
        header.append(str.format(r"\x%02x" % int(nb_bytes & 0x00FF)))
        header.append(str.format(r"\x%02x" % int(nb_bytes & 0xFF00)))
        header.append(str.format(r"\x%02x" % int(cmd_id & 0x00FF)))
        header.append(str.format(r"\x%02x" % int(cmd_id & 0xFF00)))
        data_bytes = r''.join(header + payload)
        return data_bytes


if __name__ == '__main__':
    sys.exit(WfxPtaData().data())