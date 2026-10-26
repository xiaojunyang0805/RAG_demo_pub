<!-- CONTRACT: STATE — must be true now. How to commission a Halyard drive. -->

# Commissioning a Halyard drive

## 1. Before power

- Motor phases on the 7.62 mm terminal block: U, V, W from left to right seen from the connector side.
- Encoder cable (RS-485) from the M-80 to HB-S; brake to HB-S `J3`.
- CAN to the AGV controller, 1 Mbit/s; fit the termination jumper on the last node only.

## 2. First power

1. Bench supply at 24 V, current limit 2 A. The status LED blinks green at 1 Hz.
2. Read the parameter block over CAN (`0x6F0`): check PWM = 24000 Hz, current limit = 32 A, thermal limit = 95 °C.
3. Raise to 48 V.

## 3. Encoder alignment

Send `ALIGN` (CAN `0x6F1`, byte 0 = 0x01). The drive injects 8 A on the d-axis for 2 s and stores the encoder
offset. Repeat after any motor or encoder change.

## 4. Faults

| Code | Meaning | Action |
|---|---|---|
| F1 | Over-current (> 35 A hardware or > 35.2 A firmware) | Check phase wiring and the motor for shorts |
| F2 | Heat sink above 95 °C | Let it cool; check the fan and chassis airflow |
| F3 | Encoder fault | Check the RS-485 cable and HB-S power |
| F4 | CAN timeout (50 ms) | Check the AGV controller and the bus termination |
| F5 | Bus over-voltage (> 60 V) | Check the regen resistor |
