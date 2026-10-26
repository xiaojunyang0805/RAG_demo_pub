<!-- CONTRACT: STATE — must be true now. HB-P spec sheet. -->

# HB-P — Power stage (Rev B)

| | |
|---|---|
| Size | 110 × 80 mm, 4 layers, 2 oz outer copper |
| Bridge | 3 half-bridges, 6 × QX-100N (100 V, 2.1 mΩ), one per switch |
| Gate drive | 3 × Tessaro GD-22 half-bridge drivers, 4.7 Ω gate resistor per MOSFET (`PW-O7`) |
| Dead time | 150 ns (`P-07`) |
| DC link | **680 µF**: 4 × 170 µF 63 V polymer (`D10`) |
| Current sense | 1 mΩ low-side shunt per leg, amplified ×20 into the HB-C ADC |
| PWM | **24 kHz** (`D7`), centre-aligned |
| Phase current limit | **32 A** peak (`D8`), hardware comparator at 35 A as a backstop |
| Motor connector | 3-pin **7.62 mm** pitch terminal block, rated 41 A (`D12`) |
| Thermal | Heat-sink NTC; drive stops at **95 °C** (`D11`) |

## Status

Rev B built and tested: TR-2 ripple, TR-3 stall, TR-4 thermal all passed.
Rev A (C4-120 controller, 470 µF, 5.08 mm connector) is retired; its notes are in `archive/`.
