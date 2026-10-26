<!-- CONTRACT: STATE — must be true now. HB-S spec sheet. -->

# HB-S — Sensor hub

| | |
|---|---|
| Encoder link | **RS-485**, 2.5 Mbit/s, to the M-80's absolute encoder (`D5`); verified error-free over a 2 m chassis cable |
| Encoder resolution | 4096 counts/rev, absolute (`P-10`) |
| Motor NTC | 10 kΩ input, read by HB-C; motor stops at 120 °C winding temperature |
| Brake | 24 V brake output, MOSFET low-side switch, engages on any stop |
| Size | 50 × 30 mm, mounted on the motor end bell |

## Why RS-485

The encoder cable runs 2 m through the chassis beside the motor phases. SPI at 4 MHz showed bit errors in the
first chassis test (`SH-O2`); a differential link does not.
