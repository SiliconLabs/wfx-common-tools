<p align="center">
    <img src="silabs_logo.png" height=100px>
    <img src="wi-fi-blue-circle-icon.jpg" height=100px>
</P>

---

# Silicon Laboratories WFx Wi-Fi tools for all supported platforms

## Related Parts

* [WF200](https://www.silabs.com/products/wireless/wi-fi/wf200-series-2-wi-fi-transceiver-socs/device.wf200)
* [WF200S](https://www.silabs.com/products/wireless/wi-fi/wf200-series-2-wi-fi-transceiver-socs/device.wf200s)
* [WFM200](https://www.silabs.com/products/wireless/wi-fi/wf200-series-2-wi-fi-transceiver-modules)
* [WGM160P](https://www.silabs.com/products/wireless/wi-fi/wgm160-series-1-wi-fi-modules)

Select the proper Wi-Fi product for your application from [here](https://www.silabs.com/products/wireless/wi-fi).

Read the documentation on [docs.silabs.com](https://docs.silabs.com/wifi/wf200/content-source/getting-started/linux/getting-started#raspberry-pi--raspbian-wifi-lower-mac-driver-example)

---

## Support

Please use the [Silicon Labs Support Portal](https://www.silabs.com/support/)
for all support requests.

[WF200]: https://www.silabs.com/products/wireless/wi-fi/wf200-series-2-wi-fi-transceiver-socs/device.wf200

---

# wfx-common-tools

This repository contains WFX tools which are not platform-specific,
 and can be used on several platforms.

## Installation

**The tools is tested with Python 3.13.3**

It would be a best practice to install packages in a virtual environment using pip & venv for different projects as the guideline [here](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/). 

Basically, some basic steps as the following commands:

```bash
$ mkdir -p my_project && cd my_project
$ python -m venv my_env
$ source my_env/bin/activate

# For development setup
$ pip install -r requirements.txt
```

### Installing the package from PyPI (Stable version)

Still under the "my_project" from the above commands:

```bash
$ pip install wfx-common-tools
$ pip list # see a list of just installed packages
```
### Installing the package from Github repository (Latest version)

You also can install the package from this repo to test the latest code.

```bash
$ pip install wfx_common_tools@git+https://github.com/SiliconLabs/wfx-common-tools.git
```

## Typical Usage

After installing "wfx_common_tools" package, we can import the library into our script as below:

See [README of connection package][3] for SSH connection setup.

```python 
# Using the "test_feature" package
from wfx_common_tools.test_feature import wfx_test_dut

# Control the DUT via SSH connection by using "root" user & authentication by SSH keys (not using the password)
dut = wfx_test_dut.WfxTestDut('Pi_111', host='192.168.2.111', user='pi', password='default_password', port=22)
dut.test_conditions()
```

## Usage with test.py

```shell
$ source my_env/bin/activate

# By serial port selection
$ (my_env) python -i test.py
# By given serial port
$ (my_env) python -i test.py --port <port>

>> help() # Print help
```

This `test.py` script will add some helper function to ease TX tone/CW mode setup.
If no port is given with `--port <port>` in the script call, a prompt will permit to select one's of avaiable serial port.
Ex:
```shell
>(my_env) python -i test.py
Available serial ports:
[0] /dev/cu.wlan-debug - n/a
[1] /dev/cu.debug-console - n/a
[2] /dev/cu.Bluetooth-Incoming-Port - n/a
[3] /dev/cu.usbserial-FT5RQIQL - TTL232RG-VSW3V3
[4] /dev/cu.usbmodemD34F056C81B54 - PPK2
[5] /dev/cu.usbmodemD34F056C81B52 - PPK2
[6] /dev/cu.usbserial-1410 - CP2102N USB to UART Bridge Controller
Select a port by number: 3
Using serial port: /dev/cu.usbserial-FT5RQsIQL
```
Once a port is selected, the script will set the board to handle RF agent.
A message `RF agent ready...` will be prompted when it is ready.

It adds below functions:
- `tone(channel, freq_offset=0, dbm=None)`: Start a TX Tone on the given channel
  - `channel`: Mandatory, WIFI channel. Range [1;14].
  - `freq_offset`: Optionnal, Frequency offset. Step of 312.5 KHz. Range [-31;31]. Default = 0 dBm
  - `dbm`: Optionnal, TX Power for the tone in dbm. Float (ex: 10.0) or None. In case of None, it will use ``
  - Examples:
  ```python
    tone(1) # Run a tone on the channel 1, No offset, Default TX Power
    tone(6, 10, 10.0) # Run a tone on the channel 6 + 10 * 312.5 Khz, Tx power set to 10.0 dBm
  ```
- `modulation(regulatory_mode, channel, tx_mode, tx_power_reduction=0.0, tx_framing=1500)`: Start a CW Mode
  - `regulatory_mode` : Mandatory, applies TX power backoff for the selected region. Values: 'All', 'FCC', 'ETSI', 'JAPAN', 'Unrestricted'
  - `channel` : Mandatory, Wifi channel. Range [1;14]
  - `tx_mode` : Mandotory, Select between B (11b), G (11g), MM (11n mixed mode) & GF (11n Greenfield) and set the rate. Values: `mode_802_11`:<br>'[B]\_[1, 2, 5_5, 11]Mbps'<br>'[G]\_[6, 9, 12, 18, 24, 36, 48, 54]Mbps'<br>'[MM, GF]\_MCS[0-7]'<br>**Examples**: 'B_1Mbps', 'G_54Mbps', 'GF_MCS5'
    - `B_`
  - `tx_power_reduction`: Optionnal, TX power reduction (in dBm). Step of 0.25 dBm.
  - `tx_framing`: Optionnal, Control the frame size (in bytes)
  - Examples:
  ```python
  modulation("ETSI", 1, "B_1Mbps")  # CW mode, ETSI, Channel 1 and B_1Mbps
  modulation("FCC", 6, "G_12Mbps", tx_power_reduction=5.0)  # CW mode, FCC, Channel 6, B_1Mbps and power reduction of 5.0 dBm
  ```
- `wait()` : Wait a CTRL+C escape before continuing.
- `help()` : Print help.
- `quit()` : Quit Python terminal.

For functions are available. Complete documentations are available in these below links:
- [List of `dut` functions](https://github.com/SiliconLabs/wfx-common-tools/blob/master/src/wfx_common_tools/test_feature/README.md#wfxtestdut-api-functions)
- [Certifications process](https://github.com/SiliconLabs/wfx-common-tools/blob/master/src/wfx_common_tools/test_feature/certification.md)

**Note**
When running commands, please check the `UART received` fields and particullary the message of `UART received <Send PDS OK>`.
If an error occured, the message will be `UART received <Send PDS error>`

## Repository Sub-Packages

Typically, Python resources can be used to run tests on WFX devices, and such tools can be running on any
 Python-capable platform.

| Packages       | Usage                                                                                                       | Documentation |
|--------------|-------------------------------------------------------------------------------------------------------------|---------------|
| connection   | Python communication resources imported from other tools, accessed using `from wfx_common_tools.connection import *` | [README][3]   |
| pta          | Python scripts for PTA (Packet Traffic Arbitration), when several radio standards use shared RF resources   | [README][4]   |
| test_feature | Pythons scripts used to test the RF performance tests <br><br>NB: Prior to running RF testing, make sure you must stop any WLAN use of your product. <br> For instance: `$ sudo ip link set dev wlan0 down`                                                | [README][5]   |

Please refer to the corresponding README files for details on using the tools.

## Related resources

Whenever a tool is only valid for a single platform, it is stored
 in a corresponding platform-specific repository.

Platform-specific repositories are:

* [The 'FullMAC tools' repository][1], for RTOS & Bare Metal applications
* [The 'Linux tools' repository][2], for Linux platforms

[1]: https://github.com/SiliconLabs/wfx-fullMAC-tools
[2]: https://github.com/SiliconLabs/wfx-linux-tools
[3]: https://github.com/SiliconLabs/wfx-common-tools/blob/master/src/wfx_common_tools/connection/README.md
[4]: https://github.com/SiliconLabs/wfx-common-tools/blob/master/src/wfx_common_tools/pta/README.md
[5]: https://github.com/SiliconLabs/wfx-common-tools/blob/master/src/wfx_common_tools/test_feature/README.md
