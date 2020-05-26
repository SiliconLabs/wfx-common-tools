#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""wfx_test_dut.py
"""

from wfx_test_target import *
from job import *


class WfxTestDut(WfxTestTarget):
    tools_version = '1.0.0'
    debug_color = "\033[95m"
    error_color = "\033[91m"
    write_color = "\033[94m"
    read_color  = "\033[92m"
    set_color   = "\033[93m"
    reset_color = "\033[0;0m"

    def __init__(self, nickname, **kwargs):
        critical_message = ''
        super().__init__(nickname, **kwargs)
        self.rx_res = None
        self.rx_avg = None
        self.rx_cnt = None
        self.rx_modulations = [
            '1M', '2M', '5.5M', '11M',
            '6M', '9M', '12M', '18M', '24M', '36M', '48M', '54M',
            'MCS0', 'MCS1', 'MCS2', 'MCS3', 'MCS4', 'MCS5', 'MCS6', 'MCS7']
        self.rx_items = ['frames', 'errors', 'PER', 'RSSI', 'SNR', 'CFO']
        self.rx_averaging = ['RSSI', 'SNR', 'CFO']
        self.rx_globals = ['frames', 'errors', 'PER', 'Throughput', 'deltaT', 'loops', 'start_us', 'last_us']
        self.rx_job = None
        self.__rx_clear()
        agent_reply = self.run('wfx_test_agent read_agent_version')
        print(self.link.conn + ' agent_reply: ' + str(agent_reply))
        if agent_reply == '' or 'command not found' in agent_reply:
            agent_error = 'No \'wfx_test_agent\' on ' + self.link.conn + \
                          '. Communication OK, but we miss the agent!!\n reply: ' + str(agent_reply)
            raise Exception("%s: %s" % (self.nickname, agent_error))

        for option in self.useful_options:
            agent_result = self.run('wfx_test_agent ' + option)
            print('wfx_test_agent ' + option + '  agent_result ' + agent_result)
            if 'unknown' in self.run('wfx_test_agent ' + option):
                agent_error = 'No \'' + option + '\' option in the ' + self.link.conn + \
                              ' wfx_test_agent. We can talk to the agent,' + \
                              ' but it does not reply to \'wfx_test_agent ' + option + '\'!!'
                print("%s: MISSING USEFUL   OPTION: %s" % (self.nickname, agent_error))
        if self.required_options:
            print(str(len(self.required_options)) + ' required_options: ' + str(self.required_options))
            for option in self.required_options:
                agent_result = self.run('wfx_test_agent ' + option)
                print('wfx_test_agent ' + option + '  agent_result ' + agent_result)
                if 'unknown' in agent_result or agent_result == '':
                    agent_error = 'No \'' + option + '\' option in the ' + self.link.conn + \
                                  ' wfx_test_agent. We can talk to the agent,' + \
                                  ' but it does not reply to \'wfx_test_agent ' + option + '\'!!'
                    print("%s: MISSING CRITICAL OPTION: %s" % (self.nickname, agent_error))
                    critical_message = critical_message + agent_error + '\n   '

        if critical_message != '':
            raise Exception("%s:\n   %s" % (self.nickname, critical_message))

    @staticmethod
    def __errors_from_per(nb, per):
        return int((int(nb) * int(per) / 10000) + 0.5)

    @staticmethod
    def __per(nb=0, err=0):
        if nb == 0:
            return str.format("%.3e" % 1)
        else:
            return str.format("%.3e" % (int(err) / int(nb)))

    @staticmethod
    def __average(num, count):
        div = 1 if count == 0 else count
        offset = 0.5 if num >= 0 else -0.5
        return int((num + offset) / div)

    def channel(self, ch=None):
        if ch is None:
            return self.wfx_get_list({'TEST_CHANNEL_FREQ'})
        else:
            return self.wfx_set_dict({'TEST_CHANNEL_FREQ': ch}, send_data=0)

    def c_tune_xi_xo(self, xi=None, xo=None):
        if xi is None:
            return self.wfx_get_list({"CTUNE_XI"})  + " " + self.wfx_get_list({"CTUNE_XO"})
        else:
            if xo is None:
                xo = xi
            return self.wfx_set_dict({"CTUNE_XI": str(xi), "CTUNE_XO": str(xo)})

    def c_tune_fix(self, fix=None):
        if fix is None:
            return self.wfx_get_list({"CTUNE_FIX"})
        else:
            return self.wfx_set_dict({"CTUNE_FIX": str(fix)})

    def fem_pa_used(self, yes_no=None):
        if yes_no is None:
            return self.wfx_get_list({"PA_USED"}, mode='quiet')
        return self.wfx_set_dict({"PA_USED": yes_no}, send_data=1)

    def fem_pa_max_gain(self, gain_db=None):
        if gain_db is None:
            return self.wfx_get_list({"MAX_GAIN"}, mode='quiet')
        return self.wfx_set_dict({"MAX_GAIN": int(gain_db*4)}, send_data=1)

    def fem_pa_table(self, vdet_vs_pout=None):
        def list_from_text(txt):
            (clean_text, length) = re.subn('[\[\]\s]', '', txt)
            return clean_text.split(',')
        def text_from_list(v_list):
            return "[" + ','.join(v_list) + "]"
        if vdet_vs_pout is 'text':
            vdet_text = self.wfx_get_list({"VDET_VAL"}, mode='quiet')
            pout_text = self.wfx_get_list({"POUT_VAL"}, mode='quiet')
            return vdet_text + "\n" + pout_text
        if vdet_vs_pout is None:
            vdet_list = list_from_text(self.wfx_get_list({"VDET_VAL"}, mode='quiet'))
            pout_list = list_from_text(self.wfx_get_list({"POUT_VAL"}, mode='quiet'))
            length = len(vdet_list)
            vdet_vs_pout = []
            for i in range(length):
                vdet_vs_pout.append((vdet_list[i], pout_list[i]))
            return vdet_vs_pout
        if vdet_vs_pout is 'open_loop':
            return self.wfx_set_dict({"NB_OF_POINTS": 0}, send_data=1)
        if vdet_vs_pout is 'closed_loop':
            pout = self.wfx_get_list("POUT_VAL", mode='silent')
            print(f"pout {pout}")
            nb_points = len(self.wfx_get_list("POUT_VAL", mode='silent').split(','))
            return self.wfx_set_dict({"NB_OF_POINTS": nb_points}, send_data=1)
        nb_points = len(vdet_vs_pout)
        vdet_list = []
        pout_list = []
        for point in vdet_vs_pout:
            vdet_list.append(str(point[0]))
            pout_list.append(str(point[1]))
        nb_res   = self.wfx_set_dict({"NB_OF_POINTS": nb_points}, send_data=0)
        vdet_res = self.wfx_set_dict({"VDET_VAL": text_from_list(vdet_list)}, send_data=0)
        pout_res = self.wfx_set_dict({"POUT_VAL": text_from_list(pout_list)}, send_data=0)
        return vdet_res + "\n" + pout_res

    def fem_read_tx_info(self, match=None):
        res = self.run('wfx_test_agent read_tx_info').strip()
        if match is None:
            return res
        re_match = re.compile(match)
        for line in res.split('\n'):
            matching = re_match.match(line)
            if matching is not None:
                if self.trace:
                    print(f"matching {match}: {matching}")
                    print(f"matching groups: {matching.groups()}")
                return str(matching.group(1)).strip()
        return ''

    def fem_read_digital_gain(self):
        return self.fem_read_tx_info(match='Tx gain digital:(.*)')

    def fem_read_pa_gain(self):
        return self.fem_read_tx_info(match='Tx gain PA:(.*)')

    def fem_read_target_pout(self):
        return self.fem_read_tx_info(match='Target Pout:(.*) dBm')

    def fem_read_fem_pout(self):
        return self.fem_read_tx_info(match='FEM Pout:(.*) dBm')

    def fem_read_vpdet(self):
        return self.fem_read_tx_info(match='Vpdet:(.*) mV')

    def fem_read_measure_index(self):
        re_match = re.compile('Measure index:(.*)')
        match = re_match.match(self.fem_read_tx_info())
        if match is not None:
            return int(match.group(1))
        else:
            return 0

    def test_ind_period(self, period=None):
        if period is None:
            return self.wfx_get_list({'TEST_IND'})
        else:
            return self.wfx_set_dict({'TEST_IND': period}, send_data=0)

    def tone_freq(self, offset=None):
        if offset is None:
            return self.wfx_get_list({"FREQ1"}, mode='quiet')
        return self.wfx_set_dict({"FREQ1": offset}, send_data=1)

    def tone_power(self, dbm=None):
        if dbm is None:
            power = int(self.wfx_get_list({"MAX_OUTPUT_POWER"}, mode='quiet'))
            return "MAX_OUTPUT_POWER  " + str(power) + "  " + "     tone_power  " + str(power / 4.0) + " dBm"
        else:
            return self.wfx_set_dict({"MAX_OUTPUT_POWER": int(4 * dbm)}, send_data=1)

    def tone_start(self, offset=None):
        if offset is None:
            offset = self.wfx_get_list({"FREQ1"}, mode='quiet')
        # CW Mode: generate CW @ offset*312.5Khz
        return self.wfx_set_dict({"TEST_MODE": "tx_cw", "CW_MODE": "single", "FREQ1": offset}, send_data=1)

    def tone_stop(self):
        return self.tx_stop()

    def tx_power(self, dbm=None):
        if dbm is None:
            power = int(self.wfx_get_list("MAX_OUTPUT_POWER_QDBM", mode='quiet'))
            return "MAX_OUTPUT_POWER_QDBM" + "  " + str(power) + \
                   "     tx_power  " + str(power / 4.0) + " dBm"
        else:
            return self.wfx_set_dict({"MAX_OUTPUT_POWER_QDBM": int(4 * dbm),
                                      "TEST_MODE": "tx_packet",
                                      "NB_FRAME": 0}, send_data=1)

    def tx_backoff(self, mode_802_11=None, backoff_level=0):
        if backoff_level == "":
            backoff_level = 0
        if mode_802_11 == "RSVD":
            return
        if mode_802_11 is None:
            backoff_val = self.wfx_get_list({"BACKOFF_VAL"}, mode='quiet')
            (backoff_data, nb) = re.subn('[\[\]\s]', '', backoff_val)
            backoff_max = max(backoff_data.split(','))
            backoff_dbm = str(int(backoff_max) / 4.0)
            return "BACKOFF_VAL  " + backoff_max + "     tx_backoff  " + backoff_dbm + " dB"
        else:
            backoff_indexes_by_bitrate = {
                0: ['1Mbps', '2Mbps', '5_5Mbps', '11Mbps'],
                1: ['6Mbps', '9Mbps', '12Mbps'],
                2: ['18Mbps', '24Mbps'],
                3: ['36Mbps', '48Mbps'],
                4: ['54Mbps']
            }
            backoff_indexes_by_modulation = {
                0: ['DSSS', 'CCK'],
                1: ['MCS0', 'MCS1'],
                2: ['MCS2', 'MCS3'],
                3: ['MCS4', 'MCS5'],
                4: ['MCS6'],
                5: ['MCS7']
            }
            index = -1
            if 'Mbps' in mode_802_11:
                input_bitrate = '_'.join(mode_802_11.split('_')[1:])
                for k in backoff_indexes_by_bitrate.keys():
                    for bitrate in backoff_indexes_by_bitrate[k]:
                        if bitrate == input_bitrate:
                            index = k
            else:
                for k in backoff_indexes_by_modulation.keys():
                    modulations = backoff_indexes_by_modulation[k]
                    for modulation in modulations:
                        if modulation in mode_802_11:
                            index = k
            if index == -1:
                warning_msg = "tx_backoff: Unknown 802.11 mode " + str(mode_802_11)
                add_pds_warning(warning_msg)
                return warning_msg
            value = [0, 0, 0, 0, 0, 0]
            value[index] = int(4 * backoff_level)
            self.wfx_set_dict({"BACKOFF_VAL": str(value), "TEST_MODE": "tx_packet", "NB_FRAME": 0}, send_data=1)

    def regulatory_mode(self, reg_mode=None):
        if reg_mode is None:
            return self.wfx_get_list("REG_MODE", mode='quiet')
        else:
            possible_reg_modes = ["All", "FCC", "ETSI", "JAPAN", "Unrestricted"]
            old_namings = {"JP": "JAPAN", "min": "All"}
            for n in old_namings.keys():
                if n in reg_mode:
                    reg_mode = old_namings[n]
            for m in possible_reg_modes:
                if m in reg_mode:
                    return self.wfx_set_dict({"REG_MODE": "CERTIFIED_" + m}, send_data=0)
            return "Unknown '" + reg_mode + " ' regulatory_mode. Use " + str(possible_reg_modes[0:5])

    def tx_framing(self, packet_length_bytes=None, ifs_us=100):
        if packet_length_bytes is None:
            return self.wfx_get_list({"FRAME_SIZE_BYTE", "IFS_US"})
        else:
            return self.wfx_set_dict({"FRAME_SIZE_BYTE": packet_length_bytes, "IFS_US": ifs_us}, send_data=0)

    def tx_mode(self, mode_802_11=None):
        if mode_802_11 is None:
            return self.wfx_get_list({"HT_PARAM", "RATE"})
        else:
            res = re.findall("([^_]*)_(.*)", mode_802_11)
            mode = res[0][0]
            suffix = res[0][1].replace('Mbps', '')
            ht_param = ""
            rate = ""
            ht_param_modes = {
                'MM': ['B', 'DSSS', 'CCK', 'G', 'LEG', 'MM'],
                'GF': ['GF'],
            }
            rate_prefix_modes = {
                'B': ['B', 'DSSS', 'CCK'],
                'G': ['G', 'LEG'],
                'N': ['MM', 'GF'],
            }
            for k in ht_param_modes.keys():
                for param_mode in ht_param_modes[k]:
                    if param_mode == mode:
                        ht_param = k
            for k in rate_prefix_modes.keys():
                for rate_prefix in rate_prefix_modes[k]:
                    if rate_prefix == mode:
                        rate = k + '_' + suffix
            if 'MCS' not in rate:
                rate += 'Mbps'
            if ht_param == "":
                warning_msg = "tx_mode: Unknown 802.11 mode " + str(mode_802_11)
                add_pds_warning(warning_msg)
                return warning_msg
            return self.wfx_set_dict({"HT_PARAM": ht_param, "RATE": rate}, send_data=0)

    def tx_rx_select(self, tx_ant=None, rx_ant=None):
        if tx_ant is None:
            return self.wfx_get_list({"RF_PORTS"})
        else:
            return self.wfx_set_dict({"RF_PORTS": "TX" + str(tx_ant) + "_RX" + str(rx_ant)})

    def tx_start(self, nb_frames=None):
        if nb_frames is None:
            return self.wfx_get_list({"TEST_MODE", "NB_FRAME"})
        else:
            if str(nb_frames) == "continuous":
                nb_frames = 0
            return self.wfx_set_dict({"TEST_MODE": "tx_packet", "NB_FRAME": nb_frames}, send_data=1)

    def tx_stop(self):
        res = self.wfx_set_dict({"TEST_MODE": "tx_packet", "NB_FRAME": 100}, send_data=1)
        return res

    def rx_start(self):
        res = self.wfx_set_dict({"TEST_MODE": "rx"}, send_data=1)
        return res

    def rx_stop(self):
        if self.rx_job is not None:
            self.rx_job.stop()
        return self.tx_stop()

    def read_rx_stats(self):
        return self.run('wfx_test_agent read_rx_stats').strip()

    def rx_logs(self, mode=None):
        res = []
        if mode is None:
            for mode in (['global'] + self.rx_modulations):
                res.append(str.format("mode %7s  %s\n" % (mode, self.rx_logs(mode))))
            return ''.join(res).strip()
        mode = 'global' if mode not in self.rx_modulations else mode
        keys = self.rx_globals if mode == 'global' else self.rx_items
        for key in keys:
            res.append(str.format("%s %5s  " % (key, str(self.rx_res[mode][key]))))
        return ''.join(res).rstrip()

    def rx_receive(self, mode='global', frames=1000, timeout_s=0, sleep_ms=None):
        start = time.time()
        self.__rx_clear()
        nb_pkt = nb_same_timestamp = 0
        test_ind = int(self.test_ind_period().split()[1])
        if mode == 'endless':
            self.rx_stop()
            if self.rx_job is not None:
                self.rx_job.stop()
            self.rx_job = Job(test_ind, self.__rx_stats)
            self.rx_start()
            # Waiting for 110% of TEST_IND to read the first stats.
            #  2 goals:
            #   . Making sure we don't attempt to read the data while it's written
            #   . Making sure the first read corresponds to our test conditions
            loop_time = test_ind
            time.sleep((loop_time * 1.1) / 1000)
            self.rx_job.start()
            return "Endless rx loop started with a period of " + str(loop_time) + " ms. Use " + \
                   "'rx_logs()' to monitor Rx, " + \
                   "'rx_kill()' to stop Rx monitoring, " + \
                   "'rx_stop()' to stop Rx entirely"
        mode = 'global' if mode not in self.rx_modulations else mode
        time.sleep((test_ind * 1.1) / 1000)
        origin = time.time()
        if sleep_ms is None:
            sleep_ms = test_ind
        while nb_pkt < frames:
            before = time.time()
            timestamp_changed = self.__rx_stats()
            elapsed = int(time.time() - start)
            if timestamp_changed != 0:
                nb_same_timestamp = 0
                print(str.format('%s >>> rx_receive:   mode %s %s   (%5.2f s)' %
                                 (time_stamp(time.time()), mode, self.rx_logs(mode), elapsed)))
                nb_pkt = self.rx_res[mode]['frames']
            else:
                nb_same_timestamp += 1
                if nb_same_timestamp > 3:
                    msg = ' Error: Rx stats timestamp not changing. Rx not running!'
                    add_pds_warning(msg)
                    print('\n' + self.error_color + msg + self.reset_color + '\n')
                    break
            if elapsed > timeout_s > 0:
                msg = str.format(' Warning: Rx stats timeout after %5.2f seconds!' % elapsed)
                add_pds_warning(msg)
                print('\n', msg, '\n')
                break
            time_from_origin = before - origin
            loops = int((time_from_origin*1000/sleep_ms) + 0.5)
            next_loop = origin + ((loops+1)*sleep_ms/1000)
            after = time.time()
            sleep_this_time = int((next_loop - after)*1000)
            if sleep_this_time < 0:
                sleep_this_time = 0
            time.sleep(sleep_this_time/1000)
        return self.rx_logs(mode)

    def read_agent_version(self):
        return self.run('wfx_test_agent read_agent_version').strip()

    def read_driver_version(self):
        return self.run('wfx_test_agent read_driver_version').strip()

    def read_fw_version(self):
        return self.run('wfx_test_agent read_fw_version').strip()

    def test_conditions(self):
        agt = self.read_agent_version()
        if 'ERROR' in agt or agt == '':
            agt = "unknown"
        fw = self.read_fw_version()
        if 'ERROR' in fw or fw == '':
            fw = "unknown"
        drv = self.read_driver_version()
        if 'ERROR' in drv or drv == '':
            drv = "unknown"
        return str.format("Test conditions: DUT %s / Driver %s / FW %s / Tools %s / Agent %s / %s" %
                          (self.nickname, drv, fw, WfxTestDut.tools_version, agt, self.link.conn))

    def __rx_clear(self):
        self.rx_res = {}
        self.rx_avg = {}
        self.rx_cnt = {}
        for mode in self.rx_modulations:
            dict_items = {}
            for item in self.rx_items:
                dict_items[item] = self.__per() if item == 'PER' else 0
            self.rx_res[mode] = dict_items
            cnt_items = {}
            avg_items = {}
            for item in self.rx_averaging:
                avg_items[item] = 0
                cnt_items[item] = 0
            self.rx_avg[mode] = avg_items
            self.rx_cnt[mode] = cnt_items
        for mode in ['global']:
            dict_items = {}
            for item in self.rx_globals:
                dict_items[item] = self.__per() if item == 'PER' else 0
            self.rx_res[mode] = dict_items

    def __rx_stats(self):
        re_fr_per_th = re.compile('Num. of frames: (.*), PER \(x10e4\): (.*), Throughput: (.*)Kbps/s*')
        re_timestamp = re.compile('Timestamp: (.*)us')
        re_modulation = re.compile('\s*(\d+\w|\w+\d)\s*([-]*\d*)\s*([-]*\d*)\s*([-]*\d*)\s*([-]*\d*)\s*([-]*\d*)')
        lines = self.read_rx_stats()
        return_val = 0
        for line in lines.split('\n'):
            stamp = re_timestamp.match(line)
            if stamp is not None:
                timestamp = int(stamp.group(1))
                if timestamp == 0:
                    break
                if timestamp == self.rx_res['global']['last_us']:
                    break
                else:
                    return_val = 1
                self.rx_res['global']['last_us'] = timestamp
                if self.rx_res['global']['loops'] == 0:
                    self.rx_res['global']['start_us'] = (timestamp - 1000000) % pow(2, 31)
                self.rx_res['global']['deltaT'] = (timestamp - self.rx_res['global']['start_us']) % pow(2, 31)
                self.rx_res['global']['loops'] += 1
            cumulated = re_fr_per_th.match(line)
            if cumulated is not None and int(cumulated.group(1)) > 0:
                self.rx_res['global']['frames'] += int(cumulated.group(1))
                self.rx_res['global']['errors'] += self.__errors_from_per(cumulated.group(1), cumulated.group(2))
                self.rx_res['global']['PER'] = self.__per(self.rx_res['global']['frames'],
                                                          self.rx_res['global']['errors'])
                self.rx_res['global']['Throughput'] = int(cumulated.group(3))
            modline = re_modulation.match(line)
            if modline is not None and int(modline.group(2)) > 0:
                modulation = modline.group(1)
                self.rx_res[modulation]['frames'] += int(modline.group(2))
                self.rx_res[modulation]['errors'] += self.__errors_from_per(modline.group(2), modline.group(3))
                self.rx_res[modulation]['PER'] = self.__per(self.rx_res[modulation]['frames'],
                                                            self.rx_res[modulation]['errors'])
                index = 4
                for item in self.rx_averaging:
                    self.rx_cnt[modulation][item] += 1
                    self.rx_avg[modulation][item] += int(modline.group(index))
                    self.rx_res[modulation][item] = self.__average(self.rx_avg[modulation][item],
                                                                   self.rx_cnt[modulation][item])
                    index += 1
        return return_val


if __name__ == '__main__':

    #print(uarts())
    # Select one of the following lines to connect
    #dut = WfxTestDut('Local')
    #dut = WfxTestDut('Pi_ssh', host='10.5.124.186', user='pi', port=22, password='default_password')
    #dut = WfxTestDut('Pi_uart',   port='COM19', baudrate=115200, bytesize=8, parity='N', stopbits=1, user='pi', password='default_password')
    dut = WfxTestDut('iMX6_uart', port='COM26', baudrate=115200, bytesize=8, parity='N', stopbits=1, user='root', password='')
    #dut = WfxTestDut('RTOS_uart', port='COM21', baudrate=115200, bytesize=8, parity='N', stopbits=1)

    # enable traces if needed
    dut.link.trace = False
    dut.link.debug = False
    dut.trace = True

    if 'GNU/Linux' in dut.run('uname -a'):
        # for linux: avoid dmesg forwarding to console
        print(dut.run('dmesg -D'))

    driver_version = dut.run('wfx_test_agent read_driver_version').strip()
    print("driver_version '" + driver_version + "'")
    dut.run('wfx_driver_reload -C')
    print(dut.run('dmesg | tail'))

    print(check_pds_warning())
    print(dut.test_data.pretty())

    # Retrieving DUT info via the agent
    print(dut.test_conditions())
    dut.run('wfx_test_agent log_message "' + dut.test_conditions() + '"')

    # Tx (modulated) test
    dut.run('wfx_test_agent log_message "Tx (modulated) test"')
    dut.channel(7)
    dut.tx_rx_select(2, 2)
    dut.tx_power(11.25)
    dut.tx_start('continuous')
    dut.tx_stop()

    # Rx test (endless)
    dut.run('wfx_test_agent log_message "Rx test (endless)"')
    dut.trace = False
    print(dut.rx_receive('endless'))
    for i in range(10):
        time.sleep(1200 / 1000)
        print(dut.rx_logs('global'))
    dut.rx_stop()
    print(dut.rx_logs())

    # Rx test (waiting for set number of frames)
    dut.run('wfx_test_agent log_message "Rx test (waiting for set number of frames)"')
    dut.rx_receive('global')
    dut.rx_stop()
    print(dut.rx_logs())

    # Tone test
    dut.run('wfx_test_agent log_message "Tone test"')
    dut.tone_power(16)
    dut.tone_freq(0)
    dut.run('wfx_test_agent log_message "tone_start"')
    dut.tone_start()
    time.sleep(1)
    dut.run('wfx_test_agent log_message "tone_stop"')
    dut.tone_stop()
