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

At the time of writing, related repositories are:

* [The 'FullMAC tools' repository][1]
* [The 'Linux tools' repository][2]

[1]: https://github.com/SiliconLabs/wfx-fullMAC-tools
[2]: https://github.com/SiliconLabs/wfx-linux-tools
[3]: https://github.com/SiliconLabs/wfx-common-tools/blob/master/connection/README.md
[4]: https://github.com/SiliconLabs/wfx-common-tools/blob/master/pta/README.md
[5]: https://github.com/SiliconLabs/wfx-common-tools/blob/master/test-feature/README.md
