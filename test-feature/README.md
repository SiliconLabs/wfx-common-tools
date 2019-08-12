# WFX Test
*wfx_test_dut* is a python3 module allowing RF testing.

**wfx_test_dut** *is an evolution of the initial test-feature scripts which were present under
 https://github.com/SiliconLabs/wfx-linux-tools/tree/master/test-feature, 
 with the added capability to be ran from a test server with either SSH or UART access to the DUT*

The architecture is now a Test Server/DUT configuration:
* The **Test server** can run **wfx_test_dut** on any python3-capable platform with network and/or UART communication
 capabilities
	* One possible python3-capable platform is the Raspberry PI. In this case, both the Test Server and
	 the DUT are running on the Raspberry PI, if this is convenient for testing.
* The **DUT** only needs to support a small **wfx_test_agent** executable with the following capabilities:
	* `write_test_data [data_string]` (required for Tx and Rx testing)
	* `read_rx_stats` (required only for Rx testing)
	* `read_agent_version` (optional, used for logging test conditions)
	* `read_driver_version` (optional, used for logging test conditions)
	* `read_fw_version` (optional, used for logging test conditions)

### Prerequisites
First install the  **WXF connection layer**
The connection layer is the same as the one used for WFX RF testing, allowing connection in the following modes:
* Local
* SSH
* UART

The connection layer is available in 
https://github.com/SiliconLabs/wfx-common-tools/tree/master/connection
(a subfolder of `wfx-common-tools`, so from the PTA scripts perspective they are under `../connection`)

Refer to 
https://github.com/SiliconLabs/wfx-common-tools/blob/master/connection/README.md
 for details on the connection layer and its installation.

### DUT wfx_test_agent installation
The **wfx test agent** needs to be installed on the **DUT**

