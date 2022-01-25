# WFX RF Testing

RF testing on WFx is achieved using the *wfx_test_dut* python3 module, available in the [wfx-common-tools repository 'test-feature' folder][COM_REPO_RF].

> NB: **wfx_test_dut** *is an evolution of the initial test-feature scripts which were present in the [wfx-linux-tools repository 'test-feature' folder][LIN_REPO_RF], with the added capability to be ran from a test server with either SSH, UART or TELNET access to the DUT. Only the Linux wfx_test_agent (discussed below) is now present under the [wfx-linux-tools repository 'test-feature' folder][LIN_REPO_RF]*.

The RF test architecture is now a Test Server/DUT configuration

* The **Test server** can run **wfx_test_dut** on any python3-capable platform with network and/or UART communication capabilities
  * One possible python3-capable platform is the Raspberry PI. In this case, both the Test Server and the DUT are running on the Raspberry PI, if this is convenient for testing.
* The **DUT** only needs to support a small **wfx_test_agent** executable with the following capabilities:
  * `write_test_data [data_string]` (required for Tx and Rx testing)
  * `read_rx_stats` (required only for Rx testing)
  * `read_agent_version` (optional, used for logging test conditions)
  * `read_driver_version` (optional, used for logging test conditions)
  * `read_fw_version` (optional, used for logging test conditions)
  * `read_tx_info` (optional, used with a FEM)

> NB: Prior to running RF testing, make sure you stop any WLAN use of your product.

## Prerequisites

First, install the  **WXF connection layer**

The connection layer is common to RF testing, allowing connection in the following modes:

* Local
* SSH
* UART

(The connection layer is available in [wfx-common-tools repository 'connection' folder][COM_REPO_CONN], so from the RF Test scripts perspective they are under `../connection`)

Refer to the [connection README][CONN_DOC] for details on the connection layer and its installation.

### DUT wfx_test_agent installation

The **wfx test agent** needs to be installed on the **DUT**

* Installation differs depending on the platform

#### Linux wfx test agent

* Download from the [wfx-linux-tools repository 'test-feature' folder][LIN_REPO_RF] the Linux wfx_test_agent

* The Linux agent is directly usable on Linux platforms
  * make sure it has execution rights and is in the path (create a link as /usr/local/bin/wfx_test_agent)

```bash
chmod a+x   /home/pi/siliconlabs/wfx-linux-tools/test-feature/wfx_test_agent
sudo ln -sf /home/pi/siliconlabs/wfx-linux-tools/test-feature/wfx_test_agent /usr/local/bin/wfx_test_agent
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

```python
dut.run('wfx_test_agent read_agent_version')
```

Any other DUT command can also be called in a similar way. 
For instance, the following would work on a Linux DUT

```python
dut.run('uname -r')
```

### [DUT wfx_test_agent options/features](#agent-features)

Some DUT wfx_test_agent features are mandatory for RF Testing:

* `write_test_data [data_string]` (required for Tx and Rx testing)
  * Send [data_string] as a HI_CONFIGURATION_REQ_ID request message payload
* `read_rx_stats` (required only for Rx testing)
  * Return the payload of a HI_GENERIC_INDICATION_ID_RX_STATS indication message formatted as follows (abstract):

```text
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

* `read_agent_version` (returns '1.0.0' at the time of writing)
* `read_driver_version` (returns '2.0.3' at the time of writing)
* `read_fw_version` (returns '2.2.1' at the time of writing)

Others are used with a FEM:
* `read_tx_info`

```text
Tx gain digital: 0
Tx gain PA: 0
Target Pout: 0.00 dBm
FEM Pout: 0.00 dBm
Vpdet: 0 mV
Measure index: 0
```

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

```bash
cd ~/siliconlabs/wfx-common-tools/test-feature
python3
```

```python
>>> from wfx_test_dut import *
```

#### Local/Direct DUT connection

```python
>>>  dut = WfxTestDut('Local')
```

#### SSH DUT connection

```python
>>>  dut = WfxTestDut('Pi_186', host='10.5.124.186', user='root', port=22)
```

_NB: for SSH connection: user, port and password values are optional, values used above are the default values
 (The user account needs to have root privileges)_

#### UART DUT connection (Linux, OS with login/password)

```python
>>>  dut = WfxTestDut('Serial', port='COM21', baudrate=115200, bytesize=8, parity='N', stopbits=1, user='<user>', password='<password>' )
```

