# WFX Test Agent (Bare Metal)
*wfx_test_agent* is an executable which needs to be available on the DUT to allow RF Testing using
 Python3 scripts provided at https://github.com/SiliconLabs/wfx-common-tools/tree/master/test-feature

## WXF Test Agent installation
The Bare Metal `wfx_test_agent` is provided for a given MCU.

* Compile the sources as an executable named `wfx_test_agent`
* If required, adapt the code to support the features listed below in your setup.

## WXF Test Agent testing
*The wfx_test_agent can be tested & validated stand-alone before being used for RF Testing:*
* On platforms with SSH access, connect to the DUT and call `wfx_test_agent <option>` to test all options
* On platforms accessible via UART, open a terminal and call `wfx_test_agent <option>` to test all options

## WFX Test Agent features/options
Some DUT wfx_test_agent features are **mandatory for RF Testing**:

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

Others are **only useful to log test conditions** ('nice to have'):

* `read_agent_version` (returns '1.0.0' at the time os writing)
* `read_driver_version` (returns '2.0.3' at the time os writing)
* `read_fw_version` (returns '2.2.1' at the time os writing)
