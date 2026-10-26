<!-- CONTRACT: REFERENCE — what the Tessaro GD-22 datasheet (Rev C) says. Never edited to match our design. -->

# Tessaro GD-22 half-bridge gate driver — datasheet notes

| Item | Datasheet value |
|---|---|
| Supply | 10–20 V gate supply, bootstrap high side up to 120 V |
| Peak gate current | 2.5 A source, 3.5 A sink |
| Minimum dead time | **120 ns** (programmable by resistor, 120 ns–1 µs) |
| Propagation delay | 45 ns typical |
| UVLO | 8.2 V rising |

The datasheet recommends a series gate resistor "between 2.2 Ω and 10 Ω to damp gate-loop ringing", and a gate loop
area "below 1 cm²". Application note AN-7 shows a 48 V, 30 A bridge switching at 20 kHz as its reference design.
