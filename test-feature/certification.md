# Certification testing

RF Tx certification testing of a Wi-Fi product consists in checking that Tx signals are compliant with regulatory
 requirements (power, spurious,..) without using an AP in WLAN mode.

To test Tx, the product is using a continuous transmission mode.

> NB: Prior to running RF testing, make sure you stop any WLAN use of your product.

Below is an example showing a test scenario and results for FCC certification:

* This example is for **FCC certification** with **WFM200** and **WGM160P**
* For **WF200**, start from **WF200 Recommended TX Backoff** table 5.2 or 5.3 from [UG382 'WF200 Hardware Design User's
Guide
'](https://www.silabs.com/documents/public/user-guides/ug382-wf200-hardware-design-ug.pdf) (section 5.2 'RF Part'))

## General initialization

```python
from wfx_test_dut import *
dut = WfxTestDut('Local')
dut.tx_rx_select(1,1)      # Select antenna 1 in TX/RX
dut.tx_framing(1500,0)     # Frame size of 1500 bytes with the lowest inter frame space (IFS)
regulatory_mode('FCC')     # set regulatory mode to ETSI or FCC or JAPAN
```

## Channel and Tx Backoff testing

For each channel in the regulatory domain and each PHY rate, check Tx power against the
 regulatory Tx requirements and apply Tx power reduction (aka 'backoff') if required

### Channel and Tx Mode selection

```python
dut.channel(1)
dut.tx_mode('B_1Mbps')
```

### Tx Backoff adjustment 

```python
dut.tx_backoff('B_1Mbps',0.5)  # Tx power reduction of 0.5dB for B_1Mbps (step: 0.25 dB)
dut.tx_start('continuous')
# . . . Compare Tx spectrum with regulatory requirements, increase tx_backoff until 'PASS'
```

When done, stop transmitting and continue testing the next channel and Tx mode

```python
dut.tx_stop()
```

## Tx Backoff tables

After each channel and PHY rate has been checked and the corresponding Tx backoff found, you have the following tables
 for each MOD_GROUP:

### MOD_GROUP_0: B_1Mbps, B_2Mbps, B_5.5Mbps, B_11Mbps

| **MOD_GROUP_0**<br>PHY rate / Channel | B_1Mbps | B_2Mbps | B_5.5Mbps | B_11Mbps | max_backoff (dB) | BACKOFF_QDB = 4*max_backoff |
|----| -----|------|------|------|------|-------|
|  1 | 0.50 | 0.25 | 0    | 0    | 0.50 | **2** |
|  2 | 0.25 | 0.25 | 0    | 0    | 0.25 | **1** |
|  3 | 0    | 0    | 0    | 0    | 0    | **0** |
|  4 | 0    | 0    | 0    | 0    | 0    | **0** |
|  5 | 0    | 0    | 0    | 0    | 0    | **0** |
|  6 | 0    | 0    | 0    | 0    | 0    | **0** |
|  7 | 0    | 0    | 0    | 0    | 0    | **0** |
|  8 | 0    | 0    | 0    | 0    | 0    | **0** |
|  9 | 0    | 0    | 0    | 0    | 0    | **0** |
| 10 | 0.25 | 0.25 | 0    | 0    | 0.25 | **1** |
| 11 | 0.50 | 0.25 | 0    | 0    | 0.50 | **2** |
| 12 | 0    | 0    | 0    | 0    | 0    | **0** |
| 13 | 0    | 0    | 0    | 0    | 0    | **0** |
| 14 | 0    | 0    | 0    | 0    | 0    | **0** |


### MOD_GROUP_1: G_6Mbps, G_9Mbps, G_12Mbps, N_MCS0, N_MCS1 

| **MOD_GROUP_1**<br>PHY rate / Channel |  G_6Mbps | G_9Mbps | G_12Mbps | N_MCS0 | N_MCS1 | max_backoff (dB) | BACKOFF_QDB = 4*max_backoff |
|----| -----|------|------|------|------|------|-----------|
|  1 | 2.50 | 0    | 0    | 2.00 | 0    | 2.50 | **10**    |
|  2 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |
|  3 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |
|  4 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |
|  5 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |
|  6 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |
|  7 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |
|  8 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |
|  9 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |
| 10 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |
| 11 | 1.50 | 0    | 0    | 1.00 | 0    | 1.50 |  **6**    |
| 12 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |
| 13 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |
| 14 | 0    | 0    | 0    | 0    | 0    | 0    |  **0**    |

### MOD_GROUP_2: G_18Mbps, G_24Mbps, N_MCS2, N_MCS3

| **MOD_GROUP_2**<br>PHY rate / Channel |  G_18Mbps | G_24Mbps | N_MCS2 | N_MCS3 | max_backoff (dB) | BACKOFF_QDB = 4*max_backoff |
|----| -----|------|------|------|------|----------|
|  1 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  2 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  3 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  4 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  5 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  6 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  7 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  8 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  9 | 0    | 0    | 0    | 0    | 0    | **0**    |
| 10 | 0    | 0    | 0    | 0    | 0    | **0**    |
| 11 | 0    | 0    | 0    | 0    | 0    | **0**    |
| 12 | 0    | 0    | 0    | 0    | 0    | **0**    |
| 13 | 0    | 0    | 0    | 0    | 0    | **0**    |
| 14 | 0    | 0    | 0    | 0    | 0    | **0**    |


### MOD_GROUP_3: G_36Mbps, G_48Mbps, N_MCS4, N_MCS5 

| **MOD_GROUP_3**<br>PHY rate / Channel |  G_36Mbps | G_48Mbps | N_MCS4 | N_MCS5 | max_backoff (dB) | BACKOFF_QDB = 4*max_backoff |
|----| -----|------|------|------|------|----------|
|  1 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  2 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  3 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  4 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  5 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  6 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  7 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  8 | 0    | 0    | 0    | 0    | 0    | **0**    |
|  9 | 0    | 0    | 0    | 0    | 0    | **0**    |
| 10 | 0    | 0    | 0    | 0    | 0    | **0**    |
| 11 | 0    | 0    | 0    | 0    | 0    | **0**    |
| 12 | 0    | 0    | 0    | 0    | 0    | **0**    |
| 13 | 0    | 0    | 0    | 0    | 0    | **0**    |
| 14 | 0    | 0    | 0    | 0    | 0    | **0**    |

### MOD_GROUP_4: G_54Mbps, N_MCS6 

| **MOD_GROUP_4**<br>PHY rate / Channel |  G_54Mbps | N_MCS6 | max_backoff (dB) | BACKOFF_QDB = 4*max_backoff |
|----| -----|------|------|---------|
|  1 | 0    | 0    | 0    | **0**   |
|  2 | 0    | 0    | 0    | **0**   |
|  3 | 0    | 0    | 0    | **0**   |
|  4 | 0    | 0    | 0    | **0**   |
|  5 | 0    | 0    | 0    | **0**   |
|  6 | 0    | 0    | 0    | **0**   |
|  7 | 0    | 0    | 0    | **0**   |
|  8 | 0    | 0    | 0    | **0**   |
|  9 | 0    | 0    | 0    | **0**   |
| 10 | 0    | 0    | 0    | **0**   |
| 11 | 0    | 0    | 0    | **0**   |
| 12 | 0    | 0    | 0    | **0**   |
| 13 | 0    | 0    | 0    | **0**   |
| 14 | 0    | 0    | 0    | **0**   |


### MOD_GROUP_5: N_MCS7

| **MOD_GROUP_5**<br>PHY rate / Channel |  N_MCS7 | max_backoff (dB) | BACKOFF_QDB = 4*max_backoff |
|----| -----|------|---------|
|  1 | 0    | 0    | **0**   |
|  2 | 0    | 0    | **0**   |
|  3 | 0    | 0    | **0**   |
|  4 | 0    | 0    | **0**   |
|  5 | 0    | 0    | **0**   |
|  6 | 0    | 0    | **0**   |
|  7 | 0    | 0    | **0**   |
|  8 | 0    | 0    | **0**   |
|  9 | 0    | 0    | **0**   |
| 10 | 0    | 0    | **0**   |
| 11 | 0    | 0    | **0**   |
| 12 | 0    | 0    | **0**   |
| 13 | 0    | 0    | **0**   |
| 14 | 0    | 0    | **0**   |

## BACKOFF_QDB vs Channel per MOD_GROUP

If we only display the **BACKOFF_QDB** for each MOD_GROUP (the **bold** values above), we have the
 following summary table, as a result of certification testing

|BACKOFF_DQB = f(MOD_GROUP, Channel)|MOD_GROUP_0|MOD_GROUP_1|MOD_GROUP_2|MOD_GROUP_3|MOD_GROUP_4|MOD_GROUP_5|
|----| ----|-----|-----|-----|-----| ----|
|  1 | **2** | **10** | **0** | **0** | **0** | **0** |
|  2 | **1** |  **0** | **0** | **0** | **0** | **0** |
|  3 | **0** |  **0** | **0** | **0** | **0** | **0** |
|  4 | **0** |  **0** | **0** | **0** | **0** | **0** |
|  5 | **0** |  **0** | **0** | **0** | **0** | **0** |
|  6 | **0** |  **0** | **0** | **0** | **0** | **0** |
|  7 | **0** |  **0** | **0** | **0** | **0** | **0** |
|  8 | **0** |  **0** | **0** | **0** | **0** | **0** |
|  9 | **0** |  **0** | **0** | **0** | **0** | **0** |
| 10 | **1** |  **0** | **0** | **0** | **0** | **0** |
| 11 | **2** |  **6** | **0** | **0** | **0** | **0** |
| 12 | **0** |  **0** | **0** | **0** | **0** | **0** |
| 13 | **0** |  **0** | **0** | **0** | **0** | **0** |
| 14 | **0** |  **0** | **0** | **0** | **0** | **0** |


> Note that in this example channels 3 to 9 use identical values, and well as channels 12 to 14
> (these last don't apply to the FCC case).

## BACKOFF_QDB in PDS

Once the above **BACKOFF_QDB** values have been filled they need to be copied in the PDS file, in section
 **RF_POWER_CFG:BACKOFF_QDB**, as follows
  (see [UG404 'WF(M)200 Configuration Guide
with PDS'](https://www.silabs.com/documents/public/user-guides/ug404-wf200-pds-configuration-users-guide.pdf)
 section 3.7 'RF_POWER_CFG Section'):

```text
RF_POWER_CFG: { 
// Designate the RF port affected by the following configurations 
// RF_PORT_1, RF_PORT_2, RF_PORT_BOTH (default) 
RF_PORT: RF_PORT_BOTH, 
// The max Tx power value in quarters of dBm. Type: signed integer between -128 and 127 (range in dBm: [-32; 31.75]) 
// It is used to limit the Tx power. Thus a value larger than 80 does not make sense. 
MAX_OUTPUT_POWER_QDBM: 80, 
// Front-end loss (loss between the chip and the antenna) in quarters of dB. 
// Type: signed integer between -128 and 127 (range in dB: [-32; 31.75]) 
// This value must be positive when the front end attenuates the signal and negative when it amplifies it. 
// Values on Rx path and Tx path can be different thus 2 values are provided here 
FRONT_END_LOSS_TX_QDB: 0, 
FRONT_END_LOSS_RX_QDB: 0, 
// Backoff vs. Modulation Group vs Channel 
// CHANNEL_NUMBER: Designate a channel number (an integer) or a range of channel numbers (an array) 
// e.g. CHANNEL_NUMBER: [3, 9] : Channels from 3 to 9 
// Each backoff value sets an attenuation for a group of modulations. 
// BACKOFF_VAL is given in quarters of dB. Type : unsigned integer. Covered range in dB: [0; 63.75] 
// A modulation group designates a subset of modulations : 
// * MOD_GROUP_0 : B_1Mbps, B_2Mbps, B_5.5Mbps, B_11Mbps 
// * MOD_GROUP_1 : G_6Mbps, G_9Mbps, G_12Mbps, N_MCS0, N_MCS1, 
// * MOD_GROUP_2 : G_18Mbps, G_24Mbps, N_MCS2, N_MCS3, 
// * MOD_GROUP_3 : G_36Mbps, G_48Mbps, N_MCS4, N_MCS5 
// * MOD_GROUP_4 : G_54Mbps, N_MCS6 
// * MOD_GROUP_5 : N_MCS7 
// BACKOFF_VAL: [MOD_GROUP_0, ..., MOD_GROUP_5]
BACKOFF_QDB: [
 {
 CHANNEL_NUMBER: 1,
 BACKOFF_VAL: [2, 10, 0, 0, 0, 0]
 },
 {
 CHANNEL_NUMBER: 2,
 BACKOFF_VAL: [1, 0, 0, 0, 0, 0]
 },
 {
 CHANNEL_NUMBER: [3, 9],
 BACKOFF_VAL: [0, 0, 0, 0, 0, 0]
 },
 {
 CHANNEL_NUMBER: 10,
 BACKOFF_VAL: [1, 0, 0, 0, 0, 0]
 },
 {
 CHANNEL_NUMBER: 11,
 BACKOFF_VAL: [2, 6, 0, 0, 0, 0]
 },
 {
 CHANNEL_NUMBER: [12, 14],
 BACKOFF_VAL: [0, 0, 0, 0, 0, 0]
 }
 ]
}
```

* Each **BACKOFF_QDB** column in the tables corresponds to one column in the **BACKOFF_VAL** arrays
* When several channels use identical **BACKOFF_QDB**, they can be grouped in a **CHANNEL_NUMBER** array
* Using a production PDS file with these values will ensure that the TX power will stay within regulatory limits for all channels

You can use the attached [Excel sheet](tx_backoff.xlsx) during this process.