_NB: for UART connection: baudrate, bytesize, parity and stopbits values are optional, values used above are the default values_

#### UART DUT connection (RTOS/Bare metal)

```python
>>>  dut = WfxTestDut('Serial', port='COM21', baudrate=115200, bytesize=8, parity='N', stopbits=1)
```

_NB: for UART connection: baudrate, bytesize, parity and stopbits values are optional, values used above are the default values_

### Tx (modulated)

```python
>>> dut.tx_rx_select(1,1)
>>> dut.channel(11)
>>> dut.tx_mode('GF_MCS0')
>>> dut.tx_framing(packet_length_bytes, ifs_us)
>>> dut.tx_start('continuous')
. . .
>>> dut.tx_stop()
```

While testing, messages are issued in dmesg every TEST_IND period (in ms):

```text
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

```python
>>> dut.tx_rx_select(1,1)
>>> dut.channel(11)
>>> dut.tone_power(dbm)
>>> dut.tone_freq(freq)
>>> dut.tone_start([freq])
. . .
>>> dut.tone_stop()
```

While testing, messages are issued in dmesg every TEST_IND period (in ms):

```text
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

```python
>>> dut.tx_rx_select(1,1)
>>> dut.channel(11)
>>> dut.rx_start()
>>> dut.rx_receive('MCS7', frames=10000, timeout_s = 10)
>>> dut.rx_logs('global')
>>> dut.rx_logs('MCS7')
>>> dut.rx_logs()
. . .
>>> dut.rx_stop()
```

While testing, an rx_stats indication message is updated by the FW every `test_ind_period` (default 1000 ms), and transmitted to the driver as a  HI_GENERIC_INDICATION_ID_RX_STATS indication message.

* Under Linux, it is formatted and copied by the driver under
  `/sys/kernel/debug/ieee80211/phy*/wfx/rx_stats`.
* For non-Linux platforms, the wfx_test_agent should format the HI_GENERIC_INDICATION_ID_RX_STATS indication message
 to the same format and return it when called with option `'read_rx_stats`.

This content is polled by `dut.rx_receive()`, results are accumulated and averaged
 internally by the Python code.
 The results are retrieved by the user using `dut.rx_logs()` under the following form:

* 'global' results

```python
>>> dut.rx_logs('global')
frames   588  errors   116  PER 1.973e-01  Throughput    78  deltaT 10000057  loops    10  start_us 2245737  last_us 12245794
```

* results for a selected modcode:

```python
>>> dut.rx_logs('24M')
frames    76  errors    48  PER 6.316e-01  RSSI   -79  SNR     7  CFO   -18
```

* all results

```python
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

```c++
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

**pds_compress.py** is a copy of the pds_compress tool used to compress the PDS data
 (the one sent right after FW download) with the added `.py` extension, such that it can be loaded as a Python3 module. It is much faster to load this module once and for all than calling it from the OS every time test data needs to be 'compressed'.

## wfx_pds_tree module

**wfx_pds_tree.py** manages the Test data in a nested dict

**wfx_pds{}** defines the Test data structure

* `ITEM` names are unique by design (FW constraint)
* `VERSION` defines the mimimal FW version
* `PATH` defines the position of each item in the tree
* `DEFAULT` defines the default value
* `VALUES` lists possible values for each item
* `DOC` contains the documentation relative to each item

### NB: The line order defines in which order sections are to be sent (when sending several sections) as well as in which order items within a section wil be ordered_

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

### PdsTree dependencies

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

### NB: When called with no argument, most functions return the corresponding value(s) of the parameter(s) they control*

### WfXTestTarget dependencies

**wfx_test_dut.py** relies on

* **wfx_test_target.py** to handle the test data and communicate with the DUT

### WfXTestDut API functions

