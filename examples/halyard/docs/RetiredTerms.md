<!-- CONTRACT: STATE — wording a decision has retired. -->

# Halyard — Retired terms

When a decision makes a description wrong, its pattern goes here. A line that matches is **not** stale when it
marks itself as history: it contains the retiring ID, or *was*, *not*, *no longer*, *superseded*, *replaced*,
*formerly*, `~~`.

| Pattern (regex, case-insensitive) | Retired by | Use instead |
|---|---|---|
| `25 ?A (phase )?(current )?limit\|limit (of\|at) 25 ?A` | `D8` | Phase current limit 32 A (measured stall 31.2 A) |
| `20 ?kHz PWM\|PWM (at\|of) 20 ?kHz` | `D7` | PWM 24 kHz |
| `470 ?µF` | `D10` | DC link 680 µF |
| `105 ?°C` | `D11` | Thermal shutdown 95 °C |
| `500 ?kbit/s` | `D6` | CAN 1 Mbit/s |
| `C4-120` | `D9` | Corvid C4-180 |
| `encoder[^\n]{0,30}SPI\|SPI[^\n]{0,30}encoder` | `D5` | RS-485 encoder link |
| `5\.08 ?mm` | `D12` | Motor connector 7.62 mm |
