<!-- CONTRACT: LOG — append-only; only §0 states current truth. -->

# HB-C worknote

## §0 CURRENT STATE *(2026-06-01)*

| | |
|---|---|
| Board | Rev B, Corvid C4-180, FOC running |
| Firmware | v0.9; flash use 318 KB of 512 KB |
| Open | `CT-O5` field weakening |

> ⛔ Below is history.

## §1 Rev A, January 2026

MCU is the Corvid C4-120: 120 MHz, 256 KB flash. Six-step commutation first, FOC later. CAN at 500 kbit/s to
match the AGV controller default. The encoder is read over SPI at 4 MHz on SPI2.

## §2 Flash, March 2026

FOC + CAN stack + bootloader link to 310 KB. The C4-120 has 256 KB. Opened `CT-O2`. Options: drop the bootloader,
or move to the C4-180 (pin-compatible, 512 KB). Chose the C4-180 (`D9`).

## §3 CAN load, March 2026

Telemetry at 2 kHz fills 71 % of a 500 kbit/s bus. Moving to 1 Mbit/s (`D6`).

## §4 Bootloader, May 2026

A corrupt image passed the check: the CRC covered the 64-byte header only (`CT-O3`). Now CRC-32 over the whole
image, verified before the jump.
