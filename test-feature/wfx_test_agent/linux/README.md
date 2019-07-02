# WFX Test Agent (Linux)
*wfx_test_agent* is an executable which needs to be available on the DUT to allow RF Testing using
 Python3 scripts provided at https://github.com/SiliconLabs/wfx-common-tools/tree/master/test-feature

## WXF Test Agent installation
The Linux `wfx_test_agent` is a bash script with execution permission which should be directly applicable
 to any Linux platform.

* Create a link from `/usr/local/bin/wfx_test_agent` to the script
* Make sure it has execution rights

## WXF Test Agent testing
*The wfx_test_agent can be tested & validated stand-alone before being used for RF Testing:*
* On Linux platforms, call `wfx_test_agent <option>` to test all options
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

*The wfx-linux-driver used on Linux platforms already performs this formatting (inside wfx_rx_stats_show()), 
 and copies it to `/sys/kernel/debug/ieee80211/phy*/wfx/rx_stats`, so the wfx_test_agent only needs to echo
 this content*

Others are **only useful to log test conditions** ('nice to have'):

* `read_agent_version` (returns '1.0.0' at the time os writing)
* `read_driver_version` (returns '2.0.3' at the time os writing)
* `read_fw_version` (returns '2.2.1' at the time os writing)
