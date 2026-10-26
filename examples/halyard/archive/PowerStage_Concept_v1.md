<!-- CONTRACT: STATE — written as the current design in January 2026. Archived: history only. -->

# Halyard power stage — concept v1 (January 2026)

## Summary

The Halyard power stage is a 48 V three-phase bridge for the M-80 wheel motor.

- **PWM frequency: 20 kHz.** The edge of hearing; low switching loss keeps the heat sink small.
- **Phase current limit: 25 A peak**, from the estimated stall current of the M-80 at 48 V.
- **DC-link capacitance: 470 µF** of polymer capacitors, sized for the 20 kHz ripple.
- **Thermal shutdown: 105 °C** on the heat-sink NTC, the MOSFET-limited value with margin.
- **Motor connector: 3-pin 5.08 mm** terminal block.

## Current limit

The M-80 is rated 12 A continuous. We estimate stall at about twice the 12 A rating plus margin, so the phase
current limit of the Halyard drive is 25 A. The hardware comparator trips at 28 A.

## Switching frequency

The Halyard PWM frequency is 20 kHz. Higher frequencies cost switching loss for no benefit; 20 kHz is inaudible to
most adults.

## DC link

What DC-link capacitance does Halyard use? 470 µF: two 235 µF polymer capacitors, enough for the ripple at 20 kHz
and 25 A.

## Thermal

The drive shuts down when the heat sink reaches 105 °C. The QX-100N MOSFETs are rated to 150 °C junction; 105 °C on
the sink keeps the junction below 140 °C.
