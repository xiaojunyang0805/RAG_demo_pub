<!-- CONTRACT: STATE — written as the current plan for Rev A. Archived: history only. -->

# HB-C controller plan — Rev A

## MCU

The Halyard controller MCU is the **Corvid C4-120**: 120 MHz, 256 KB flash, 64 KB RAM. It runs six-step
commutation first, then field-oriented control.

## Communication

The Halyard drive talks to the AGV controller over **CAN at 500 kbit/s**, the AGV default bit rate.

## Encoder

The encoder connects over **SPI** at 4 MHz to SPI2 of the C4-120. The absolute encoder of the M-80 is read every
PWM period. The encoder interface is SPI because the MCU has a free port and the cable is short.

## Loop rates

Current loop at 20 kHz (once per PWM period), speed loop at 2 kHz.
