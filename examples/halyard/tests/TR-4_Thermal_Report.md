<!-- CONTRACT: STATE — test report TR-4, results as measured. -->

# TR-4 — Thermal test, HB-P Rev B (2026-06-03)

## Setup

HB-P Rev B + HB-C Rev B in the closed AGV chassis, 25 °C ambient, M-80 on a dynamometer, 24 kHz PWM, 20 A rms
continuous phase current for 60 min, then 32 A peaks at 10 % duty.

## Results

| Point | Temperature after 60 min |
|---|---|
| Heat sink (NTC) | 88 °C |
| DC-link capacitors | 81 °C |
| MOSFET case, hottest | 97 °C |

## Finding

The DC-link capacitors sit 12 mm from the heat sink and track it at about −7 °C. Their life halves for every 10 °C
above 85 °C.
With the shutdown at 105 °C on the sink (the value before this test, now superseded), the capacitors could sit at 98 °C indefinitely.

## Decision

Thermal shutdown on the heat-sink NTC set to **95 °C** (`D11`), which keeps the capacitors at or below 88 °C.
