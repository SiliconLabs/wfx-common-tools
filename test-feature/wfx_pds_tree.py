#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""wfx_pds_tree.py
    Defines the PDS structure (Sections, Parameters, Values) for a given FW version
    This module supports the latest FW version definitions
    Parameters not known to the current FW version (the one loaded by the driver) are not processed & trigger messages

    Use case:
        pds = PdsTree(wfx_pds)
        fw_version = [retrieve FW version from HW as a x.y string]
        pds.fill_tree('2.0')      # Limit parameters to those known to FW2.0
        pds.set('NB_FRAME', 45)   # Set NB_FRAME parameter, wherever it is in the structure (names are unique by design)
        pds.get('NB_FRAME')       # Get NB_FRAME parameter
        pds.pretty()              # Print PDS tree in a nice format
        pds.print()               # Retrieve PDS tree in a 'pds_compress ready' format


"""

from copy import deepcopy
from distutils.version import StrictVersion

wfx_pds = [
  #  ITEM                            | VERSION | DEFAULT              | PATH                            | VALUES                    | DOC
    ('RF_PORT'                       ,  '2.0'  , 'RF_PORT_BOTH'       , 'RF_POWER_CFG'                  , "RF_PORT_1, RF_PORT_2, RF_PORT_BOTH(default)", "RF port affected by the RF_POWER_CFG parameters"),
    ('MAX_OUTPUT_POWER_QDBM'         ,  '2.0'  ,  80                  , 'RF_POWER_CFG'                  , "[-128, 127]", "Max Tx power value, in 1/4 of dBm. Resultant covered range in dBm: [-32; 31.75]"),
    ('FRONT_END_LOSS_CORRECTION_QDB' ,  '2.0'  ,  0                   , 'RF_POWER_CFG'                  , "[-128, 127]", "Front-end loss (loss between the chip and the antenna) in 1/4 of dB. Resultant covered range in dB: [-32; 31.75]"),
    ('CHANNEL_NUMBER'                ,  '2.0'  , '[1, 14]'            , 'RF_POWER_CFG.BACKOFF_QDB[]'    , "[1, 14]", "Backoff CHANNEL_NUMBER : channel number (an integer) or range of channel numbers (an array) to which the backoff values apply"),
    ('BACKOFF_VAL'                   ,  '2.0'  , '[0, 0, 0, 0, 0 ,0]' , 'RF_POWER_CFG.BACKOFF_QDB[]'    , "[0, 255] possible values", "BACKOFF_VAL is given in 1/4 of dB. Covered range in dB: [0; 63.75].\
                                                                                                                                      Each value sets a backoff for a group of modulation.\
                                                                                                                                      A modulation group designates a subset of modulations :\
                                                                                                                                      # MOD_GROUP_0 : B_1Mbps, B_2Mbps, B_5.5Mbps, B_11Mbps\
                                                                                                                                      # MOD_GROUP_1 : G_6Mbps, G_9Mbps, G_12Mbps, N_MCS0,  N_MCS1,\
                                                                                                                                      # MOD_GROUP_2 : G_18Mbps, G_24Mbps, N_MCS2, N_MCS3,\
                                                                                                                                      # MOD_GROUP_3 : G_36Mbps, G_48Mbps, N_MCS4, N_MCS5\
                                                                                                                                      # MOD_GROUP_4 : G_54Mbps, N_MCS6\
                                                                                                                                      # MOD_GROUP_5 : N_MCS7"),
    ('RSSI_CORRECTION'               ,  '2.2.2', 0                       , 'RF_POWER_CFG'                  , "[0, 255]"               , "Backoff CHANNEL_NUMBER : channel number (an integer) or range of channel numbers (an array) to which the backoff values apply"),
    ('RF_PORTS'                      ,  '2.0'  , 'TX1_RX1'               , 'RF_ANTENNA_SEL_DIV_CFG'        , "TX1_RX1, TX2_RX2, TX1_RX2, TX2_RX1, TX12_RX12", "Antenna selection"),
    ('TEST_CHANNEL_FREQ'             ,  '2.0'  ,  11                     , 'TEST_FEATURE_CFG'              , "[1, 14]"                , "Wi-Fi channel to use for TEST_FEATURE"),
    ('TEST_MODE'                     ,  '2.0'  , 'tx_packet'             , 'TEST_FEATURE_CFG'              , "rx, tx_packet, tx_cw"   , "TEST_FEATURE selection"),
    ('TEST_IND'                      ,  '2.0'  ,  1000                   , 'TEST_FEATURE_CFG'              , "[0, TBD(65535?]"        , "Tx: TEST_IND period in ms at which an indication message is sent. Rx: returns the measurement results (PER)"),
    ('CW_MODE'                       ,  '2.0'  , 'single'                , 'TEST_FEATURE_CFG.CFG_TX_CW'    , "single, dual"           , "TEST_FEATURE on one or 2 channels"),
    ('FREQ1'                         ,  '2.0'  ,  0                      , 'TEST_FEATURE_CFG.CFG_TX_CW'    , "[-31, 31]"              , "Channel 1 frequency offset in 312.5 kHz steps. Covered range: [-9687.5 to 9687.5] kHz"),
    ('FREQ2'                         ,  '2.0'  ,  0                      , 'TEST_FEATURE_CFG.CFG_TX_CW'    , "[-31, 31]"              , "Channel 2 frequency offset in 312.5 kHz steps. Covered range: [-9687.5 to 9687.5] kHz"),
    ('MAX_OUTPUT_POWER'              ,  '2.0'  ,  68                     , 'TEST_FEATURE_CFG.CFG_TX_CW'    , "TBD"                    , "Max Tx power value in quarters of dBm"),
    ('FRAME_SIZE_BYTE'               ,  '2.0'  ,  3000                   , 'TEST_FEATURE_CFG.CFG_TX_PACKET', "[25, 4091]"             , "frame size in byte (without CRC)"),
    ('IFS_US'                        ,  '2.0'  ,  0                      , 'TEST_FEATURE_CFG.CFG_TX_PACKET', "[0, 255]"               , "interframe spacing in us"),
    ('HT_PARAM'                      ,  '2.0'  , 'MM'                    , 'TEST_FEATURE_CFG.CFG_TX_PACKET', "MM, GF"                 , "HT format (MM: mixed mode or GF: greenfield)"),
    ('RATE'                          ,  '2.0'  , 'N_MCS7'                , 'TEST_FEATURE_CFG.CFG_TX_PACKET', "B_1Mbps, B_2Mbps, B_5_5Mbps, B_11Mbps, G_6Mbps, G_9Mbps, G_12Mbps, G_18Mbps, G_24Mbps, G_36Mbps, G_48Mbps, G_54Mbps, N_MCS0, N_MCS1, N_MCS2, N_MCS3, N_MCS4, N_MCS5, N_MCS6, N_MCS7",
                                                                                                                                     "rate selection."),
    ('NB_FRAME'                      ,  '2.0'  ,  0                      , 'TEST_FEATURE_CFG.CFG_TX_PACKET', "[0, 65535]"             , "number of frames to send before stopping. 0 means continuous"),
    ('REG_MODE'                      ,  '2.2'  , 'CERTIFIED_Unrestricted', 'TEST_FEATURE_CFG.CFG_TX_PACKET', "CERTIFIED_All, CERTIFIED_FCC, CERTIFIED_ETSI, CERTIFIED_JAPAN, CERTIFIED_Unrestricted",
                                                                                                                                        "Regulatory mode"),
    ('RX'                            ,  '2.0'  , ''                      , 'TEST_FEATURE_CFG'              , "TBD (default empty)"    , "additional configuration for rx mode"),
    ('CTUNE_FIX'                     ,  '2.0'  , '3'                     , 'HF_CLK.XTAL_CFG'               , "[0, 3]"                 , "set a high value capacitance on both XTAL_I and XTAL_O"),
    ('CTUNE_XI'                      ,  '2.0'  , '140'                   , 'HF_CLK.XTAL_CFG'               , "[0, 255]"               , "fine tune the capacitor on pin XTAL_I"),
    ('CTUNE_XO'                      ,  '2.0'  , '140'                   , 'HF_CLK.XTAL_CFG'               , "[0, 255]"               , "fine tune the capacitor on pin XTAL_O"),
]

pds_order = []
pds_warning = ""


class PdsTree(dict):
    """
        Returns a ```PdsTree``` object with the given name
    """
    pds_keys = []

    def __init__(self):
        dict.__init__(self)
        self.res = ""
        self.pds_structure = wfx_pds
        self.max_fw_version = "2.2.2"
        self.current_fw_version = self.max_fw_version

    def set_current_fw_version(self, version):
        self.current_fw_version = version

    def print(self):
        print(str(self).replace('\'', ''))

    def fill_tree(self, version, trace=0):
        self.set_current_fw_version(version)
        msg = ""
        for item in self.pds_structure:
            key, version, default, path, values, doc = item
            if StrictVersion(version) > StrictVersion(self.current_fw_version):
                msg += "  Info: '" + key + "' cannot be supported with FW" + self.current_fw_version + \
                       ", it has been added in FW" + version + " (skipped)\n"
                print(msg)
            else:
                self._add_node(str(path), str(key), str(default))
                if trace:
                    self.pretty()
                    print("----------------")
                levels = str(path).split('.')
                for level in levels:
                    if level not in pds_order:
                        pds_order.append(level)
                if key not in self.pds_keys:
                    pds_order.append(key)
                    self.pds_keys.append(key)
        if msg:
            add_pds_warning(msg)
            print("fill_tree has messages: \n" + msg)
        return msg

    def add_tmp_param(self, version, path, key, default, trace=0):
        msg = ""
        if StrictVersion(version) > StrictVersion(self.current_fw_version):
            msg += "  Info: '" + key + "' cannot be supported with FW" + self.current_fw_version + \
                   ", it has been added in FW" + version + " (skipped)\n"
            add_pds_warning(msg)
            print(msg)
        else:
            self._add_node(str(path), str(key), str(default))
            levels = str(path).split('.')
            for level in levels:
                if level not in pds_order:
                    pds_order.append(level)
            if key not in self.pds_keys:
                pds_order.append(key)
                self.pds_keys.append(key)
            self.pds_structure.append((str(key), str(version), str(default), str(path), "unknown range",
                                       "Temporary parameter, lost after closing"))
            if trace:
                self.pretty()
                print("---- tmp -------")
            return self.pretty()

    def sub_tree(self, keys_to_keep=None):
        pds_subtree = deepcopy(self)
        if len(keys_to_keep) == 0:
            return self
        sections_to_keep = []
        sections_to_delete = []
        for item in self.pds_structure:
            key, version, default, path, values, doc = item
            section_root = path.split('.')[0]
            if key in keys_to_keep and section_root not in keys_to_keep:
                if StrictVersion(version) > StrictVersion(self.current_fw_version):
                    msg = "  Info: '" + key + "' cannot be supported with FW" + self.current_fw_version + \
                           ", it has been added in FW" + version + " (skipped)\n"
                    print(msg)
                    add_pds_warning(msg)
                else:
                    sections_to_keep.append(section_root)
        for key in pds_subtree.keys():
            if key not in sections_to_keep:
                sections_to_delete.append(key)
        for key in sections_to_delete:
            del pds_subtree[key]
        return pds_subtree

    def pretty(self, indent=0):
        result = ""
        items_to_print = []
        for key, v in self.items():
            items_to_print.append(key)
        for section in pds_order:
            for k, v in self.items():
                if k == section:
                    if isinstance(v, dict):
                        if '[]' in k:
                            result += '\t' * indent + k.replace('[', '').replace(']', '') + " : [ {\n"
                        else:
                            result += '\t' * indent + str(k) + " : {\n"
                        result += PdsTree.pretty(v, indent + 1)
                        if '[]' in k:
                            result += '\t' * indent + "} ],\n"
                        else:
                            result += '\t' * indent + "},\n"
                    else:
                        if str(v) == "":
                            result += '\t' * indent + str(k) + ' :' + ' ' * max(1, 32 - len(k)) + '{ }' + ",\n"
                        else:
                            result += '\t' * indent + str(k) + ' :' + ' ' * max(1, 32 - len(k)) + str(v) + ",\n"
        return result

    def set(self, key, value):
        if key not in self.pds_keys:
            msg = "key '" + key + "' not in pds_structure. Possible keys are " + str(self.pds_keys)
            add_pds_warning(msg)
            return msg
        for item in self.pds_structure:
            k, version, default, path, values, doc = item
            if k == key:
                if StrictVersion(version) > StrictVersion(self.current_fw_version):
                    return "Warning: '" + key + "' cannot be supported with FW" + self.current_fw_version + \
                           ", it has been added in FW" + version + " (skipped)\n"
                return self._set_node_value(path, key, value)
        return "Error setting " + key

    def get(self, key):
        if key not in self.pds_keys:
            msg = "key '" + key + "' not in pds_structure. Possible keys are " + str(self.pds_keys)
            add_pds_warning(msg)
            return msg
        for item in self.pds_structure:
            k, version, default, path, values, doc = item
            if k == key:
                if StrictVersion(version) > StrictVersion(self.current_fw_version):
                    return "Warning: '" + key + "' cannot be supported with FW" + self.current_fw_version + \
                           ", it has been added in FW" + version + " (skipped)\n"
                return self._get_node_value(path, key)
        return "Error checking " + key

    def _add_node(self, path, key, default):
        levels = str(path).split('.')
        next_path = ".".join(levels[1:])
        if levels[0] not in self:
            new_node = self[levels[0]] = dict()
        else:
            new_node = self[levels[0]]
        if len(next_path) > 0:
            PdsTree._add_node(new_node, str(next_path), str(key), str(default))
        else:
            new_node[key] = default
            return

    def _set_node_value(self, path, key, value):
        levels = str(path).split('.')
        next_path = ".".join(levels[1:])
        current_node = self[levels[0]]
        if len(next_path) > 0:
            return PdsTree._set_node_value(current_node, next_path, key, value)
        else:
            current_node[key] = value
            return str(value)

    def _get_node_value(self, path, key):
        levels = str(path).split('.')
        next_path = ".".join(levels[1:])
        current_node = self[levels[0]]
        if len(next_path) > 0:
            return PdsTree._get_node_value(current_node, next_path, key)
        else:
            return str(current_node[key])


def add_pds_warning(msg):
    global pds_warning
    pds_warning += msg


def check_pds_warning(msg=""):
    global pds_warning
    if pds_warning == "":
        return msg.strip()
    else:
        ret = pds_warning
        pds_warning = ""
        return ret.strip()


pds_compatibility_text = "\
#ifndef   MAX_TX_POWER_CFG\n\
    #define MAX_TX_POWER_CFG h\n\
#endif /* MAX_TX_POWER_CFG */\n\n\
#ifndef   TEST_FEATURE_CFG\n\
    #define TEST_FEATURE_CFG i\n\
    #define RF_ANTENNA_SEL_DIV_CFG j\n\
    #define TEST_CHANNEL_FREQ a\n\
#endif /* TEST_FEATURE_CFG */\n\n\
#ifndef   RF_POWER_CFG\n\
    #define RF_POWER_CFG h\n\
#endif /* RF_POWER_CFG */\n\
#ifndef   CERTIFIED_Unrestricted\n\
    #define CERTIFIED_All          0\n\
    #define CERTIFIED_FCC          1\n\
    #define CERTIFIED_ETSI         2\n\
    #define CERTIFIED_JAPAN        3\n\
    #define CERTIFIED_Unrestricted 4\n\
#endif /* CERTIFIED_Unrestricted */\n\
\n\n\
"


if __name__ == '__main__':
    print("\n# pds = PdsTree(pds_structure)")
    pds = PdsTree()
    print("\n# pds.fill_tree(\"2.0\")")
    pds.fill_tree("2.0")
    print("\n# pds_order")
    print(pds_order)
    print("\n# pds.pretty():")
    print(pds.pretty())
    print("\n# pds.current_fw_version     :", pds.current_fw_version)
    print("\n# pds.max_fw_version         :", pds.max_fw_version)
    print("\n# pds.set(\"FOO\", 45)       : " + str(pds.set("FOO", 22)))
    print("\n# pds.get(\"NB_FRAME\")      : " + str(pds.get("NB_FRAME")))
    print("\n# pds.set(\"NB_FRAME\" , 45) : " + str(pds.set("NB_FRAME", 45)))
    print("\n# pds.get(\"NB_FRAME\")      : " + str(pds.get("NB_FRAME")))
    print("\n# pds.set(\"REG_MODE\" , 12) : " + str(pds.set("REG_MODE", 12)))
    print("\n# pds.get(\"REG_MODE\")      : " + str(pds.get("REG_MODE")))
    print("\n# pds.get(\"BAR\")           : " + str(pds.get("BAR")))
    print("\n# pds.print():")
    pds.print()
    print("\n# pds.pretty():")
    print(pds.pretty())

    print("\n# pds.set(\"TEST_CHANNEL_FREQ\" , 5) : " + str(pds.set("TEST_CHANNEL_FREQ", 5)))
    print("\n# pds.get(\"TEST_CHANNEL_FREQ\")     : " + str(pds.get("TEST_CHANNEL_FREQ")))

    sub = pds.sub_tree(["RF_PORT"])
    print("\n# sub.pretty():")
    print(sub.pretty())
    print(pds.sub_tree(["RF_PORT"]).pretty())

    sub = pds.sub_tree(["NB_FRAME", "RF_PORTS"])
    print("\n# sub.pretty():")
    print(sub.pretty())

    print("\n# pds.pretty():")
    print(pds.pretty())
