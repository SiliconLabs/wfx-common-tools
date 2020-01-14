# PTA (Packet Traffic Arbitration) python scripts

PTA is used to manage radio coexistence of Wi-Fi with other standards

Common use cases are:

* Wi-Fi + Bluetooth
* Wi-Fi + Zigbee

(Watch <https://www.youtube.com/watch?v=BiEe_EbhpGg> to discover the benefits of PTA and
visit <https://www.silabs.com/products/wireless/learning-center/wi-fi-coexistence> for more details)

## Usage

To manage PTA, sending configuration data is required to

* Provide the PTA settings to the WFX firmware
* Control the PTA priority
* Turn PTA on/off

## Source repository

<https://github.com/SiliconLabs/wfx-common-tools>

## Python version

The scripts have been written for and tested for Python3 

## Installation

These scripts are used to format PTA bytes according to the user's preferences and send them to the WFX firmware.

They can be used either directly on the target or on a remote tester, via the **WFX connection layer**

### Prerequisites

First install the  **WFX connection layer**
The connection layer is the same as the one used for WFX RF testing, allowing connection in the following modes:

* Local
* SSH
* UART
* Telnet

The connection layer is available in
<https://github.com/SiliconLabs/wfx-common-tools/tree/master/connection>
(a subfolder of `wfx-common-tools`, so from the PTA scripts perspective they are under `../connection`)

Refer to
<https://github.com/SiliconLabs/wfx-common-tools/blob/master/connection/README.md>
 for details on the connection layer and its installation.

----------------

### PTA scripts installation

Once you have installed the **WFX connection layer** you will also have installed the Python scripts for PTA, since
these are in the same repository, in the `pta` folder.

```bash
cd siliconlabs/wfx-common-tools/pta
```

----------------

### PTA help

Help can be obtained using the `pta_help()` function, and will also be displayed in case a function parameter
 is missing or invalid.

```bash
python3
```

```python
>>> from wfx_pta import *
>>> dut = WfxPtaTarget('local')
>>> dut.pta_help()
```

#### PTA help content

```text
usage: wfx_pta_data.py [-h] [--version]
                       [--config {1w_wlan_master_example,1w_coex_master_example,2w_example,3w_example,4w_example}]
                       [--pta_mode {1w_wlan_master,1w_coex_master,2w,3w,4w}]
                       [--request_signal_active_level {low,high}]
                       [--priority_signal_active_level {low,high}]
                       [--freq_signal_active_level {low,high}]
                       [--grant_signal_active_level {low,high}]
                       [--coex_type {generic,ble}]
                       [--default_grant_state {no_grant,grant}]
                       [--simultaneous_rx_accesses {false,true}]
                       [--priority_sampling_time PRIORITY_SAMPLING_TIME]
                       [--tx_rx_sampling_time TX_RX_SAMPLING_TIME]
                       [--freq_sampling_time FREQ_SAMPLING_TIME]
                       [--grant_valid_time GRANT_VALID_TIME]
                       [--fem_control_time FEM_CONTROL_TIME]
                       [--first_slot_time FIRST_SLOT_TIME]
                       [--periodic_tx_rx_sampling_time PERIODIC_TX_RX_SAMPLING_TIME]
                       [--coex_quota COEX_QUOTA]
                       [--wlan_quota WLAN_QUOTA]
                       [--priority_mode {coex_maximized,coex_high,balanced,wlan_high,wlan_maximized}]
                       [--coex_priority_low COEX_PRIORITY_LOW]
                       [--reserved1 RESERVED1]
                       [--coex_priority_high COEX_PRIORITY_HIGH]
                       [--reserved2 RESERVED2]
                       [--grant_coex GRANT_COEX]
                       [--grant_wlan GRANT_WLAN]
                       [--protect_coex PROTECT_COEX]
                       [--protect_wlan_tx PROTECT_WLAN_TX]
                       [--protect_wlan_rx PROTECT_WLAN_RX]
                       [--reserved3 RESERVED3]
                       [--state {off,on}]
                       {settings,priority,state}

        Prepare and send PTA parameters depending on the selected pta_cmd


positional arguments:
  {settings,priority,state}
                        pta_cmd <settings/priority/state>

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

settings:
  --config {1w_wlan_master_example,1w_coex_master_example,2w_example,3w_example,4w_example}
                        Preset configurations for common use cases examples
                        (These presets can be used as start points and be
                        overwritten using options listed below to fine-tune
                        specific options)
  --pta_mode {1w_wlan_master,1w_coex_master,2w,3w,4w}
                        PTA mode selection (default 1w_wlan_master)
  --request_signal_active_level {low,high}
                        (input) Active level on REQUEST signal, provided by
                        Coex to request the RF (default low)
  --priority_signal_active_level {low,high}
                        (input) Active level on PRIORITY signal, provided by
                        Coex to set the priority of the request (default low)
  --freq_signal_active_level {low,high}
                        (input) Active level on FREQ signal, provided by Coex
                        in 4-wire mode when Coex and Wlan share the same band
                        (default low)
  --grant_signal_active_level {low,high}
                        (output) Active level on grant signal, generated by
                        PTA to grant the RF to Coex (default low)
  --coex_type {generic,ble}
                        Coex type (default generic)
  --default_grant_state {no_grant,grant}
                        State of the grant signal before arbitration at
                        grant_valid_time (default no_grant)
  --simultaneous_rx_accesses {false,true}
                        (uint8), Boolean to allow both Coex and Wlan to
                        receive concurrently, also named combined mode
                        (default false)
  --priority_sampling_time PRIORITY_SAMPLING_TIME
                        (uint8), Time in microseconds from the Coex request to
                        the sampling of the priority on PRIORITY signal (1 to
                        31), (default 0)
  --tx_rx_sampling_time TX_RX_SAMPLING_TIME
                        (uint8), Time in microseconds from the Coex request to
                        the sampling of the directionality on PRIORITY signal
                        (priority_sampling_time to 63) (default 0)
  --freq_sampling_time FREQ_SAMPLING_TIME
                        (uint8), Time in microseconds from the Coex request to
                        the sampling of the freq-match information on FREQ
                        signal (1 to 127) (default 0)
  --grant_valid_time GRANT_VALID_TIME
                        (uint8), Time in microseconds from Coex request to the
                        grant signal assertion (max(tx_rx_sampling_time,
                        freq_sampling_time), to 0xFF), (default 0)
  --fem_control_time FEM_CONTROL_TIME
                        (uint8), Time in microseconds from Coex request to the
                        control of FEM (grant_valid_time to 0xFF), (default 0)
  --first_slot_time FIRST_SLOT_TIME
                        (uint8), Time in microseconds from the Coex request to
                        the beginning of reception or transmission
                        (grant_valid_time to 0xFF), (default 0)
  --periodic_tx_rx_sampling_time PERIODIC_TX_RX_SAMPLING_TIME
                        (uint16), Period in microseconds from first_slot_time
                        of following samplings of the directionality on
                        PRIORITY signal (1 to 1023), (default 0)
  --coex_quota COEX_QUOTA
                        (uint16), Duration in microseconds for which RF is
                        granted to Coex before it is moved to Wlan (default 0)
  --wlan_quota WLAN_QUOTA
                        (uint16), Duration in microseconds for which RF is
                        granted to Wlan before it is moved to Coex (default 0)

priority:
  --priority_mode {coex_maximized,coex_high,balanced,wlan_high,wlan_maximized}
                        coex_maximized = 0x00000562 : Maximizes priority to
                        COEX, WLAN connection is not ensured. coex_high =
                        0x00000462 : High priority to COEX, targets low-
                        latency to COEX. balanced = 0x00001461 : Balanced PTA
                        arbitration, WLAN acknowledge receptions are
                        protected. wlan_high = 0x00001851 : High priority to
                        WLAN, protects WLAN transmissions. wlan_maximized =
                        0x00001A51 : Maximizes priority to WLAN
  --coex_priority_low COEX_PRIORITY_LOW
                        Priority given to Coex for low-priority requests
                        (default 0)
  --reserved1 RESERVED1
                        Reserved for future use (default 0)
  --coex_priority_high COEX_PRIORITY_HIGH
                        Priority given to Coex for high-priority requests
                        (default 0)
  --reserved2 RESERVED2
                        Reserved for future use (default 0)
  --grant_coex GRANT_COEX
                        Allows Coex to override Wlan (default 0)
  --grant_wlan GRANT_WLAN
                        Allows Wlan to override Coex whenever Wlan is not idle
                        (default 0)
  --protect_coex PROTECT_COEX
                        Wlan grant is delayed until Coex has finished its
                        present granted transaction (default 0)
  --protect_wlan_tx PROTECT_WLAN_TX
                        Prevents Coex from being granted when Wlan is
                        transmitting (the protection is also extended to the
                        response) (default 0)
  --protect_wlan_rx PROTECT_WLAN_RX
                        Prevents Coex from being granted when Wlan is
                        receiving or waiting for a response to an already
                        transmitted frame (default 0)
  --reserved3 RESERVED3
                        Reserved for future use (default 0)

state:
  --state {off,on}      PTA state on/off

        Examples:

        Python3 interpreter:
        python3
         >>> from wfx_pta import *
        selecting the connection mode to match your DUT:
         >>> dut = WfxPtaTarget('Pi203', host='pi203', user='pi', port=22, password='default_password')
         >>> dut = WfxPtaTarget('Serial', port='COM8')
         >>> dut = WfxPtaTarget('Local')
         selecting settings, priority and activating PTA:
         >>> dut.settings('--config 3w_ble --first_slot_time 123')
         >>> dut.priority('--priority_mode balanced')
         >>> dut.state('--state on')
         activating PTA traces (tracks PTA data values):
         >>> dut.trace = True
         activating communication link traces (tracks bytes write/read):
         >>> dut.link.trace = True

        Command line using 'wfx_pta.py': directly sending PTA bytes to a 'Local' DUT:
         (bytes silently sent to DUT)
           python wfx_pta.py settings --config 3w_example
           python wfx_pta.py priority --priority_mode balanced
           python wfx_pta.py state --state on
         (verbose mode)
           python wfx_pta.py settings --config 3w_example verbose
            Local: configuring a Direct connection
            ['settings', '--config', '3w_example']
            configuring for 3w_example
            pta_mode                       1w_wlan_master =>       3w
            request_signal_active_level         low =>     high
            priority_signal_active_level        low =>     high
            default_grant_state            no_grant =>    grant
            priority_sampling_time                0 =>       10
            grant_valid_time                      0 =>       72
            fem_control_time                      0 =>      140
            pta_mode                       3w         
            request_signal_active_level    high       
            priority_signal_active_level   high       
            freq_signal_active_level       low
            grant_signal_active_level      low
            coex_type                      generic
            default_grant_state            grant      
            simultaneous_rx_accesses       false
            priority_sampling_time         10

            tx_rx_sampling_time            0
            freq_sampling_time             0
            grant_valid_time               72         H
            fem_control_time               140        
            first_slot_time                0
            periodic_tx_rx_sampling_time   0
            coex_quota                     0
            wlan_quota                     0
            Local    D>>|  wfx_exec wfx_hif_send_msg "\x18\x00\x2b\x00\x03\x01\x01\x00\x00\x00\x01\x00\x0a\x00\x00\x48\x8c\x00\x00\x00\x00\x00\x00\x00"
            Local    D<<|  0

        Command line using 'wfx_pta_data.py': retrieving the PTA bytes (no byte sent to HW):
          python wfx_pta_data.py settings --config 3w_example
            \x18\x00\x2b\x00\x03\x01\x01\x00\x00\x00\x01\x00\x0a\x00\x00\x48\x8c\x00\x00\x00\x00\x00\x00\x00
          python wfx_pta_data.py settings --config 3w_example --grant_valid_time 40 --priority_sampling_time 8
            \x18\x00\x2b\x00\x03\x01\x01\x00\x00\x00\x01\x00\x08\x00\x00\x28\x8c\x00\x00\x00\x00\x00\x00\x00
          python wfx_pta_data.py priority --priority_mode balanced
             , a
          python wfx_pta_data.py priority --coex_priority_low 1 --coex_priority_high 5 --grant_wlan 1 --protect_wlan_tx 1 --protect_wlan_rx 1
             , Q
          python wfx_pta_data.py state --state on
            \x08\x00\x2d\x00\x01\x00\x00\x00
          python wfx_pta_data.py state --state off
            \x08\x00\x2d\x00\x00\x00\x00\x00
```

## PTA API

### settings(options)

PTA settings are filled based on the `options` string as a structure with the following parameters

| settings parameter          | Possible values                      | unit |
|-----------------------------|--------------------------------------|------|
| pta_mode                    |1w_wlan_master,1w_coex_master,2w,3w,4w|      |
| request_signal_active_level |low,high                              |      |
| priority_signal_active_level|low,high                              |      |
| freq_signal_active_level    |low,high                              |      |
| grant_signal_active_level   |low,high                              |      |
| coex_type                   |generic,ble                           |      |
| default_grant_state         |no_grant,grant                        |      |
| simultaneous_rx_accesses    |false,true                            |      |
| priority_sampling_time      |1 to 31                               | us   |
| tx_rx_sampling_time         |1 to 50                               | us   |
| freq_sampling_time          |1 to 127                              | us   |
| grant_valid_time            |int                                   | us   |
| fem_control_time            |int                                   | us   |
| first_slot_time             |int                                   | us   |
| periodic_tx_rx_sampling_time|1 to 1023                             | us   |
| coex_quota                  |int                                   | us   |
| wlan_quota                  |int                                   | us   |

* Each parameter can be set using the `--<parameter>=<value>` syntax
* No specific order for parameters provided in the `options` string
* All parameters are optional
* Parameters not listed will be set to 0

#### PTA setting pre-filled configurations

Typical pre-filled configurations (matching common use cases) can be selected using an additional `config` parameter:

| '--config=<pre_filled_config>'| pta_mode     | signals used                 | options set             |
|-------------------------------|--------------|------------------------------|-------------------------|
| 1w_wlan_master_example        |1w_wlan_master|GRANT                         |wlan_quota <br>coex_quota|
| 1w_coex_master_example        |1w_coex_master|REQUEST                       |                         |
| 2w_example                    |2w            |GRANT, REQUEST                |                         |
| 3w_example                    |3w            |GRANT, REQUEST, PRIORITY      |coex_type <br> simultaneous_rx_accesses <br> priority_sampling_time <br>grant_valid_time <br>fem_control_time|
| 4w_example                    |4w            |GRANT, REQUEST, PRIORITY, FREQ|coex_type <br> simultaneous_rx_accesses <br> priority_sampling_time <br>tx_rx_sampling_time <br>freq_sampling_time <br>grant_valid_time <br>fem_control_time <br>first_slot_time <br>periodic_tx_rx_sampling_time|

#### PTA settings defaults vs pre-filled configurations vs user options

**PTA settings** are applied in the following order:

* All defaults
* Pre-filled configuration options values
* User options

NB: Using the PTA data filling tracing (described below) can be a good way to become familiar with this process

### priority (options)

PTA priority options are filled based on the `options` string as a structure with the following parameters

| priority parameter          | Possible values    |
|-----------------------------|--------------------|
| coex_priority_low           |0 to 7              |
| coex_priority_high          |0 to 7              |
| grant_coex                  |0, 1                |
| grant_wlan                  |0, 1                |
| protect_coex                |0, 1                |
| protect_wlan_tx             |0, 1                |
| protect_wlan_rx             |0, 1                |

* Each parameter can be set using the `--<parameter>=<value>` syntax
* No specific order for parameters provided in the `options` string
* All parameters are optional
* Parameters not listed will be set to 0

#### PTA priority pre-filled configurations

Typical pre-filled configurations (matching common use cases) can be selected using an additional `priority_mode` parameter:

| '--priority_mode=<pre_filled_config>'| coex_prio_low | coex_prio_high | grant_coex | grant_wlan | protect_coex | protect_wlan_tx | protect_wlan_rx |
|--------------------------------------|---------------|----------------|------------|------------|--------------|-----------------|-----------------|
| coex_maximized                       | 2             | 6              | 1          | 0          | 1            | 0               | 0               |
| coex_high                            | 1             | 6              | 0          | 0          | 1            | 0               | 0               |
| balanced                             | 1             | 5              | 0          | 0          | 1            | 0               | 1               |
| wlan_high                            | 1             | 5              | 0          | 0          | 0            | 1               | 1               |
| wlan_maximized                       | 1             | 5              | 0          | 1          | 0            | 1               | 1               |


## Use case 1: from a Python3 interpreter

```bash
python3
```

```python
>>> from wfx_pta import *
```

### Connection

Select one of (with your own parameters for the SSH or UART cases)

```python
>>> dut = WfxPtaTarget('Pi203', host='pi203', user='pi', port=22, password='default_password')
>>> dut = WfxPtaTarget('Serial', port='COM8')
>>> dut = WfxPtaTarget('Local')
```

### PTA settings

**All defaults + pta_mode & tx_rx_sampling_time**

```python
>>> dut.settings('--pta_mode 3w --tx_rx_sampling_time 30')
```

**Pre-filled configuration 'as is'**

```python
>>> dut.settings('--config 3w_example')
```

**Pre-filled configuration + user-selected values**

```python
>>> dut.settings('--config 3w_example --first_slot_time 123')
```

### PTA priority

```python
>>> dut.priority('--priority_mode balanced')
```

**Pre-filled configuration + user-selected values**

```python
>>> dut.settings('--priority_mode balanced --coex_priority_high 4')
```

### PTA state

```python
>>> dut.state('--state off')
```

### Tracing

#### Tracing PTA data filling

Adding `mode='verbose'` to a PTA function call will enable tracing of the PTA data filling process

**without traces**

```python
>>> dut.settings('--config 3w_ble')
'HI_STATUS_SUCCESS'
```

**with traces**

```python
>>> dut.settings('--config 3w_example --fem_control_time 135', mode='verbose')
['settings', '--config', '3w_example', '--fem_control_time', '135']
configuring for 3w_example
pta_mode                       1w_wlan_master =>       3w
request_signal_active_level         low =>     high
priority_signal_active_level        low =>     high
default_grant_state            no_grant =>    grant
priority_sampling_time                0 =>       10
grant_valid_time                      0 =>       72
fem_control_time                      0 =>      140
fem_control_time                    140 ->      135
pta_mode                       3w         \x03
request_signal_active_level    high       \x01
priority_signal_active_level   high       \x01
freq_signal_active_level       low        \x00
grant_signal_active_level      low        \x00
coex_type                      generic    \x00
default_grant_state            grant      \x01
simultaneous_rx_accesses       false      \x00
priority_sampling_time         10         \x0a
tx_rx_sampling_time            0          \x00
freq_sampling_time             0          \x00
grant_valid_time               72         \x48
fem_control_time               135        \x87
first_slot_time                0          \x00
periodic_tx_rx_sampling_time   0          \x00\x00
coex_quota                     0          \x00\x00
wlan_quota                     0          \x00\x00
'HI_STATUS_SUCCESS'
>>>
```

NB: Above we can see

* Indicated with `=>`: the changes done on the defaults when applying '3w_example'
* Indicated with `->`: the changes done on the current settings when applying '--fem_control_time 135'
* When there is a change from the default: the default values on the left side, the final value on the right

#### Tracing PTA data transmission

It is also possible to track the connection layer communication with the DUT, using

```python
>>> dut.link.trace = True
```

**without connection traces**

```python
>>> dut.settings('--config 3w_example')
'HI_STATUS_SUCCESS'
```

**with connection traces**

```python
>>> dut.settings('--config 3w_example')
pi       D>>|  wfx_exec wfx_hif_send_msg "\x18\x00\x2b\x00\x03\x01\x01\x00\x00\x00\x01\x00\x0a\x00\x00\x48\x8c\x00\x00\x00\x00\x00\x00\x00"
<<D       pi|  0
'HI_STATUS_SUCCESS'
```

## Use case 2: command line to retrieve PTA formatted data

### settings

```bash
python wfx_pta.py settings --config 3w_example
```

### priority

```bash
python wfx_pta.py priority --priority_mode balanced
```

### state

```bash
python wfx_pta.py state --state on
```

### tracing

add 'verbose' to the command to trace PTA data filling

```bash
python wfx_pta.py settings --config 3w_example verbose
```

## Use case 3: command line to directly send PTA data

### settings

```bash
python wfx_pta_data.py settings --config 3w_example --grant_valid_time 40 --priority_sampling_time 8
```

### priority

```bash
python wfx_pta_data.py priority --priority_mode balanced
```

### state

```bash
python wfx_pta_data.py state --state on
```

# Self test

A specific set of `command_line_test/selftest` functions has been added to allow testing proper installation of the tools.
`command_line_test/selftest` calls the 3 PTA functions will valid example values to check that PTA data formatting and transmission
 is working as expected. To achieve this, internal tracing features are used.

## Running the self test

```bash
python3 wfx_pta_data.py
```

## Expected result of dut.selftest():

```text
['settings', '--config', '3w_ble', '--request_signal_active_level', 'low', '--first_slot_time', '123']
configuring for 3w_example
pta_mode                       1w_wlan_master =>       3w
request_signal_active_level         low =>     high
priority_signal_active_level        low =>     high
default_grant_state            no_grant =>    grant
priority_sampling_time                0 =>       10
grant_valid_time                      0 =>       72
fem_control_time                      0 =>      140
first_slot_time                       0 ->      123
pta_mode                       3w         \x03
request_signal_active_level    high       \x01
priority_signal_active_level   high       \x01
freq_signal_active_level       low        \x00
grant_signal_active_level      low        \x00
coex_type                      generic    \x00
default_grant_state            grant      \x01
simultaneous_rx_accesses       false      \x00
priority_sampling_time         10         \x0a
tx_rx_sampling_time            0          \x00
freq_sampling_time             0          \x00
grant_valid_time               72         \x48
fem_control_time               140        \x8c
first_slot_time                123        \x7b
periodic_tx_rx_sampling_time   0          \x00\x00
coex_quota                     0          \x00\x00
wlan_quota                     0          \x00\x00
\x18\x00\x2b\x00\x03\x01\x01\x00\x00\x00\x01\x00\x0a\x00\x00\x48\x8c\x7b\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x09\x00\x00\x00\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe8\x03\x00\x00
\x18\x00\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd2\x04
\x08\x00\x2d\x00\x00\x00\x00\x00
\x08\x00\x2d\x00\x01\x00\x00\x00
\x08\x00\x2c\x00\x62\x05\x00\x00
\x08\x00\x2c\x00\x62\x04\x00\x00
\x08\x00\x2c\x00\x61\x14\x00\x00
\x08\x00\x2c\x00\x51\x18\x00\x00
\x08\x00\x2c\x00\x51\x1a\x00\x00
\x08\x00\x2c\x00\x07\x00\x00\x00
\x08\x00\x2c\x00\x70\x00\x00\x00
\x08\x00\x2c\x00\x00\x01\x00\x00
\x08\x00\x2c\x00\x00\x02\x00\x00
\x08\x00\x2c\x00\x00\x04\x00\x00
\x08\x00\x2c\x00\x00\x08\x00\x00
\x08\x00\x2c\x00\x00\x10\x00\x00

```
