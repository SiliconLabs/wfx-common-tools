# WFX connection layer

During WFX development, communicating with the part is required for several purposes (such as RF testing or PTA)

To limit the number of platform-specific code and provide easier coding and maintenance, most scripts can run
 remotely once the necessary communication can be established with the part.

Such is the purpose of the WFX connection layer.

## Connection modes

Tests scripts requiring access to the WFX can connect in the following modes:

* Local (only possible on platforms supporting Python3, such as the Raspberry Pi)
* SSH
* UART

## Test architecture

The test uses a **Test server**/**DUT** architecture, where only the bare minimum is added to the **DUT** and most of the complexity is handled by the **Test server**

The **Test server** can be any python3-capable platform with network and/or UART communication capabilities

* One possible python3-capable platform is the Raspberry PI.
  * In this case, both the Test Server and the DUT are running on the Raspberry PI.
* In most customer cases, the **Test server** is a separate machine which connects to the **DUT** via SSH or UART

* The **DUT** only needs to support the actions required for the test.
  * Examples are
  * Sending HIF commands (a.ka. 'Requests') to the WFX and retrieving the corresponding 'confirmation' status (for PTA)
  * Send RF test data via a small **wfx_test_agent** (for RF testing)

## Python version

Connection scripts are written and tested for Python3.

## Installation

### Dependencies

Install Python3 with SSH and UART on the **Test server** to allow the connection layer to connect

Python3 resources for SSH and UART need to be installed on the **Test server**, including the paramiko package which deals with encryption required by SSH (paramiko installation is the longest one).

This part of the installation differs depending on the **Test server** OS:
  
### Installing Python3 with SSH and UART resources on Windows

* Download Python3 from <https://www.python.org/downloads/windows/> for your platform
* In the first installation window, tick 'Add Python 3.x to PATH' (otherwise you will need to add it to your PATH later)
  * To check proper Python3 installation, open a terminal window and type 'python'. This should give you the Python `>>>` prompt
 with details on the version. use `quit()` to stop Python3
* Installing Python3 will also have pip and pip3 installed. However, it is required to upgrade to their latest versions using
 `python -m pip install --upgrade pip`
* Install paramiko (for SSH support), ifaddr (to be able to list available networks) and pyserial (to connect to UARTS) 

```bash
pip3 install paramiko
pip3 install ifaddr
pip3 install pyserial
````

### Installing Python3 with SSH and UART resources on Linux

(run the `.install.sh` script on the **Test server**)
NB: the `install` script for `wfx-common-tools/connection/` takes a while, since it install paramiko, the Python
package for SSH connection. SSH requires cryptography resources, and installing these takes a while.

```bash
apt-get update
apt-get install libffi-dev python3-pip
apt-get install libssl-dev
pip3 install pip==19.1
pip3 install setuptools==41.0.1
pip3 install pynacl
pip3 install pygments==2.3.1
pip3 install paramiko==2.4.2
pip3 install ipython==6
pip3 install ifaddr==0.1.6
pip3 install pyserial==2.6
```

### Connection layer Installation

Install the connection layer on the **Test server**

```bash
cd ~/siliconlabs/
git clone https://github.com/SiliconLabs/wfx-common-tools.git
```

### Connection layer Update

Update the connection layer on the **Test server**

```bash
cd ~/siliconlabs/wfx-common-tools/test-feature
git fetch
git checkout origin/master
```

## Connecting

### Direct

('name' only --> Direct)

```python
>>>  dut = WfxConnection('<name>')
```

### SSH

```python
>>>  dut = WfxConnection('<name>', host='<hostname or IP address>', user='<user>', password='<password>')
```

### UART with user/password

(port + user --> UART with login)

```python
>>>  dut = WfxConnection('<name>', port='COM19', user='<user>', password='<password>', baudrate=115200, bytesize=8, parity='N', stopbits=1)
```

_NB: baudrate, bytesize, parity and stopbits values are optional, values used above are the default values_

### UART for RTOS/Bare metal

(port --> UART)

```python
>>>  dut = WfxConnection('<name>', port='COM19', baudrate=115200, bytesize=8, parity='N', stopbits=1)
```

_NB: baudrate, bytesize, parity and stopbits values are optional, values used above are the default values_

### TELNET

(port ='telnet' + host + user --> TELNET)

```python
>>>  dut = WfxConnection('<name>', host='<hostname or IP address>', port='telnet', user='<user>', password='<password>')
```

## Connection API

| function      | function parameters               | Comments                          |
|---------------|-----------------------------------|-----------------------------------|
| `write`       |`text`: string to write            |                                   |
| `read`        |None                               |                                   |
| `run`         |`cmd`: string to write<br>`wait_ms`: delay between `write` and `read`  | Calls `write`, waits for *wait_ms* then calls `read` |
| 'close'       |None                               | Close connection                  |
