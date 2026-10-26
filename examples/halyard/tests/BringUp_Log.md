<!-- CONTRACT: LOG — append-only; only §0 states current truth. -->

# Halyard bring-up log

## §0 CURRENT STATE *(2026-06-10)*

| | |
|---|---|
| Last session | 2026-06-10: Rev B drive ran the M-80 in the AGV chassis for 2 h, no faults |
| Firmware | v0.9 |
| Next | Pilot build for Brightwater Robotics (`PL-O1`) |

> ⛔ Sessions below are history.

## Session 1 — 2026-02-18 (Rev A)

First power at 12 V, current limit 3 A on the supply. PWM 20 kHz. Motor spins open-loop. Encoder read over SPI.
Joris Kant on the scope.

## Session 2 — 2026-03-01 (Rev A, chassis)

Mounted in the AGV chassis with the 2 m encoder cable. SPI encoder reads show bit errors when the motor runs
(`SH-O2`). CAN at 500 kbit/s works but telemetry saturates the bus.

## Session 3 — 2026-04-07 (Rev A, chassis)

Brightwater Robotics' operators report a whine from the chassis at 20 kHz PWM. TR-1 noise survey scheduled.

## Session 4 — 2026-05-14 (Rev B)

TR-3 stall test: 31.2 A. Limit raised from 25 A to 32 A.

## Session 5 — 2026-06-10 (Rev B, chassis)

24 kHz PWM: no audible noise. 2 h run at 30 % duty, heat sink peaked at 71 °C.