| function                           | usage                                              | function parameters      
|------------------------------------|----------------------------------------------------|--------------------------
| `add_tmp_param`                    | adds a temporary parameter to the tree (for debug purposes) |`version`: min FW<br>`path`: position in tree<br>`key`: name<br>`default`:value|
| `c_tune_xi_xo(xi, xo)`             | set XTAL capacitance (see UG404 for details)       |`xi`: [0-255]<br>`xo`: [0-255] XTAL capacitance
| `c_tune_fix(fix)`                  | configure XTAL imbalance (see UG404 for details)   |`fix`: [0-3] XTAL imbalance configuration
| `channel(ch)`                      | set the test channel                               |`ch`: [1-14]\(channel\) or [2300-2530] MHz
| `fem_pa_max_gain(gain_db)`         | set FEM Power Amplifier max gain in closed loop<br>set FEM Power Amplifier typical gain in open loop |`gain_db`: [0-256]. Max FEM Power Amplifier Gain in dB
| `fem_pa_table(vdet_vs_pout)`       | set or check the FEM PA table                      |`vdet_vs_pout`:<br>'[[\<vdet\>, \<pout\>], ...]': Up to 16 [vdet, pout] pairs<br><br>'open_loop': start open loop mode<br>'closed_loop' start closed loop mode<br>'text': returns series of vdet and pout values, number of points and indicates the current loop mode
| `fem_pa_used(yes_no)`              | activates/de-activates the FEM Power Amplifier     |`yes_no`: ['yes', 'no']<br>**none**: check the current FEM Amplifier state
| `fem_read_digital_gain()`          | Returns WFx digital gain info                      |**none**
| `fem_read_fem_pout()`              | Returns FEM output power estimated by firmware using FEM PA table and Vpdet measured, in dBm                    |**none**
| `fem_read_measure_index()`         | Returns 8 bit counter of Vpdet measurements, refreshed every second|**none**
| `fem_read_pa_slice()`              | Returns WFx PA slice                               |**none**
| `fem_read_target_pout()`           | Returns requested target output power, in dBm      |**none**
| `fem_read_tx_info(match)`          | Returns FEM tx info<br>* WFx digital gain info and PA slice<br>* FEM target output power<br>* voltage measured at WFx VPDET pin<br>* output power estimated by firmware<br>* 8 bit counter of Vpdet measurements refreshed every second|if no parameter, returns the entire text as formatted by the driver<br><br>if `match` is provided, filter on `match`. If match is 'values', return a series of name/value pairs
| `fem_read_vpdet()`                 | Returns voltage measured on VPDET in mV            |**none**
| `read_agent_version()`             | returns Agent version                              |**none**
| `read_driver_version()`            | returns driver version                             |**none**
| `read_fw_version()`                | returns FW version                                 |**none**
| `read_rx_stats()`                  | call `run('wfx_test_agent read_rx_start')` to retrieve the Rx stats |**none**
| `regulatory_mode(reg_mode)`        | applies TX power backoff for the selected region   |`reg_mode`:<br>'[All, FCC, ETSI, JAPAN, Unrestricted]'
| `rx_logs(mode=None)`               | retrieve accumulated python content of Rx stats polling.<br><br>Full table if no 'mode', otherwise only the row matching the 'mode' (logs are available until next `tx_receive()` call) |`mode`: <br>'global'(default if '')<br>'[1, 2, 5.5, 11, 6, 9, 12, 18, 24, 36, 48, 54]M'<br>'MCS[0-7]'
| `rx_receive(mode, frames, sleep_ms, timeout)` | Clear Rx logs and polls Rx stats until it has received the required number of frames(default 1000).|`mode`:<br>'endless': run continuously<br>'global'(default if '')<br>'[1, 2, 5.5, 11, 6, 9, 12, 18, 24, 36, 48, 54]M'<br>'MCS[0-7]'<br>`frames`: Nb of frames to receive before stopping'<br>`sleep_ms`:[(750)]. Polling period. No need to poll too often, the FW updates the table only every second<br>`timeout_s`: max number of seconds to poll (useful if very few frames are received)
| `rx_start()`                       | start Rx test in the DUT                           |**none**
| `rx_stop()`                        | stop Rx test in the DUT and Python3 polling thread |**none**
| `test_conditions()`                | returns DUT/Driver/FW/Tools/Agent versions and DUT connection info |**none**
| `test_ind_period()`                | set the delay between indication messages in Tx and Rx_stats in |`period`: period in ms before 2 status indications
| `tone_freq(offset=None)`           | set CW tone offset                                 |`offset`: offset([-31,31], default 0) in 312.5 kHz steps
| `tone_power(dBm)`                  | set tone power                                     |`dbm`: [TBD]  
| `tone_start(offset=None)`          | start CW tone on current channel                   |`offset`: offset([-31,31], default 0) in 312.5 kHz steps
| `tone_stop()`                      | stop CW tone                                       |**none**
| `tx_backoff(mod, backoff_level)`   | set power backoff for one group of modulations. All other backoff 0.<br>Used during certification testing to find the backoff levels to be set in the production PDS to stay within regulatory power limits|`mode_802_11`:<br>  '[B]\_[1, 2, 5_5, 11]Mbps'<br>'[G]\_[6, 9, 12, 18, 24, 36, 48, 54]Mbps'<br>'[MM, GF]\_MCS[0-7]'<br><br>**Examples**: 'B_1Mbps', 'G_54Mbps', 'GF_MCS5'<br>`backoff_level`: [0:63.75] dB
| `tx_framing(pkt_len, ifs_us)`      | control the frame size (in bytes) and IFS (InterFrame Spacing) |<br>`packet_length_bytes`:[25-4091] Frame size in bytes\(without CRC\)<br>`ifs_us`:[0-255] Interframe spacing in us. 100us is recommended for WFM200 to allow crystal compensation over temperature
| `tx_mode(mode)`                    | select between B (11b), G (11g), MM (11n mixed mode) & GF (11n Greenfield) and set the rate|`mode_802_11`:<br>'[B]\_[1, 2, 5_5, 11]Mbps'<br>'[G]\_[6, 9, 12, 18, 24, 36, 48, 54]Mbps'<br>'[MM, GF]\_MCS[0-7]'<br>**Examples**: 'B_1Mbps', 'G_54Mbps', 'GF_MCS5'
| `tx_power(dBm)`                    | set the maximum output power.<br>NB: use tx_backoff() for certification testing|`dbm`: [TBD]
| `tx_rx_select(tx_ant, rx_ant)`     | select the Tx/Rx antennas                          |`tx_ant`: [1-2] Tx antenna<br>`rx_ant`: [1-2] Rx antenna
| `tx_start(nb_frames)`              | start sending a selected number of frames          |`nb_frames`: [0-65535] or 'continuous'. Nb of frames to send before stopping.<br>0 = 'continuous'
| `tx_stop()`                        | send a burst of 100 frames to complete a previous continuous transmission|**none**

