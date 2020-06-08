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

## Content

Typically, Python resources can be used to run tests on WFX devices, and such tools can be running on any
 Python-capable platform.

| Folder       | Usage                                                                                                       | Documentation |
|--------------|-------------------------------------------------------------------------------------------------------------|---------------|
| connection   | Python communication resources imported from other tools, accessed using `sys.path.append('../connection')` | [README][3]   |
| pta          | Python scripts for PTA (Packet Traffic Arbitration), when several radio standards use shared RF resources   | [README][4]   |
| test-feature | Pythons scripts used to test the RF performance                                                             | [README][5]   |

Please refer to the corresponding README files for details on using the tools.

## Related resources

Whenever a tool is only valid for a single platform, it is stored
 in a corresponding platform-specific repository.

Platform-specific repositories are:

* [The 'FullMAC tools' repository][1], for RTOS & Bare Metal applications
* [The 'Linux tools' repository][2], for Linux platforms

[1]: https://github.com/SiliconLabs/wfx-fullMAC-tools
[2]: https://github.com/SiliconLabs/wfx-linux-tools
[3]: https://github.com/SiliconLabs/wfx-common-tools/blob/master/connection/README.md
[4]: https://github.com/SiliconLabs/wfx-common-tools/blob/master/pta/README.md
[5]: https://github.com/SiliconLabs/wfx-common-tools/blob/master/test-feature/README.md
