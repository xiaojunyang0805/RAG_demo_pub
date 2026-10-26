<!-- CONTRACT: LOG — append-only; only §0 states current truth. -->

# HB-P worknote

## §0 CURRENT STATE *(2026-06-05, after TR-4)*

| | |
|---|---|
| Board | Rev B built, all bench tests passed |
| Values | PWM 24 kHz · limit 32 A · DC link 680 µF · shutdown 95 °C · connector 7.62 mm |
| Open | none on HB-P |

> ⛔ Below is the bench diary. Values in it were correct on the day and many are superseded.

## §1 Rev A bring-up, February 2026

The bridge switches at 20 kHz PWM. First spin at 12 V, then 24 V, then 48 V. Phase current limit set at 25 A in
firmware, matching the stall estimate. DC link is 470 µF; at 15 A phase current the capacitors warm by 9 °C.

Motor cable lands on the 5.08 mm terminal block. Fine at bench currents.

## §2 Gate ringing, March 2026

High-side gate shows 14 V overshoot at turn-off. Scope at the driver pin. Opened `PW-O7`. Tried a ferrite bead —
no change. A 4.7 Ω series resistor in each gate drops it to 3 V; Rev B layout will shorten the loop too.

## §3 Ripple, April 2026

At 25 A the 470 µF DC link carries 7.9 A rms and runs 18 °C above ambient. Rated 2.4 A rms per part at 105 °C.
Too hot. Opened `PW-O4`. Rev B: 4 × 170 µF.

## §4 Thermal, May 2026

Heat sink reaches 101 °C after 20 min at 25 A continuous with 20 kHz PWM in the closed chassis. The shutdown at
105 °C is never reached, but the capacitors next to the sink read 94 °C.

## §5 Stall test TR-3, 2026-05-14

M-80 locked rotor at 48 V: 31.2 A peak. The 25 A limit trips during a hill start. Limit raised to 32 A (`D8`);
the 5.08 mm connector (24 A) must go — 7.62 mm part ordered (`D12`).