## Printing the current test tree content

| pretty (tabulated)              | single line                     |
|---------------------------------|---------------------------------|
| `print(dut.test_data.pretty())` | `print(dut.test_data.print())`  |

_Nb: the above is only possible if using `dut = WfxTestDut(...)`._

## Certification Testing

RF Tx certification testing of a Wi-Fi product consists in checking that Tx signals are compliant with regulatory
 requirements (power, spurious,..) without using an AP in WLAN mode.

Refer to [Certification Testing](certification.md) for details and an example.

## Advanced features

### Traces

#### Tracing test data settings

use `dut.trace = True` to trace all changes to test data items

#### Tracing dut communication link

use `dut.link.trace = True` to trace all communication with the wfx_test-agent

### Accessing a test parameter if it's not managed by a test function

All parameters (even those not managed by test functions) listed in the
 wfx_test_dut API are still accessible using generic functions:

#### Reading

```python
>>> dut.test_data.wfx_get_list({'NB_FRAME'})
>>> dut.test_data.wfx_get_list({'TEST_MODE','NB_FRAME'})
```

#### Writing (without sending Test data)

```python
>>> dut.test_data.wfx_set_dict({'NB_FRAME':12}, 0)
>>> dut.test_data.wfx_set_dict({'TEST_MODE':'tx_packet','NB_FRAME':12}, 0)
```

#### Writing (sending Test data)

```python
>>> dut.test_data.wfx_set_dict({'NB_FRAME':12}, 1)
>>> dut.test_data.wfx_set_dict({'TEST_MODE':'tx_packet','NB_FRAME':12}, 1)
```

### Adding a temporary test parameter

It is possible to define new parameters and access them using the generic
 `wfx_get_list` / `wfx_set_dict` functions described above.

#### Adding a test parameter

```python
>>> dut.test_data.add_tmp_param('version', 'path', 'key', 'default')
```

adds a (temporary) parameter to the Test structure. This is useful to test FW release candidates in the lab

* **example**

```python
# Creating the params in the tree (Pending FW support for 'z.a.b.x' &  'z.a.b.y'):
>>> dut.test_data.add_tmp_param(pds, '2.0', 'z.a.b', 'x', '10')
>>> dut.test_data.add_tmp_param(pds, '2.0', 'z.a.b', 'y', '25')

# Setting the value and sending Test data:
>>> dut.test_data.wfx_set_dict({'x':15, 'y':32}, 1)
```

