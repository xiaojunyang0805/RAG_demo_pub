<!-- CONTRACT: STATE — must be true now. HB-P as built, with reasons. -->

# HB-P Design Note (Rev B)

## 1. Switching

PWM runs at 24 kHz. At 20 kHz the AGV chassis resonated audibly (TR-1); 24 kHz is above the band. Switching
loss at 24 kHz and 32 A is 6.4 W per board, 1.1 W more than at 20 kHz, and the heat sink absorbs it at the 95 °C
shutdown point.

## 2. DC link

Four 170 µF polymer capacitors, 680 µF total. TR-2 measured 9.8 A rms ripple at 32 A phase current; each part is
rated 3.2 A rms, so four carry it with 30 % margin. The capacitors sit 12 mm from the heat sink, which is why the
thermal shutdown is set by their lifetime (`D11`).

## 3. Current sensing

One 1 mΩ, 3 W shunt per low-side leg. At 32 A the shunt drops 32 mV; the ×20 amplifier maps ±40 A to the ADC
range. The hardware over-current comparator trips at 35 A, independent of firmware.

## 4. Gate drive

Tessaro GD-22 drivers. Rev A had no gate resistor and rang 14 V above the rail at turn-off (`PW-O7`); Rev B fits
4.7 Ω per MOSFET and shortens the gate loop to 9 mm. Measured overshoot: 2.1 V.

## 5. Connector

Phase currents up to 32 A need the 7.62 mm terminal block (41 A rating). The motor cable is 2.5 mm² per phase.
