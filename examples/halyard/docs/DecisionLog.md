<!-- CONTRACT: LOG — append-only history; only §0 is current. -->

# Halyard — Decision Log

## §0 CURRENT STATE *(last verified 2026-06-12 against DesignNote §4 and Parameters)*

| ID | Decision | Status |
|---|---|---|
| D5 | Encoder link RS-485 | ✅ Frozen 2026-03-02 |
| D6 | CAN 1 Mbit/s | ✅ Frozen 2026-03-20 |
| D7 | PWM 24 kHz | ✅ Frozen 2026-04-08 |
| D8 | Phase current limit 32 A | ✅ Frozen 2026-05-14 |
| D9 | MCU Corvid C4-180 | ✅ Frozen 2026-03-25 |
| D10 | DC link 680 µF | ✅ Frozen 2026-04-22 |
| D11 | Thermal shutdown 95 °C | ✅ Frozen 2026-06-03 |
| D12 | Motor connector 7.62 mm | ✅ Frozen 2026-05-20 |

> ⛔ Below this line is the record of how we got here. It keeps superseded reasoning on purpose.

## §1 Early decisions (January–February 2026)

**D5 (first form, 2026-01-20).** The encoder talks SPI to the MCU. The encoder sits 20 cm from HB-C on the bench,
SPI at 4 MHz is simple, and the MCU has a free SPI port. Encoder link: SPI.

**D6 (first form).** CAN at 500 kbit/s, the AGV controller's default. The bus is short and 500 kbit/s leaves margin.

**D7 (first form).** PWM at 20 kHz: the edge of hearing, and the switching loss at 20 kHz keeps the heat sink small.

**Current limit (estimate, 2026-02-10).** Motor M-80's rated current is 12 A continuous; we estimate a stall peak
of 25 A and set the phase current limit at 25 A.

**DC link (first estimate).** 470 µF of polymer capacitors, sized from the 20 kHz ripple estimate.

**MCU (Rev A).** Corvid C4-120: 256 KB flash, 120 MHz, enough for six-step control with margin.

## §2 Revisions (March–June 2026)

**D5 revised, 2026-03-02.** In the chassis the encoder cable is 2 m and runs beside the motor phases. SPI at 4 MHz
failed with bit errors on the first chassis test (`SH-O2`). The link moves to RS-485 (differential, 2.5 Mbit/s).
SPI is no longer used for the encoder.

**D9, 2026-03-25.** FOC plus the bootloader needs 310 KB of flash, above the C4-120's 256 KB. Rev B moves to the
Corvid C4-180 (512 KB, 180 MHz).

**D6 revised, 2026-03-20.** At 500 kbit/s the 2 kHz speed loop's telemetry used 71 % of the bus. Raised to 1 Mbit/s.

**D7 revised, 2026-04-08.** The pilot customer's operators heard a whine at 20 kHz inside the AGV chassis (TR-1:
the chassis resonates near 19.6 kHz). PWM moves to 24 kHz. The extra switching loss is ≈ 1.1 W per board, inside
the thermal budget.

**D10, 2026-04-22.** TR-2 measured 9.8 A rms ripple in the DC link at 32 A phase current; four 170 µF polymer
parts (680 µF) carry it within rating. 470 µF ran 18 °C above ambient.

**D8, 2026-05-14.** TR-3 measured a stall current of 31.2 A on motor M-80 at 48 V. The limit is set at 32 A; the
25 A estimate would have tripped during normal hill starts.

**D12, 2026-05-20.** The 5.08 mm motor connector is rated 24 A; 32 A per phase (`D8`) needs the 7.62 mm part
(rated 41 A).

**D11, 2026-06-03.** At 105 °C on the heat sink, the DC-link capacitors next to it reach 98 °C, which halves their
lifetime. TR-4 sets the shutdown at 95 °C on the heat-sink NTC.