# Real-life testing

## Direct on Raspberry PI (without SSH)

Below is an example of testing directly on the Raspberry PI, having the PI as both RF Test Server and DUT

```bash
python3
```

```python
Python 3.4.2 (default, Oct 19 2014, 13:31:11)
[GCC 4.9.1] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from wfx_test_dut import *
/usr/local/lib/python3.4/dist-packages/cryptography/hazmat/bindings/openssl/binding.py:163:
 CryptographyDeprecationWarning: OpenSSL version 1.0.1 is no longer supported by the OpenSSL project, please upgrade. A future version of cryptography will drop support for it.
  utils.CryptographyDeprecationWarning
```

*Disregard the **CryptographyDeprecationWarning** above, since it's related to paramiko dependencies, and dealing with these it out of our scope (as long as it still works)*

```python
>>> dut = WfxTestDut('Local')
Local: Configuring a Direct connection
Local    D>>|  wfx_test_agent read_fw_version
<<D    Local|  2.2.1
```

*The lines with `Local    D>>|` or `<<D    Local|` are write/read traces coming from the connection link.
These can be disabled using `dut.link.trace = False`. They are useful to check/debug the wfx_test_agent behavior.*

```python
Local: fw_version retrieved from HW (2.2.1)
  Info: 'FRONT_END_LOSS_RX_QDB' cannot be supported with FW2.2.1, it has been added in FW2.2.2 (skipped)
```

*The above information tells us that the current FW is 2.2.1. 
In wfx_pds{} the VERSION value for 'FRONT_END_LOSS_RX_QDB' is 2.2.2.
This means that the current FW doesn't support 'FRONT_END_LOSS_RX_QDB', so it's not added to the test_data we will use here, to avoid FW exceptions*

```python
fill_tree has messages:
  Info: 'FRONT_END_LOSS_RX_QDB' cannot be supported with FW2.2.1, it has been added in FW2.2.2 (skipped)
```

*After filling the test_data tree, the code checks for any test data processing message (using `check_pds_warning()`),
 so the message is first printed when it occurs then following this check.*

```python
Local: tree filled for FW2.2.1
```

*Finally, we get a message indicating the FW version used by the test data.*

```python
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

```python
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

```python
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

```python
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

```python
>>> dut.link.trace = False
>>> print(dut.run('dmesg | tail -n 5'))
[943517.134836] wfx_wlan: TX packet test ongoing...
[943518.134831] wfx_wlan: TX packet test ongoing...
[943518.170225] wfx_wlan: End of TX packet test
[943518.171552] wfx_wlan: Start TX packet test feature
[943518.212839] wfx_wlan: End of TX packet test
>>>
```

*Here we stop the link trace to avoid too many lines, and we check the content of `dmesg`. We see a 'Start TX' message closely followed by an 'End of TX' message. These 2 correspond to the transmission of 100 frames we triggered to stop transmitting*

```python
>>> quit()
```

*Use `quit()` to stop testing*

## Local on Raspberry PI (via SSH)

```bash
python3
```

```python
Python 3.4.2 (default, Oct 19 2014, 13:31:11)
[GCC 4.9.1] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from wfx_test_dut import *
/usr/local/lib/python3.4/dist-packages/cryptography/hazmat/bindings/openssl/binding.py:163: CryptographyDeprecationWarning: OpenSSL version 1.0.1 is no longer supported by the OpenSSL project, please upgrade. A future version of cryptography will drop support for it.
  utils.CryptographyDeprecationWarning
```

*Disregard the **CryptographyDeprecationWarning** above, since it's related to paramiko dependencies, and dealing with these it out of our scope (as long as it still works)*

```python
>>> dut = WfxTestDut('SSH', host='127.0.0.1', user='pi', password='default_password', port=22)
SSH: Configuring a SSH connection to host 127.0.0.1 for user pi
INFO:root:SSH           I'm connected to 127.0.0.1:22 as pi
```

*Good news: The rest is strictly identical to the **Direct on Raspberry PI (without SSH)** case!*

## Remote on Raspberry PI (via SSH)

### (On Test server)

```bash
 python3
```

