# wfx-common-tools
This repository contains WFX tools which are not platform-specific,
 and can be used on several platforms.

NB: Whenever a tool is only valid for a single platform, it will be stored
 in a corresponding platform-specific repository.
  At the time of writing, related repositories are:
* https://github.com/SiliconLabs/wfx-fullMAC-tools
* https://github.com/SiliconLabs/wfx-linux-tools

# repository content
Typically, Python resources can be used to run tests on WFX devices, and such tools can be running on any
 Python-capable platform.

| folder       | usage |
|--------------|-------|
| connection   | Python communication resources imported from other tools, which use `sys.path.append('../connection')` |
| pta          | Python scripts for PTA (Packet Traffic Arbitration), when several radio standards use shared RF resources|
|test-feature  | Pythons scripts used to test the RF performance |

Please refer to the corresponding READMEs for details on using the tools. 