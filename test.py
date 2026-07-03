from src.wfx_common_tools.test_feature import wfx_test_dut
import time
import serial
import signal
import argparse
import serial.tools.list_ports
import threading

dut = None
stop_event = threading.Event()

def list_serial_ports():
    """Return a list of available serial ports with descriptions."""
    return list(serial.tools.list_ports.comports())

def choose_serial_port():
    """Prompt user to choose a serial port from the list."""
    ports = list_serial_ports()
    if not ports:
        print("No serial ports found.")
        return None

    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"[{i}] {port.device} - {port.description}")

    while True:
        try:
            index = int(input("Select a port by number: "))
            if 0 <= index < len(ports):
                return ports[index].device
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")

def get_serial_port_from_args_or_prompt():
    parser = argparse.ArgumentParser(description="Serial port selector")
    parser.add_argument('--port', help="Serial port to use (e.g., COM3 or /dev/ttyUSB0)")
    args = parser.parse_args()

    if args.port:
        return args.port
    else:
        return choose_serial_port()

def send_cli_commands(serial_port, commands):
    try:
        '''
            This function will permit to run some CLI commands before RF Agent
        '''
        command_timeout_s = 3.0
        with serial.Serial(port=serial_port, baudrate=115200, timeout=0.5) as ser:
            for item in commands:
                cmd = item["cmd"]
                expected_response = item["response"]

                # Send the command
                ser.write((cmd + '\r\n').encode('utf-8'))
                print(f">>> {cmd}")

                if expected_response is None:
                    time.sleep(1.0)
                    while ser.readline():
                        # Empty incoming buffer
                        pass
                    
                    continue  # No response expected, move to next command

                # Start waiting for the expected response
                start_time = time.time()
                while time.time() - start_time < command_timeout_s:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        print(f"<<< {line}")
                        if line == expected_response:
                            break
                else:
                    raise RuntimeError(f"Timeout waiting for response '{expected_response}' to command '{cmd}'")

            print("All commands processed successfully.")
            return True

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
        return False
    except RuntimeError as e:
        print(e)
        return False

def wait_for_ctrl_c_and_run(signal_handler, text):
    print("Press Ctrl+C to {:s}".format(text))
    stop_event.clear()
    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_event.set()
    signal_handler() 

def wait_no_action(sig, frame):
    pass

def wait():
    wait_for_ctrl_c_and_run(wait_no_action, "continue")

def modulation_stop_handler():
    global dut
    print("\nCtrl+C detected. Stop modulation")
    dut.tx_stop()
    
    
def modulation(regulatory_mode, channel, tx_mode, tx_power_reduction = 0.0, tx_framing=1500):
    global dut
    dut.tx_framing(tx_framing,0)     # Frame size of 1500 bytes with the lowest inter frame space (IFS)
    dut.regulatory_mode(regulatory_mode) # set regulatory mode to ETSI or FCC or JAPAN
    dut.channel(channel)
    dut.tx_backoff(tx_mode, tx_power_reduction)  # Tx power reduction of 0.5dB for B_1Mbps (step: 0.25 dB)
    dut.tx_start('continuous')
    wait_for_ctrl_c_and_run(modulation_stop_handler, "stop modulation")
    
def tone_stop_handler():
    global dut
    print("\nCtrl+C detected. Stop Tone")
    dut.tone_stop()

def tone(channel=1, freq_offset=0, dbm=None):
    global dut
    '''
        Run a TX Tone on the given channel
        @param dut RF agent DUT
        @param channel WIFI Channel Number. Range [1;13]
        @param freq_offset Offset from the channel. Step of 312.5 KHz. Range: [-31;1]
        @param dbm Tone power. Can be None or dbm (float). Ex: 10.0
    '''
    dut.channel(channel)
    dut.tone_power(dbm)
    dut.tone_freq(freq_offset)
    dut.tone_start()
    wait_for_ctrl_c_and_run(tone_stop_handler, "stop tone")

#port = '/dev/tty.usbserial-FT5RQIQL'

commands = [
    {"cmd": "HW POWER DCDC_EN 0", "response": None},    # Force restart of Wifi
    {"cmd": "HW POWER DCDC_EN 1", "response": "OK"},    # Start power supply for Wifi chipset
    {"cmd": "HW WIFI RF_AGENT 1", "response": "OK"},    # Start Wifi RF agent in MCU side
]

def help():
    print("======================")
    print("RF Agent helpers")
    print("This is a python console")
    print("The RF agent is available from `dut` object. Ex: `dut.channel(chan)`")
    print("Some functions helpers can be useful:")
    print("- tone(channel, freq_offset=0, dbm=None) It will send a TX tone on the matching channel.")
    print('\tEx: tone(channel=6, freq_offset=0, dbm=15.0)')
    print("- modulation(regulatory_mode, channel, tx_mode, tx_power_reduction = 0.0, tx_framing=1500) It will send a TW CW on the matching channel.")
    print('\tEx: modulation("ETSI", 1, "B_1Mbps", tx_power_reduction=0.0, tx_framing=1500)')
    print("- wait() Permit to wait a CTRL+C before continuing")
    print("- exit() to stop the terminal")
    print("- help() to print help")
    print("\nFor more commands/tool, refer to below documentation:")
    print("- List of `dut` functions: https://github.com/SiliconLabs/wfx-common-tools/blob/master/src/wfx_common_tools/test_feature/README.md#wfxtestdut-api-functions")
    print("- Certifications process: https://github.com/SiliconLabs/wfx-common-tools/blob/master/src/wfx_common_tools/test_feature/certification.md")
    print("======================")

def setup_board(port):
    global dut
    # Run settings commands
    print("RF agent starting... it will require some seconds to prepare with MCU Host...")
    send_cli_commands(port, commands)
    time.sleep(1)

    # Start WIFI RF Agent
    dut = wfx_test_dut.WfxTestDut('Serial', port=port, baudrate=115200, bytesize=8, parity='N', stopbits=1, tx_frame_ending="\r\n", rx_frame_ending="\r\n")
    dut.trace = True
    dut.link.trace = True
    dut.tx_rx_select(1,1)      # Select antenna 1 in TX/RX

    time.sleep(1)

    print("\n\nRF agent ready...")
    help()

'''
Example of commands:
modulation("ETSI", 1, "B_1Mbps", tx_power_reduction=0.0, tx_framing=1500)
tone(channel=6)
tone(channel=6, freq_offset=-10, dbm=15.0)

More RF agent commands are available there: https://github.com/SiliconLabs/wfx-common-tools/blob/master/src/wfx_common_tools/test_feature/README.md

For Certifications process, a documentation is available there: https://github.com/SiliconLabs/wfx-common-tools/blob/master/src/wfx_common_tools/test_feature/certification.md
'''

if __name__ == "__main__":
    port = get_serial_port_from_args_or_prompt()
    if port:
        print(f"Using serial port: {port}")
        setup_board(port)
    else:
        print("No port selected. Exiting.")