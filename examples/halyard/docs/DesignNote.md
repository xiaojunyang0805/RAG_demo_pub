<!-- CONTRACT: STATE — must be true now. Master specification. -->

# Halyard — Design Note

## 1. What Halyard is

A three-board drive for one 48 V brushless wheel motor (motor M-80) on an AGV. The vehicle controller sends speed
and torque commands over CAN; Halyard closes the current, speed and position loops locally.

## 2. Requirements

| ID | Requirement |
|---|---|
| FR-01 | Run from the 48 V AGV battery (`P-01`), survive 58 V on regenerative braking |
| FR-02 | Deliver 32 A peak per phase (`P-02`) for 2 s at stall |
| FR-03 | No audible switching noise in the AGV chassis |
| FR-04 | Absolute position at power-up (no homing move) |
| FR-05 | Shut down safely before any part exceeds its rating |

## 3. Blocks

- **HB-P power stage** — three half-bridges of QX-100N MOSFETs, Tessaro GD-22 gate drivers, 680 µF DC link,
  1 mΩ low-side shunts. 110 × 80 mm, 4 layers, 2 oz copper.
- **HB-C controller** — Corvid C4-180 MCU (512 KB flash, 180 MHz), field-oriented control, CAN at 1 Mbit/s,
  bootloader. 60 × 45 mm, stacks on HB-P.
- **HB-S sensor hub** — RS-485 receiver for the absolute encoder, motor NTC input, brake MOSFET.

## 4. Decisions (one line each; full text in `DecisionLog.md`)

| ID | Decision | Status |
|---|---|---|
| D1 | Three boards: power, controller, sensor hub | ✅ |
| D2 | 48 V nominal bus, 100 V MOSFETs | ✅ |
| D3 | Field-oriented control with an absolute encoder (no sensorless start) | ✅ |
| D4 | Low-side shunt current sensing, one shunt per leg | ✅ |
| D5 | Encoder link is RS-485, not SPI (2 m cable through the chassis) | ✅ |
| D6 | CAN at 1 Mbit/s | ✅ |
| D7 | PWM at 24 kHz, above the audible band | ✅ |
| D8 | Phase current limit 32 A, from the measured stall current | ✅ |
| D9 | MCU Corvid C4-180 (Rev B), replacing the C4-120 | ✅ |
| D10 | DC link 680 µF | ✅ |
| D11 | Thermal shutdown at 95 °C on the heat-sink NTC | ✅ |
| D12 | Motor connector 3-pin 7.62 mm pitch, rated 41 A | ✅ |

## 5. Safety

The drive stops switching on any of: over-current (`P-02` + 10 %), heat sink above `P-05`, bus above 60 V,
encoder fault, CAN timeout of 50 ms. The brake on HB-S engages on any stop.