* Installation differs depending on the platform
* Download from 
https://github.com/SiliconLabs/wfx-common-tools/blob/master/test-feature/wfx_test_agent
the agent corresponding to your platform
#### Linux wfx test agent
* The Linux agent is directly usable on Linux platforms
	* make sure it has execution rights and is in the path (create a link as /usr/local/bin/wfx_test_agent)
	```
	chmod a+x   /home/pi/siliconlabs/wfx-linux-tools/test-feature/wfx_test_agent
	sudo ln -sf /home/pi/siliconlabs/wfx-linux-tools/test-feature/wfx_test_agent /usr/local/bin/wfx_test_agent
	```
	TEMPORARY information (until the repository https://github.com/SiliconLabs/wfx-common-tools is made public):
	```
	chmod a+x   /home/pi/siliconlabs/wfx-common-tools/test-feature/wfx_test_agent/linux/wfx_test_agent
	sudo ln -sf /home/pi/siliconlabs/wfx-common-tools/test-feature/wfx_test_agent/linux/wfx_test_agent /usr/local/bin/wfx_test_agent
	```
	
### RTOS/Bare Metal wfx_test_agent
* The RTOS and Bare Metal agents need to be adapted and be compiled for your platform

### wfx_test_agent validation
*The wfx_test_agent can be tested & validated stand-alone before being used for RF Testing:*
* On Linux platforms, call `wfx_test_agent <option>` to test all options
* On platforms accessible via SSH, open a SSH session and call `wfx_test_agent <option>` to test all options
* On platforms accessible via UART, open a terminal and call `wfx_test_agent <option>` to test all options

### Executing commands on the DUT
Executing commands on the DUT is possible using the dut.run(cmd) syntax

An example is checking the wfx_test_agent version:
```
dut.run('wfx_test_agent read_agent_version')
```
Any other DUT command can also be called in a similar way. 
For instance, the following would work on a Linux DUT
```
dut.run('uname -r')
```

### [DUT wfx_test_agent options/features](#agent-features)
Some DUT wfx_test_agent features are mandatory for RF Testing:

* `write_test_data [data_string]` (required for Tx and Rx testing)
	* Send [data_string] as a HI_CONFIGURATION_REQ_ID request message payload
* `read_rx_stats` (required only for Rx testing)
	* Return the payload of a HI_GENERIC_INDICATION_ID_RX_STATS indication message
	 formatted as follows (abstract):
```
Timestamp: 43158786us
Low power clock: frequency 32759Hz, external yes
Num. of frames: 73, PER (x10e4): 1780, Throughput: 63Kbps/s
       Num. of      PER     RSSI      SNR      CFO
        frames  (x10e4)    (dBm)     (dB)    (kHz)
   1M       62      322      -76       17      -26
   2M        0        0        0        0        0
. . .
  54M        1    10000      -90        4       65
 MCS0        0        0        0        0        0
. . .
 MCS7        0        0        0        0        0
```

Others are only useful to log test conditions:

* `read_agent_version` (returns '1.0.0' at the time os writing)
* `read_driver_version` (returns '2.0.3' at the time os writing)
* `read_fw_version` (returns '2.2.1' at the time os writing)
## DUT with SSH connection
The wfx_test_agent needs to be executed with root privileges over SSH.

To achieve this on platforms the root user can be accessed using a password, use the root account to connect the DUT.

The Raspberry Pi does not allow a root user to be accessed using a password, so the necessary steps are required (once):

* Copying the server's public key to the 'pi' user's account
* Logging as user 'pi'
* As user Pi, use 'sudo' to copy the public key from the 'pi' user's account to the root user account.

Following this, access to Raspberry PIs with root privileges will be possible using user='root, host = '<pi_address>'
when connecting the DUT (with no password)

## [Typical Use Case](#typical-use-case)

### DUT initialization
```
cd ~/siliconlabs/wfx-common-tools/test-feature
python3
>>> from wfx_test_dut import *
```
* Local/Direct DUT connection
```
>>>  dut = WfxTestDut('Local')
```
* SSH DUT connection
```
>>>  dut = WfxTestDut('Pi_186', host='10.5.124.186', user='root', port=22)
```

_NB: for SSH connection: user, port and password values are optional, values used above are the default values
 (The user account needs to have root privileges)_

* UART DUT connection
```
>>>  dut = WfxTestDut('Serial', port='COM21', baudrate=115200, bytesize=8, parity='N', stopbits=1)
```
_NB: for UART connection: baudrate, bytesize, parity and stopbits values are optional, 
 values used above are the default values_

### Tx (modulated)
```
>>> dut.tx_rx_select(1,1)
>>> dut.channel(11)
>>> dut.tx_mode('GF_MCS0')
>>> dut.tx_framing(packet_length_bytes, ifs_us)
>>> dut.tx_start('continuous')
. . .
>>> dut.tx_stop()
```
While testing, messages are issued in dmesg every TEST_IND period (in ms):
```
wfx_wlan: Start TX packet test feature
wfx_wlan: TX packet test ongoing...
wfx_wlan: TX packet test ongoing...
. . .
wfx_wlan: End of TX packet test
wfx_wlan: Start TX packet test feature
wfx_wlan: End of TX packet test
```
NB: The last 2 lines correspond to the `stop()` call, which is sending 100 frames<br>
NB: `test_ind_period()` allows controlling the delay between these messages

### Tx (CW tone)
```
>>> dut.tx_rx_select(1,1)
>>> dut.channel(11)
>>> dut.tone_power(dbm)
>>> dut.tone_freq(freq)
>>> dut.tone_start([freq])
. . .
>>> dut.tone_stop()
```
While testing, messages are issued in dmesg every TEST_IND period (in ms):
```
wfx_wlan: Start TX CW test feature
wfx_wlan: TX CW test ongoing...
wfx_wlan: TX CW test ongoing...
. . .
wfx_wlan: End of TX CW test
wfx_wlan: Start TX packet test feature
wfx_wlan: End of TX packet test
```
NB: The last 2 lines correspond to the `tone_stop()` call, which is sending 100 frames<br>
NB: `dut.test_ind_period()` allows controlling the delay between these messages

### Rx
```
>>> dut.tx_rx_select(1,1)
>>> dut.channel(11)
>>> dut.rx_start()
>>> dut.rx_receive('MCS7', frames=10000, timeout = 10)
>>> dut.rx_logs('global')
>>> dut.rx_logs('MCS7')
>>> dut.rx_logs()
. . .
>>> dut.rx_stop()
```
While testing, an rx_stats indication message is updated by the FW every 
`test_ind_period` (default 1000 ms), and transmitted to the driver as a
 HI_GENERIC_INDICATION_ID_RX_STATS indication message.
 Under Linux, it is formatted and copied by the driver under
  `/sys/kernel/debug/ieee80211/phy*/wfx/rx_stats`.
 For non-Linux platforms, the wfx_test_agent should format the HI_GENERIC_INDICATION_ID_RX_STATS indication message
 to the same format and return it when called with option `'read_rx_stats`.
 
This content is polled by `dut.rx_receive()`, results are accumulated and averaged
 internally by the Python code.
 The results are retrieved by the user using `dut.rx_logs()` under the following form:
* 'global' results
```
>>> dut.rx_logs('global')
frames   588  errors   116  PER 1.973e-01  Throughput    78  deltaT 10000057  loops    10  start_us 2245737  last_us 12245794
```

* results for a selected modcode:
``` 
>>> dut.rx_logs('24M')
frames    76  errors    48  PER 6.316e-01  RSSI   -79  SNR     7  CFO   -18
```

* all results
```
>>> dut.rx_logs():
mode  global  frames   588  errors   116  PER 1.973e-01  Throughput    78  deltaT 10000057  loops    10  start_us 2245737  last_us 12245794
mode      1M  frames   457  errors    14  PER 3.063e-02  RSSI   -77  SNR    10  CFO   -28
mode      2M  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    5.5M  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode     11M  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode      6M  frames     4  errors     3  PER 7.500e-01  RSSI   -78  SNR     8  CFO   -22
mode      9M  frames    10  errors    10  PER 1.000e+00  RSSI   -82  SNR     3  CFO    34
mode     12M  frames     9  errors     9  PER 1.000e+00  RSSI   -83  SNR     5  CFO    19
mode     18M  frames     5  errors     5  PER 1.000e+00  RSSI   -83  SNR     7  CFO    18
mode     24M  frames    76  errors    48  PER 6.316e-01  RSSI   -79  SNR     7  CFO   -18
mode     36M  frames     4  errors     4  PER 1.000e+00  RSSI   -76  SNR     9  CFO   -22
mode     48M  frames     7  errors     7  PER 1.000e+00  RSSI   -84  SNR     2  CFO    -2
mode     54M  frames     7  errors     7  PER 1.000e+00  RSSI   -84  SNR     2  CFO   -27
mode    MCS0  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    MCS1  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    MCS2  frames     1  errors     1  PER 1.000e+00  RSSI   -80  SNR     9  CFO   -20
mode    MCS3  frames     8  errors     8  PER 1.000e+00  RSSI   -80  SNR     9  CFO   -23
mode    MCS4  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    MCS5  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    MCS6  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
mode    MCS7  frames     0  errors     0  PER 1.000e+00  RSSI     0  SNR     0  CFO     0
```

NB: PER values above are only considering **received** packets, they do not take into account lost packets.
To get a PER taking into account the lost packets it is necessary to compute 
the total number of packets for each mode using the deltaT value and the source settings. 
This is closely related to the equipment used to generate the source signal, with is specific to each test setup.

## Test data structure
The test data structure as filled before calling pds_compress is as follows:
```
RF_ANTENNA_SEL_DIV_CFG : {
        RF_PORTS :                        TX1_RX1,
},
MAX_TX_POWER_CFG : {
        FRONT_END_LOSS_CORRECTION_QDB :   0,
        MAX_OUTPUT_POWER_QDBM :           80,
        BACKOFF_QDB : [ {
                CHANNEL_NUMBER :                  [1, 14],
                BACKOFF_VAL :                     [0, 0, 0, 0, 0 ,0],
        } ],
        RF_PORT :                         RF_PORT_BOTH,
},
TEST_FEATURE_CFG : {
        RX :                              { },
        CFG_TX_PACKET : {
                REG_MODE :                        DFS_Unrestricted,
                IFS_US :                          0,
                RATE :                            N_MCS7,
                NB_FRAME :                        0,
                FRAME_SIZE_BYTE :                 3000,
                HT_PARAM :                        MM,
        },
        CFG_TX_CW : {
                FREQ1 :                           1,
                FREQ2 :                           2,
                CW_MODE :                         single,
                MAX_OUTPUT_POWER :                68,
        },
        TEST_IND :                        1000,
        TEST_CHANNEL_FREQ :               11,
        TEST_MODE :                       tx_packet,
},
```

# test modules details
## wfx_connection module
**wfx_connection.py** manages the connectivity between the Tester and the DUT
* `uarts()`             : list the existing uarts on the Tester which can be used to connect to DUTs over RS232
* `networks()`          : list the existing IP networks on the Tester which can be used to connect to DUTs over SSH
* `write(text)`         : write the input text to the DUT
* `read(text)`          : read the DUT reply
* `run(cmd, wait_ms=0)` : call `write(cmd)`, pause for wait_ms, then call `read()` to retrieve the DUT answer
* **class Uart** is implementing the above functions for UART DUTs
* **class Ssh** is implementing the above functions for SSH DUTs
* **class Direct** is implementing the above functions for Direct/Local DUTs, i.e. those connected directly 
 when the Tester is also the DUT

## pds_compress module
**pds_compress.py** is basically a copy of the pds_compress tool used to compress the PDS data
 (the one sent right after FW download) with the added `.py` extension, such that it can be loaded as
  a Python3 module. It is much faster to load this module once and for all than calling it from the OS every 
  time test data needs to be 'compressed'.

## wfx_pds_tree module 
**wfx_pds_tree.py** manages the Test data in a nested dict

**wfx_pds{}** defines the Test data structure
* `ITEM` names are unique by design (FW constraint)
* `VERSION` defines the mimimal FW version
* `PATH` defines the position of each item in the tree
* `DEFAULT` defines the default value
* `VALUES` lists possible values for each item
* `DOC` contains the documentation relative to each item

_NB: The line order defines in which order sections are to be sent (when sending several sections) as well as 
in which order items within a section wil be ordered_

### class PdsTree(dict)
* `fill_tree(version)`              : Fills the tree, adding only items supported by the current FW.
* `get(key)`                        : Gets an item value, wherever it is in the tree.
* `pretty()`                        : Returns tabulated Test data (much easier to read than print() output).
* `print()`                         : Returns one-line Test data.
* `set(key, value)`                 : Sets an item to a new value, wherever it is in the tree.
* `set_current_fw_version(version)` : Stores the current FW version (retrieved from HW by upper layers).
* `sub_tree(keys)`                  : Returns a copy of the Test data, with only (entire) sections matching
  the selected keys. Used to avoid sending entire test data on each 'send'.

**Additional PdsTree functions**
* `add_tmp_param("version", "path", "key", "default")`: Add a (temporary) parameter to the test data structure.
 Useful to test FW release candidates in the lab. *Most probably not relevant for customers*

**Additional wfx_pds_tree functions**
* `add_pds_warning(msg)`            : accumulate error messages related to test data processing.
* `check_pds_warning(msg="")`       : return accumulated error messages related to test data processing.
 Clear previous messages before returning. If no error, return `msg`

## wfx_test_target module
###dependencies
**wfx_test_target.py** relies on
* **wfx_connection.py** to communicate with the DUT
* **wfx_pds_tree.py** to store and manage test data
* **pds_compress.py** to compress test data

### class WfXTestTarget(object)
* `write(text)`                         : write the input text to the DUT
* `read(text)`                          : read the DUT reply
* `run(cmd, wait_ms=0)`                 : call `write(cmd)`, pause for wait_ms, then call `read()` to get DUT answer
* `wfx_get_list(param_list)`            : Returns a name/value sequence for all selected items.
* `wfx_set_dict(param_dict, send_data)` : Sets all selected items to their desired values, 
 compress the test data tree and send the result (send only if send_data == 1(default)).

## wfx_test_dut module
**wfx_test_dut.py** translates the test API user function calls into test data and sends it.
These are the functions which are primarily used by users to test the product.

*NB: When called with no argument, most functions return the corresponding value(s) of the parameter(s) they control*

###dependencies
**wfx_test_dut.py** relies on
* **wfx_test_target.py** to handle the test data and communicate with the DUT

### class WfXTestDut(WfxTestTarget)
* `channel(ch)`                      : set the test channel
* `read_rx_stats()`                  : call `run('wfx_test_agent read_rx_start')` to retrieve the Rx stats
* `regulatory_mode(reg_mode)`        : applies TX power backoff for the selected region
* `rx_logs(mode=None)`               : retrieve accumulated python content of Rx stats polling. Full table if no 'mode',
 otherwise only the row matching the 'mode' (logs are available until next `tx_receive()` call)
* `rx_receive(mode, frames, sleep_ms, timeout)` : Clear Rx logs and polls Rx stats until it has received
 the required number of frames(default 1000). When mode == `endless`, run continuously
* `rx_start()`                       : start Rx test in the DUT
* `rx_stop()`                        : stop Rx test in the DUT and Python3 polling thread
* `read_agent_version()`             : returns Agent version
* `read_driver_version()`            : returns driver version
* `read_fw_version()`                : returns FW version
* `test_conditions()`                : returns DUT/Driver/FW/Tools/Agent versions and DUT connection info
* `test_ind_period()`                : set the delay between indication messages in Tx and Rx_stats in Rx
* `tone_freq(offset=None)`           : set CW tone offset at 312.5kHz*offset([-31,31], default 0)
* `tone_power(dBm)`                  : set tone power
* `tone_start(offset=None)`          : start CW tone on current channel, offset by 312.5kHz*offset([-31,31], default 0)
* `tone_stop()`                      : stop CW tone
* `tx_backoff(mod, backoff_level)`   : set power backoff for one group of modulations. All other backoff 0.
* `tx_framing(pkt_len, ifs_us)`      : control the frame size (in bytes) and IFS (InterFrame Spacing)
* `tx_mode(mode)`                    : select between MM (mixed mode) & GF (Greenfield) and sets the rate
* `tx_power(dBm)`                    : set the maximum output power
* `tx_rx_select(tx_ant, rx_ant)`     : select the Tx/Rx antennas
* `tx_start(nb_frames)`              : start sending a selected number of frames. With 0 or 'continuous' = continuous
* `tx_stop()`                        : send a burst of 100 frames to complete a previous continuous transmission 
* `rx_start()`                       : start receiving frames (all modulations)
* `rx_stop()`                        : call tx_stop() to stop receiving

## [wfx_test_dut API](#API)
### wfx_test_dut parameters vs Test parameters

| function          | function parameters                                                          | Test parameters                          |
|-------------------|------------------------------------------------------------------------------|------------------------------------------|
| `channel`         |`ch`: [1-14]\(channel\) or [2300-2530] MHz                                    |`TEST_CHANNEL_FREQ`                       |
| `tone_freq`       |`offset`: offset in 312.5 kHz steps                                           |`FREQ1`                                   |
| `tone_power`      |`dbm`: [TBD]                                                                  |`MAX_OUTPUT_POWER`                        |
| `tone_start`      |`offset`: offset in 312.5 kHz steps                                           |`TEST_MODE`<br>`NB_FRAME`<br>`FREQ1`      |
| `tone_stop`       |**none**                                                                      |`TEST_MODE`<br>`NB_FRAME`                 |
| `tx_backoff`      |`mode_802_11`:<br>'[B, CCK, DSS]\_[1, 2, 5_5, 11]Mbps'<br>'[G, LEG]\_[6, 9, 12, 18, 24, 36, 48, 54]Mbps'<br>'[MM, GF]\_MCS[0-7]'<br>**Examples**: 'B_1Mbps', 'LEG_54Mbps', 'GF_MCS5'<br>`backoff_level`: [0:63.75] dB|`BACKOFF_VAL`|
| `tx_framing`      |`packet_length_bytes`:[25-4091] Frame size in bytes\(without CRC\)<br>`ifs_us`:[0-255] Interframe spacing in us|`FRAME_SIZE_BYTE`<br>`IFS_US` |
| `tx_mode`         |`mode_802_11`:<br>'[B, CCK, DSS]\_[1, 2, 5_5, 11]Mbps'<br>'[G, LEG]\_[6, 9, 12, 18, 24, 36, 48, 54]Mbps'<br>'[MM, GF]\_MCS[0-7]'<br>**Examples**: 'B_1Mbps', 'LEG_54Mbps', 'GF_MCS5'|`HT_PARAM`<br>`RATE`|
| `tx_power`        |`dbm`: [TBD]                                                                  |`MAX_OUTPUT_POWER_QDBM`                   |
| `tx_rx_select`    |`tx_ant`: [1-2] Tx antenna<br>`rx_ant`: [1-2] Rx antenna                      |`RF_PORTS`                                |
| `tx_start`        |`nb_frames`: [0-65535] or 'continuous'. Nb of frames to send before stopping. |`NB_FRAME`                                |
| `tx_stop`         |**none**                                                                      |`NB_FRAME`                                |
| `regulatory_mode` |`reg_mode`:<br>'[All, FCC, ETSI, JAPAN, Unrestricted]'                        | `REG_MODE`                               |
| `add_tmp_param`   |`version`: min FW, `path`: position in tree, `key`: name, `default`:value     | `key` (as entered)                       |
| `test_ind_period` |`period`:[0-TBD/65535?] delay in ms between messages                          |`TEST_IND`                                |
| `rx_start`        |**none**                                                                      |`TEST_MODE`                               |
| `rx_stop`         |**none**                                                                      |`NB_FRAME`                                |
| `rx_receive`      |`mode`: <br>'global'(default if '')<br>'[1, 2, 5.5, 11, 6, 9, 12, 18, 24, 36, 48, 54]M'<br>'MCS[0-7]'<br>`frames`: Nb of frames to receive before stopping'<br>`sleep_ms`:[(750)]. Polling period. No need to poll too often, the FW updates the table only every second<br>`timeout`: max number of seconds to poll (useful if very few frames are received) |**none**|
| `rx_logs`         |`mode`: <br>'global'(default if '')<br>'[1, 2, 5.5, 11, 6, 9, 12, 18, 24, 36, 48, 54]M'<br>'MCS[0-7]'|**none**           |


## Printing the current test tree content

| pretty (tabulated)              | single line                     |
|---------------------------------|---------------------------------|
| `print(dut.test_data.pretty())` | `print(dut.test_data.print())`  |

_Nb: the above is only possible if using `dut = WfxTestDut(...)`._

## Advanced features

### Traces
**Tracing test data settings**

use `dut.trace = True` to trace all changes to test data items

**Tracing dut communication link**

use `dut.link.trace = True` to trace all communication with the wfx_test-agent

### Accessing a test parameter if it's not managed by a test function

All parameters (even those not managed by test functions) listed in the 
 wfx_test_dut API are still accessible using generic functions:

**Reading**
```
dut.test_data.wfx_get_list({'NB_FRAME'})
dut.test_data.wfx_get_list({'TEST_MODE','NB_FRAME'})
```
 
**Writing** (without sending Test data)
```
dut.test_data.wfx_set_dict({'NB_FRAME':12}, 0)
dut.test_data.wfx_set_dict({'TEST_MODE':'tx_packet','NB_FRAME':12}, 0)
```

**Writing**(sending Test data)
```
dut.test_data.wfx_set_dict({'NB_FRAME':12}, 1)
dut.test_data.wfx_set_dict({'TEST_MODE':'tx_packet','NB_FRAME':12}, 1)
```

### Adding a temporary test parameter

It is possible to define new parameters and access them using the generic
 `wfx_get_list` / `wfx_set_dict` functions described above.

**Adding a test parameter**
```
dut.test_data.add_tmp_param('version', 'path', 'key', 'default')
```
adds a (temporary) parameter to the Test structure. This is useful to test FW release candidates in the lab

* **example**

```
# Creating the params in the tree (Pending FW support for 'z.a.b.x' &  'z.a.b.y'):
dut.test_data.add_tmp_param(pds, '2.0', 'z.a.b', 'x', '10')
dut.test_data.add_tmp_param(pds, '2.0', 'z.a.b', 'y', '25')

# Setting the value and sending Test data:
dut.test_data.wfx_set_dict({'x':15, 'y':32}, 1)
```

# Real-life testing
## Direct on Raspberry PI (without SSH)
Below is an example of testing directly on the Raspberry PI, having the PI as both RF Test Server and DUT
```
python3
Python 3.4.2 (default, Oct 19 2014, 13:31:11)
[GCC 4.9.1] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from wfx_test_dut import *
/usr/local/lib/python3.4/dist-packages/cryptography/hazmat/bindings/openssl/binding.py:163:
 CryptographyDeprecationWarning: OpenSSL version 1.0.1 is no longer supported by the OpenSSL project, please upgrade. A future version of cryptography will drop support for it.
  utils.CryptographyDeprecationWarning
```
*Disregard the **CryptographyDeprecationWarning** above, since it's related to paramiko dependencies,
 and dealing with these it out of our scope (as long as it still works)* 
```
>>> dut = WfxTestDut('Local')
Local: Configuring a Direct connection
Local    D>>|  wfx_test_agent read_fw_version
<<D    Local|  2.2.1
```
*The lines with `Local    D>>|` or `<<D    Local|` are write/read traces coming from the connection link.
These can be disabled using `dut.link.trace = False`. They are useful to check/debug the wfx_test_agent behavior.*
```
Local: fw_version retrieved from HW (2.2.1)
  Info: 'RSSI_CORRECTION' cannot be supported with FW2.2.1, it has been added in FW2.2.2 (skipped)
```
*The above information tells us that the current FW is 2.2.1. 
In wfx_pds{} the VERSION value for 'RSSI_CORRECTION' is 2.2.2.
This means that the current FW doesn't support 'RSSI_CORRECTION', so it's not added to the test_data we will 
 use here, to avoid FW exceptions*
```
fill_tree has messages:
  Info: 'RSSI_CORRECTION' cannot be supported with FW2.2.1, it has been added in FW2.2.2 (skipped)
```
*After filling the test_data tree, the code checks for any test data processing message (using `check_pds_warning()`),
 so the message is first printed when it occurs then following this check.*
```
Local: tree filled for FW2.2.1
```
*Finally, we get a message indicating the FW version used by the test data.*
```
Local    D>>|  wfx_test_agent read_agent_version
<<D    Local|  1.0.0
Direct agent_reply: 1.0.0
>>> dut.test_conditions()
Local    D>>|  wfx_test_agent read_agent_version
<<D    Local|  1.0.0
Local    D>>|  wfx_test_agent read_fw_version
<<D    Local|  2.2.1
Local    D>>|  wfx_test_agent read_driver_version
<<D    Local|  2.0.3
'Test conditions: DUT Local / Driver 2.0.3 / FW 2.2.1 / Tools 1.0.0 / Agent 1.0.0 / Direct'
>>>
```
*Here we see the wfx_test_agent in action, replying to options used to retrieve the test conditions*
```
>>> dut.channel(7)
Local    SET|   TEST_CHANNEL_FREQ  7
'TEST_CHANNEL_FREQ  7'
>>> dut.tx_start('continuous')
Local    D>>|  wfx_test_agent write_test_data  "{i:{a:7,b:1,f:3E8,c:{a:0,b:1,c:2,d:44},d:{a:BB8,b:0,c:0,d:15,e:0,f:4},e:{}}}"
<<D    Local|  '{i:{a:7,b:1,f:3E8,c:{a:0,b:1,c:2,d:44},d:{a:BB8,b:0,c:0,d:15,e:0,f:4},e:{}}}' sent to /sys/kernel/debug/ieee80211/phy0/wfx/send_pds
Local    SET|   TEST_MODE  tx_packet     NB_FRAME  0
'TEST_MODE  tx_packet     NB_FRAME  0'
>>>
```
*Here we see no call to wfx_test_agent when calling channel(7), since no test data is sent at this time, by design
 of the Python3 code. Test data is sent when calling tx_start(...). We see the test data being sent in compressed format
  using `wfx_test_agent write_test_data <data_string>`*

*Calling `tx_start('continuous')`, as we can see above, sets NB_FRAME to **0**, and the FW will enter permanent Tx mode.*
```
>>> print(dut.run('dmesg | tail'))
Local    D>>|  dmesg | tail
<<D    Local|  [942575.126128] wfx_wlan: TX packet test ongoing...
<<D    Local|  [942576.126134] wfx_wlan: TX packet test ongoing...
<<D    Local|  [942577.126136] wfx_wlan: TX packet test ongoing...
<<D    Local|  [942578.126161] wfx_wlan: TX packet test ongoing...
<<D    Local|  [942579.126089] wfx_wlan: TX packet test ongoing...
<<D    Local|  [942580.126097] wfx_wlan: TX packet test ongoing...
<<D    Local|  [942581.126079] wfx_wlan: TX packet test ongoing...
<<D    Local|  [942582.126087] wfx_wlan: TX packet test ongoing...
<<D    Local|  [942583.126081] wfx_wlan: TX packet test ongoing...
<<D    Local|  [942584.126201] wfx_wlan: TX packet test ongoing...
[942575.126128] wfx_wlan: TX packet test ongoing...
[942576.126134] wfx_wlan: TX packet test ongoing...
[942577.126136] wfx_wlan: TX packet test ongoing...
[942578.126161] wfx_wlan: TX packet test ongoing...
[942579.126089] wfx_wlan: TX packet test ongoing...
[942580.126097] wfx_wlan: TX packet test ongoing...
[942581.126079] wfx_wlan: TX packet test ongoing...
[942582.126087] wfx_wlan: TX packet test ongoing...
[942583.126081] wfx_wlan: TX packet test ongoing...
[942584.126201] wfx_wlan: TX packet test ongoing...
>>>
```
*The above is using a Linux-specific command to illustrate the fact that any OS 
 command is callable using dut.run('command')*

*Under Linux, we see here the 'HI_GENERIC_INDICATION_TYPE_STRING' string messages received by the
 driver being copied to dmesg. We can also see that they appear with a period of 1000 ms, 
 matching the default value of TEST_IND (set using `dut.test_ind_period(period_ms)`).*

*NB: There is no driver processing on those messages, they are directly coming from the FW 'as is'*  
```
>>> dut.tx_stop()
Local    D>>|  wfx_test_agent write_test_data  "{i:{a:7,b:1,f:3E8,c:{a:0,b:1,c:2,d:44},d:{a:BB8,b:0,c:0,d:15,e:64,f:4},e:{}}}"
<<D    Local|  '{i:{a:7,b:1,f:3E8,c:{a:0,b:1,c:2,d:44},d:{a:BB8,b:0,c:0,d:15,e:64,f:4},e:{}}}' sent to /sys/kernel/debug/ieee80211/phy0/wfx/send_pds
Local    SET|   TEST_MODE  tx_packet     NB_FRAME  100
'TEST_MODE  tx_packet     NB_FRAME  100'
>>>
```
*Once we have measured the Tx signal (using our test equipment), we stop the transmission.
 There is no real 'stop' feature in the FW, so we use a 'Tx 100 frames then stop' setting
  (less than 25 frames is not accepted by the FW)*
```
>>> dut.link.trace = False
>>> print(dut.run('dmesg | tail -n 5'))
[943517.134836] wfx_wlan: TX packet test ongoing...
[943518.134831] wfx_wlan: TX packet test ongoing...
[943518.170225] wfx_wlan: End of TX packet test
[943518.171552] wfx_wlan: Start TX packet test feature
[943518.212839] wfx_wlan: End of TX packet test
>>>
```
*Here we stop the link trace to avoid too many lines, and we check the content of `dmesg`. We see 
 a 'Start TX' message closely followed by an 'End of TX' message. These 2 correspond to the transmission of
 100 frames we triggered to stop transmitting*
```
>>> quit()
```
*Use `quit()` to stop testing*

## Local on Raspberry PI (via SSH)
```
python3
Python 3.4.2 (default, Oct 19 2014, 13:31:11)
[GCC 4.9.1] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from wfx_test_dut import *
/usr/local/lib/python3.4/dist-packages/cryptography/hazmat/bindings/openssl/binding.py:163: CryptographyDeprecationWarning: OpenSSL version 1.0.1 is no longer supported by the OpenSSL project, please upgrade. A future version of cryptography will drop support for it.
  utils.CryptographyDeprecationWarning
```
*Disregard the **CryptographyDeprecationWarning** above, since it's related to paramiko dependencies,
 and dealing with these it out of our scope (as long as it still works)* 
```
>>> dut = WfxTestDut('SSH', host='127.0.0.1', user='pi', password='default_password', port=22)
SSH: Configuring a SSH connection to host 127.0.0.1 for user pi
INFO:root:SSH           I'm connected to 127.0.0.1:22 as pi
```
*Good news: The rest is strictly identical to the **Direct on Raspberry PI (without SSH)** case!*

## Remote on Raspberry PI (via SSH)
**(On Test server)**
```
 python3
Python 3.4.2 (default, Oct 19 2014, 13:31:11)
[GCC 4.9.1] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from wfx_test_dut import *
>>> dut = WfxTestDut('SSH', host='10.5.124.186', user='root', port=22)
SSH: Configuring a SSH connection to host 10.5.124.186 for user root
/usr/local/lib/python3.4/dist-packages/cryptography/hazmat/bindings/openssl/binding.py:163: CryptographyDeprecationWarning: OpenSSL version 1.0.1 is no longer supported by the OpenSSL project, please upgrade. A future version of cryptography will drop support for it.
  utils.CryptographyDeprecationWarning
/usr/local/lib/python3.4/dist-packages/paramiko/kex_ecdh_nist.py:39: CryptographyDeprecationWarning: encode_point has been deprecated on EllipticCurvePublicNumbers and will be removed in a future version. Please use EllipticCurvePublicKey.public_bytes to obtain both compressed and uncompressed point encoding.
  m.add_string(self.Q_C.public_numbers().encode_point())
/usr/local/lib/python3.4/dist-packages/paramiko/kex_ecdh_nist.py:96: CryptographyDeprecationWarning: Support for unsafe construction of public numbers from encoded data will be removed in a future version. Please use EllipticCurvePublicKey.from_encoded_point
  self.curve, Q_S_bytes
/usr/local/lib/python3.4/dist-packages/paramiko/kex_ecdh_nist.py:111: CryptographyDeprecationWarning: encode_point has been deprecated on EllipticCurvePublicNumbers and will be removed in a future version. Please use EllipticCurvePublicKey.public_bytes to obtain both compressed and uncompressed point encoding.
  hm.add_string(self.Q_C.public_numbers().encode_point())
```
*Disregard the **CryptographyDeprecationWarning** above, since it's related to paramiko dependencies,
 and dealing with these it out of our scope (as long as it still works)* 
```
INFO:root:SSH           I'm connected to 10.5.124.186:22 as root
```
*Good news: The rest is strictly identical to the **Direct on Raspberry PI (without SSH)** case!*

## Remote on RTOS (via UART)
**(On Test server)**
```
python
Python 3.7.3 (v3.7.3:ef4ec6ed12, Mar 25 2019, 21:26:53) [MSC v.1916 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> from wfx_test_dut import *
>>> dut = WfxTestDut('Serial', port='COM21', baudrate=115200, bytesize=8, parity='N', stopbits=1)
Serial: Configuring a UART connection using COM21
Serial   U>>|  wfx_test_agent
<<U   Serial|  Unknown command
```
*The lines with `Serial    U>>|` or `<<U    Serial|` are write/read traces coming from the connection link.
These can be disabled using `dut.link.trace = False`. They are useful to check/debug the wfx_test_agent behavior.*

*Above we see the result of the wfx_test_agent call with no option. It still returns a string with `Unknown command`
 At this point, it proves there is communication with the DUT MCU*
```
Serial   U>>|  wfx_test_agent read_fw_version
<<U   Serial|  2.3.0
Serial: fw_version retrieved from HW (2.3.0)
Serial: tree filled for FW2.3.0
```
*Here we see that we can retrieve the FW version  from the wfx_test_agent. It is used to select which parameters
will be added to the test_data for this DUT. If the fw_version option is not supported by the wfx_test_agent, 
it can be set adding `, fw_version='<version>'` in the call to `WfxTestDut(...)`. By default, it will otherwise 
assume that all test data parameters are supported.*
```
Serial   U>>|  wfx_test_agent read_agent_version
<<U   Serial|  Unknown command
UART COM21/115200/8/N/1 agent_reply: Unknown command
>>> dut.test_conditions()
Serial   U>>|  wfx_test_agent read_agent_version
<<U   Serial|  Unknown command
Serial   U>>|  wfx_test_agent read_fw_version
<<U   Serial|  2.3.0
Serial   U>>|  wfx_test_agent read_driver_version
<<U   Serial|  Not supported
'Test conditions: DUT Serial / Driver Not supported / FW 2.3.0 / Tools 1.0.0 / Agent Unknown command / UART COM21/115200/8/N/1'
>>>
```
*Here we see that even though some options are not implemented in the wfx_test_agent, we can retrieve useful info
 anyway to log our test conditions for this DUT*
*Good news: The rest is strictly identical to the **Direct on Raspberry PI (without SSH)** case, 
 except the Linux OS commands, of course. But existing RTOS OS commands can be called!*

## Multiple DUTs
**(On Test server)**
```
python
Python 3.7.3 (v3.7.3:ef4ec6ed12, Mar 25 2019, 21:26:53) [MSC v.1916 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> from wfx_test_dut import *
>>> uart_dut = WfxTestDut('Serial', port='COM21', baudrate=115200, bytesize=8, parity='N', stopbits=1)
Serial: Configuring a UART connection using COM21
Serial   U>>|  wfx_test_agent
<<U   Serial|  Unknown command
Serial   U>>|  wfx_test_agent read_fw_version
<<U   Serial|  2.3.0
Serial: fw_version retrieved from HW (2.3.0)
Serial: tree filled for FW2.3.0
Serial   U>>|  wfx_test_agent read_agent_version
<<U   Serial|  Unknown command
UART COM21/115200/8/N/1 agent_reply: Unknown command
```
*An uart DUT has just been configured...*
```
>>> ssh_dut = WfxTestDut('SSH', host='10.5.124.186', user='root', port=22)
SSH: Configuring a SSH connection to host 10.5.124.186 for user root
C:\Program Files (x86)\Python37-32\lib\site-packages\paramiko\kex_ecdh_nist.py:39: CryptographyDeprecationWarning: encode_point has been deprecated on EllipticCurvePublicNumbers and will be removed in a future version. Please use EllipticCurvePublicKey.public_bytes to obtain both compressed and uncompressed point encoding.
  m.add_string(self.Q_C.public_numbers().encode_point())
C:\Program Files (x86)\Python37-32\lib\site-packages\paramiko\kex_ecdh_nist.py:96: CryptographyDeprecationWarning: Support for unsafe construction of public numbers from encoded data will be removed in a future version. Please use EllipticCurvePublicKey.from_encoded_point
  self.curve, Q_S_bytes
C:\Program Files (x86)\Python37-32\lib\site-packages\paramiko\kex_ecdh_nist.py:111: CryptographyDeprecationWarning: encode_point has been deprecated on EllipticCurvePublicNumbers and will be removed in a future version. Please use EllipticCurvePublicKey.public_bytes to obtain both compressed and uncompressed point encoding.
  hm.add_string(self.Q_C.public_numbers().encode_point())
INFO:root:SSH           I'm connected to 10.5.124.186:22 as root
SSH      S>>|  wfx_test_agent read_fw_version
<<S      SSH|  2.2.1
SSH: fw_version retrieved from HW (2.2.1)
  Info: 'RSSI_CORRECTION' cannot be supported with FW2.2.1, it has been added in FW2.2.2 (skipped)

fill_tree has messages:
  Info: 'RSSI_CORRECTION' cannot be supported with FW2.2.1, it has been added in FW2.2.2 (skipped)

SSH: tree filled for FW2.2.1
SSH      S>>|  wfx_test_agent read_agent_version
<<S      SSH|  1.0.0
SSH pi@10.5.124.186:22 agent_reply: 1.0.0
```
*A SSH DUT has just been configured...*
```
>>> uart_dut.link.trace = False
>>> ssh_dut.link.trace = False
>>> uart_dut.test_conditions()
'Test conditions: DUT Serial / Driver Not supported / FW 2.3.0 / Tools 1.0.0 / Agent Unknown command / UART COM21/115200/8/N/1'
>>> ssh_dut.test_conditions()
'Test conditions: DUT SSH / Driver 2.0.3 / FW 2.2.1 / Tools 1.0.0 / Agent 1.0.0 / SSH pi@10.5.124.186:22'
>>>
```
*We can access the uart DUT using `uart_dut.<>` and the SSH DUT using `ssh_dut.<>`. Many DUTs can be part of our test. 
 If we rely on scripts using `dut.<>`, we can use `dut = uart_dut` or `dut = ssh_dut` to switch between DUTs*

# [Hierarchy](#hierarchy)
```
                              ---------------------------------------------------------
                                                                                      |
  -------------------------                                                           |
  | customer_test.py      |                                                           |
  -------------------------                                                           |
            |                                                                         |
           \|/                                                                        |
  -------------------------                                                           |
  | serverPI_UDP.py       |                                                           |
  -------------------------                                                           | Running
            |                                                                         |   on
           \|/                                                                        | Tester
  -------------------------                                                           |
  | wfx_test_dut.py       |                                                           |
  -------------------------                                                           |
            |                                                                         |
            |---------------------------|                                             |
           \|/                         \|/                                            |
  -------------------------   -------------------------                               |
  | wfx_test_target.py    |   |      job.py           |                               |
  -------------------------   -------------------------                               |
            |                                                                         |
            |---------------------------|----------------------------|                |
           \|/                         \|/                          \|/               |
  -------------------------   -------------------------   -------------------------   |
  | wfx_connection.py     |   | pds_compress.py       |   | wfx_pds_tree.py       |   |
  -------------------------   -------------------------   -------------------------   |
           /|\                                                                        |
            |                 ---------------------------------------------------------
            |
            | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . UART or SSH connection
            |
            |                 ---------------------------------------------------------
           \|/                                                                        |
  -------------------------                                                           | Running
  | wfx_test_agent.py     |                                                           |   on
  -------------------------                                                           |  DUT(s)
                                                                                      |
                              ---------------------------------------------------------
```