```python
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
/usr/local/lib/python3.4/dist-packages/paramiko/kex_ecdh_nist.py:96: 
CryptographyDeprecationWarning: Support for unsafe construction of public numbers from encoded data will be removed in a future version. Please use EllipticCurvePublicKey.from_encoded_point
  self.curve, Q_S_bytes
/usr/local/lib/python3.4/dist-packages/paramiko/kex_ecdh_nist.py:111: CryptographyDeprecationWarning: encode_point has been deprecated on EllipticCurvePublicNumbers and will be removed in a future version. Please use EllipticCurvePublicKey.public_bytes to obtain both compressed and uncompressed point encoding.
  hm.add_string(self.Q_C.public_numbers().encode_point())
```

*Disregard the **CryptographyDeprecationWarning** above, since it's related to paramiko dependencies, and dealing with these it out of our scope (as long as it still works)*

```python
INFO:root:SSH           I'm connected to 10.5.124.186:22 as root
```

*Good news: The rest is strictly identical to the **Direct on Raspberry PI (without SSH)** case!*

## Remote on RTOS (via UART)

### (On Test server)

```bash
python
```

```python
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

```python
Serial   U>>|  wfx_test_agent read_fw_version
<<U   Serial|  2.3.0
Serial: fw_version retrieved from HW (2.3.0)
Serial: tree filled for FW2.3.0
```

*Here we see that we can retrieve the FW version  from the wfx_test_agent. It is used to select which parameters
will be added to the test_data for this DUT. If the fw_version option is not supported by the wfx_test_agent, it can be set adding `, fw_version='<version>'` in the call to `WfxTestDut(...)`. By default, it will otherwise assume that all test data parameters are supported.*

```python
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

### (On Test server)

```bash
python
```

```python
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

```python
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
  Info: 'FRONT_END_LOSS_RX_QDB' cannot be supported with FW2.2.1, it has been added in FW2.2.2 (skipped)

fill_tree has messages:
  Info: 'FRONT_END_LOSS_RX_QDB' cannot be supported with FW2.2.1, it has been added in FW2.2.2 (skipped)

SSH: tree filled for FW2.2.1
SSH      S>>|  wfx_test_agent read_agent_version
<<S      SSH|  1.0.0
SSH pi@10.5.124.186:22 agent_reply: 1.0.0
```

*A SSH DUT has just been configured...*

```python
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

## FEM table controls

Any modification of FEM test conditions shall begin with dut.tx_stop() and end with dut.tx_start('continuous') as shown in the following open loop and closed loop tests of a (26dB typ/28dB max) FEM achieving 23dBm output power in DSSS 1Mbps

### FEM open loop sequence
```python
>>> dut.tx_stop()
'TEST_MODE  tx_packet     NB_FRAME  100'
>>> dut.tx_mode('DSSS_1')
'HT_PARAM  MM     RATE  B_1Mbps'
>>> dut.fem_pa_used('yes')
'PA_USED  yes'
>>> dut.fem_pa_table('open_loop')
'NB_OF_POINTS  0'
>>> dut.fem_pa_max_gain(26)
'MAX_GAIN  104'

>>> dut.tx_power(24)
'MAX_OUTPUT_POWER_QDBM  96     TEST_MODE  tx_packet     NB_FRAME  0'
>>> dut.tx_start('continuous')
'TEST_MODE  tx_packet     NB_FRAME  0'
>>> dut.fem_read_vpdet()
'1080'

>>> dut.tx_stop()
'TEST_MODE  tx_packet     NB_FRAME  100'
>>> dut.tx_power(23)
'MAX_OUTPUT_POWER_QDBM  92     TEST_MODE  tx_packet     NB_FRAME  0'
>>> dut.tx_start('continuous')
'TEST_MODE  tx_packet     NB_FRAME  0'
>>> dut.fem_read_vpdet()
'925'

```

> Note that value of dut.fem_pa_max_gain() should be adjusted (1/4 dB resolution) to ensure that dut.tx_power(value in dBm) expected is indeed measured by Wi-Fi tester at DUT RF output. 

Once table of interpolation points has been measured in open loop, FEM can be controlled in closed loop:

