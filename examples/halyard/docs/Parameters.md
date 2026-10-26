<!-- CONTRACT: STATE — must be true now. The definitive numbers. -->

# Halyard — Parameters

Each parameter has one value, an evidence class (**M** measured · **D** derived · **A** assumed · **V** vendor) and
its source. When a value changes, the old one is kept in brackets with the decision that replaced it.

| ID | Parameter | Value | Class | Source |
|---|---|---|---|---|
| **P-01** | Battery bus, nominal | **48 V** (40–58 V operating) | A | AGV battery spec from Brightwater Robotics |
| **P-02** | Phase current limit | **32 A** peak per phase *(was 25 A, an estimate; replaced by the measured stall current, `D8`)* | M | TR-3 stall test, 2026-05-14 |
| **P-03** | PWM frequency | **24 kHz** *(was 20 kHz; moved out of the audible band, `D7`)* | D | `D7`; TR-1 noise survey |
| **P-04** | DC-link capacitance | **680 µF** (4 × 170 µF polymer) *(was 470 µF; ripple current too high, `D10`)* | M | TR-2 ripple measurement |
| **P-05** | Thermal shutdown, heat-sink NTC | **95 °C** *(was 105 °C; capacitor lifetime, `D11`)* | D | TR-4 thermal report |
| **P-06** | CAN bit rate | **1 Mbit/s** *(was 500 kbit/s; `D6`)* | D | `D6` |
| **P-07** | Gate-driver dead time | **150 ns** (vendor minimum 120 ns) | V | Tessaro GD-22 note |
| **P-08** | Current-sense shunt | **1 mΩ**, 3 W, per low-side leg | D | HB-P DesignNote §3 |
| **P-09** | Control loop rate | **24 kHz** current loop (one update per PWM period), 2 kHz speed loop | D | `D3`, `D7` |
| **P-10** | Encoder resolution | **4096** counts per revolution, absolute | V | Motor M-80 datasheet note |

## Notes

- `P-02` and the motor connector (`D12`) move together: 32 A per phase is above the rating of the 5.08 mm connector it replaced.
- `P-03` sets `P-09`: the current loop runs once per PWM period, so the loop rate followed the move to 24 kHz.
