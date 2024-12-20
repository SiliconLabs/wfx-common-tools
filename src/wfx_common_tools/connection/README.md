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

Connection scripts are written and tested for Python3.9

## Connection

### Direct

('name' only --> Direct)

```python
>>> from wfx_common_tools.connection import wfx_connection
>>>  dut = wfx_connection.WfxConnection('<name>')
```

### SSH

Connect to the DUT with username & password:

```python
>>> from wfx_common_tools.connection import wfx_connection
>>>  dut = wfx_connection.WfxConnection('<name>', host='<hostname or IP address>', user='<user>', password='<password>')
```

If you don't want to put the DUT login's password in your src code, you can use the SSH keys authentication as the following guide [ here](https://www.linode.com/docs/guides/use-public-key-authentication-with-ssh/)

```bash
$ ssh-keygen -t ed25519 -C "user@example.com"
$ ssh-copy-id [user]@[ip-address] # Input password once time
$ ssh [user]@[ip-address] # No required password input anymore
```

Now, the Python script can use Paramiko library to SSH to the DUT without password

```python
>>>  dut = wfx_connection.WfxConnection('<name>', host='<hostname or IP address>', user='<user>')
```

### UART with user/password

(port + user --> UART with login)

```python
>>>  dut = wfx_connection.WfxConnection('<name>', port='COM19', user='<user>', password='<password>', baudrate=115200, bytesize=8, parity='N', stopbits=1)
```

_NB: baudrate, bytesize, parity and stopbits values are optional, values used above are the default values_

### UART for RTOS/Bare metal

(port --> UART)

```python
>>>  dut = wfx_connection.WfxConnection('<name>', port='COM19', baudrate=115200, bytesize=8, parity='N', stopbits=1)
```

_NB: baudrate, bytesize, parity and stopbits values are optional, values used above are the default values_

### TELNET

(port ='telnet' + host + user --> TELNET)

```python
>>>  dut = wfx_connection.WfxConnection('<name>', host='<hostname or IP address>', port='telnet', user='<user>', password='<password>')
```

## Connection API

| function      | function parameters               | Comments                          |
|---------------|-----------------------------------|-----------------------------------|
| `write`       |`text`: string to write            |                                   |
| `read`        |None                               |                                   |
| `run`         |`cmd`: string to write<br>`wait_ms`: delay between `write` and `read`  | Calls `write`, waits for *wait_ms* then calls `read` |
| 'close'       |None                               | Close connection                  |