### FEM closed loop sequence
```python
>>> dut.tx_stop()
'TEST_MODE  tx_packet     NB_FRAME  100'
>>> dut.fem_pa_used('yes')
'PA_USED  yes'
>>> dut.fem_pa_table([[1080, 96], [925, 92], [818, 88], [752, 84], [682, 80], [624, 76], [570, 72], [518, 68], [478, 64], [438, 60], [377, 52], [328, 44], [289, 36], [259, 28], [234, 20], [216, 12]])
'VDET_VAL  [1080,925,818,752,682,624,570,518,478,438,377,328,289,259,234,216]\nPOUT_VAL  [96,92,88,84,80,76,72,68,64,60,52,44,36,28,20,12]'
>>> dut.fem_pa_table('closed_loop')
'NB_OF_POINTS  16'
>>> dut.fem_pa_max_gain(28)
'MAX_GAIN  112'

>>> dut.tx_power(24)
'MAX_OUTPUT_POWER_QDBM  96     TEST_MODE  tx_packet     NB_FRAME  0'
>>> dut.tx_start('continuous')
'TEST_MODE  tx_packet     NB_FRAME  0'
>>> dut.fem_read_vpdet()
'1094'
>>> dut.fem_read_fem_pout()
'24.00'

>>> dut.tx_stop()
'TEST_MODE  tx_packet     NB_FRAME  100'
>>> dut.tx_power(23)
'MAX_OUTPUT_POWER_QDBM  92     TEST_MODE  tx_packet     NB_FRAME  0'
>>> dut.tx_start('continuous')
'TEST_MODE  tx_packet     NB_FRAME  0'
>>> dut.fem_read_vpdet()
'932'
>>> dut.fem_read_fem_pout()
'23.00'

```


## [RF Test Hierarchy](#hierarchy)

```text
                           --------------------------------------------------------
                                                                                  |
  ----------------------                                                          |
  | customer_test.py   |                                                          |
  ----------------------                                                          |
            |                                                                     |
           \|/                                                                    |
  ----------------------                                                          |
  | serverPI_UDP.py    |                                                          |
  ----------------------                                                          | Running
            |                                                                     |   on
           \|/                                                                    | Tester
  ----------------------                                                          |
  | wfx_test_dut.py    |                                                          |
  ----------------------                                                          |
            |                                                                     |
            |------------------------|                                            |
           \|/                      \|/                                           |
  ----------------------   ------------------------                               |
  | wfx_test_target.py |   |      job.py          |                               |
  ----------------------   ------------------------                               |
            |                                                                     |
            |------------------------|---------------------------|                |
           \|/                      \|/                         \|/               |
  ----------------------   ------------------------   -------------------------   |
  | wfx_connection.py  |   | pds_compress.py      |   | wfx_pds_tree.py       |   |
  ----------------------   ------------------------   -------------------------   |
           /|\                                                                    |
            |              --------------------------------------------------------
            |
            | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . UART or SSH connection
            |
            |              --------------------------------------------------------
           \|/                                                                    |
  ----------------------                                                          | Running
  | wfx_test_agent.py  |                                                          |   on
  ----------------------                                                          |  DUT(s)
                                                                                  |
                           --------------------------------------------------------
```

--------------------------------

Links:

* [wfx-linux-tools repository 'test-feature' folder][LIN_REPO_RF]
* [wfx-fullMAC-tools repository 'RF_test_agent' folder][FMAC_REPO_RF]
* [wfx-fullMAC-tools repository 'RF_test_agent' folder (for Simplicity Studio v4)][FMAC_REPO_RF_SSv4]
* [wfx-common-tools repository][COM_REPO]
  * [wfx-common-tools repository 'connection' folder][COM_REPO_CONN]
    * [connection README][CONN_DOC]
  * [wfx-common-tools repository 'test-feature' folder][COM_REPO_RF]

[LIN_REPO_RF]: https://github.com/SiliconLabs/wfx-linux-tools/tree/master/test-feature
[FMAC_REPO_RF]: https://github.com/SiliconLabs/wfx-fullMAC-tools/tree/main/wifi_cli_micriumos/rf_test_agent
[FMAC_REPO_RF_SSv4]: https://github.com/SiliconLabs/wfx-fullMAC-tools/tree/wifi_examples_ssv4/Tools/RF_test_agent
[COM_REPO]: https://github.com/SiliconLabs/wfx-common-tools
[COM_REPO_CONN]: https://github.com/SiliconLabs/wfx-common-tools/tree/master/connection
[CONN_DOC]: https://github.com/SiliconLabs/wfx-common-tools/blob/master/connection/README.md
[COM_REPO_RF]: https://github.com/SiliconLabs/wfx-common-tools/tree/master/test-feature
