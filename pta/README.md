PTA (Packet Traffic Arbitration) python scripts
These scripts are used to format PTA bytes according to the user's preferences and send them to the WFX firmware.

 
# Testing

## Expected result of dut.selftest():
```
['settings', '--Config', '3W_NOT_COMBINED_BLE']
Configuring for 3W_NOT_COMBINED_BLE
PtaMode                               0 =>        3 (x3)
CoexType                              0 =>        1 (x1)
PrioritySamplingTime                  9 =>       10 (xa)
PtaMode                        3          \x03
RequestSignalActiveLevel       1          \x01
PrioritySignalActiveLevel      1          \x01
FreqSignalActiveLevel          1          \x01
GrantSignalActiveLevel         0          \x00
CoexType                       1          \x01
DefaultGrantState              1          \x01
SimultaneousRxAccesses         0          \x00
PrioritySamplingTime           10         \x0a
TxRxSamplingTime               50         \x32
FreqSamplingTime               70         \x46
GrantValidTime                 72         \x48
FemControlTime                 140        \x8c
FirstSlotTime                  150        \x96
PeriodicTxRxSamplingTime       1          \x01\x00
CoexQuota                      0          \x00\x00
WlanQuota                      0          \x00\x00
pi       D>>|  set -ex; wfx_exec wfx_hif_send_msg "\x18\x00\x2b\x00\x03\x01\x01\x01\x00\x01\x01\x00\x0a\x32\x46\x48\x8c\x96\x01\x00\x00\x00\x00\x00"
<<D       pi|  0
settings result: HI_STATUS_SUCCESS
['priority', '--PriorityMode', 'BALANCED']
PriorityMode                   5217       \x61\x14\x00\x00
pi       D>>|  set -ex; wfx_exec wfx_hif_send_msg "\x08\x00\x2c\x00\x61\x14\x00\x00"
<<D       pi|  0
priority result: HI_STATUS_SUCCESS
['state', '--State', 'OFF']
State                          0          \x00\x00\x00\x00
pi       D>>|  set -ex; wfx_exec wfx_hif_send_msg "\x08\x00\x2d\x00\x00\x00\x00\x00"
+ wfx_exec wfx_hif_send_msg \x08\x00\x2d\x00\x00\x00\x00\x00
<<D       pi|  0
state    result: HI_STATUS_SUCCESS
```

