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

It would be a best practice to install packages in a virtual environment using pip & venv for different projects as the guideline [here](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/). 

Basically, some basic steps as the following commands:

```bash
$ mkdir -p my_project && cd my_project
$ python -m venv .my_env
$ source ./my_env/bin/activate
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
