<!-- CONTRACT: STATE — must be true now. HB-C spec sheet. -->

# HB-C — Controller (Rev B)

| | |
|---|---|
| MCU | **Corvid C4-180** — 180 MHz, 512 KB flash, 128 KB RAM (`D9`) |
| Control | Field-oriented control; current loop 24 kHz, speed loop 2 kHz (`P-09`) |
| CAN | **1 Mbit/s** (`D6`), 120 Ω termination by jumper |
| Encoder input | from HB-S over the stack connector (RS-485 decoded on HB-S, `D5`) |
| Bootloader | CAN bootloader, CRC-32 over the whole image (`CT-O3`) |
| Size | 60 × 45 mm, 4 layers, stacks on HB-P with two 2 × 10 headers |
| Debug | 10-pin SWD header, UART on pins 7/8 |

## Firmware

v0.9: FOC with space-vector modulation, CAN command and telemetry, bootloader, fault handling. Field weakening
is open (`CT-O5`).
