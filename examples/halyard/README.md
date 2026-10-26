<!-- CONTRACT: STATE — must be true now. The project entry point. -->

# Halyard — 48 V wheel-drive controller

*Synthetic example corpus for truthrag. Halyard, its parts, people and companies are invented.*

Halyard drives one brushless wheel motor of an automated guided vehicle (AGV) from a 48 V battery. Three boards:
**HB-P** (power stage: three-phase bridge, DC link, current sensing), **HB-C** (controller: Corvid C4-180 MCU,
field-oriented control, CAN), and **HB-S** (sensor hub: encoder receiver, motor thermistor, brake output).

## Status — 2026-06-12

| Item | Status | Current truth |
|---|---|---|
| HB-P Rev B power stage | ✅ Built, thermal test passed (TR-4) | [README](boards/HB-P_PowerStage/README.md) · [DesignNote](boards/HB-P_PowerStage/DesignNote.md) |
| HB-C Rev B controller | ✅ Built, FOC loop closed on the bench | [README](boards/HB-C_Controller/README.md) |
| HB-S sensor hub | ✅ Built; RS-485 encoder link verified at 2 m | [README](boards/HB-S_SensorHub/README.md) |
| Firmware | ◐ v0.9: FOC, CAN, bootloader; field weakening open (`CT-O5`) | [DesignNote](docs/DesignNote.md) |
| Pilot | ⬜ Four drives to Brightwater Robotics for the AGV pilot, July 2026 | [OpenItems](docs/OpenItems.md) |

## Where to read what

| You want | Read |
|---|---|
| The definitive numbers | [`docs/Parameters.md`](docs/Parameters.md) (`P-01`…`P-10`) |
| Every decision, one line each | [`docs/DesignNote.md`](docs/DesignNote.md) §4; full text in [`docs/DecisionLog.md`](docs/DecisionLog.md) |
| What is open | [`docs/OpenItems.md`](docs/OpenItems.md) |
| How to commission a drive | [`docs/Commissioning_Guide.md`](docs/Commissioning_Guide.md) |
| Wording a decision retired | [`docs/RetiredTerms.md`](docs/RetiredTerms.md) |

## Rules for the docs

- Every `.md` opens with `<!-- CONTRACT: STATE | REFERENCE | LOG -->`. **STATE** must be true now; **REFERENCE**
  is what an external source (a datasheet, a vendor note) says; **LOG** is history — only its `§0` is current.
- Anything under `archive/` is history and never a source of current values.
