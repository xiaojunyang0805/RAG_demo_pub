<!-- CONTRACT: STATE — the only status authority for open items. -->

# Halyard — Open Items

Item IDs: `PW-Ox` power stage · `CT-Ox` controller and firmware · `SH-Ox` sensor hub · `PL-Ox` pilot.

## 1. Open

| ID | Item | Owner | Next step |
|---|---|---|---|
| CT-O5 | Field weakening above 3000 rpm | firmware | Bench test with the M-80 at 58 V |
| PL-O1 | Four drives for the AGV pilot | Mara Velden | Build and burn-in, July 2026 |
| PL-O2 | CAN message map agreed with the AGV controller | Mara Velden | Review with Brightwater Robotics |

## 2. Closed

| ID | Closed | Outcome |
|---|---|---|
| PW-O7 | 2026-04-30 | **Gate ringing on the high-side MOSFETs.** 14 V overshoot on the gate at turn-off. Fixed by a 4.7 Ω gate resistor per MOSFET (was 0 Ω) and a shorter gate loop on HB-P Rev B. Overshoot now 2.1 V. |
| CT-O3 | 2026-05-06 | **Bootloader accepted a corrupt image.** The CRC covered the header only. Fixed: CRC-32 over the whole image, checked before the jump. |
| SH-O2 | 2026-03-02 | **Encoder bit errors in the chassis.** SPI at 4 MHz over a 2 m cable beside the motor phases. Fixed by `D5`: RS-485. |
| PW-O4 | 2026-04-22 | DC-link capacitors ran 18 °C above ambient. Fixed by `D10` (680 µF). |
| CT-O2 | 2026-03-25 | Firmware did not fit in flash. Fixed by `D9` (C4-180). |
