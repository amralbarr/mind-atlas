# mmWave Radar

mmWave (millimeter-wave) radar is a sensing modality that transmits radio signals in the 30–300 GHz band — in practice, consumer/industrial sensors cluster around 60 GHz and 77 GHz — and reconstructs the position, velocity, and shape of objects from the reflections. Unlike a camera, it doesn't produce an image: it produces a sparse **[point cloud](radar-point-cloud.md)** of detected reflectors, each with range, angle, and radial velocity. That makes it a fundamentally different kind of sensor from vision, with a different set of strengths and blind spots — see [Sensor Fusion](../robotics/sensor-fusion.md) for how the two get combined in practice.

## How it senses

An mmWave radar transmits a **chirp** — a signal whose frequency sweeps linearly over time (FMCW: Frequency-Modulated Continuous Wave) — and listens for the reflection. Mixing the transmitted and received chirp produces a low-frequency **intermediate frequency (IF)** signal whose frequency is proportional to the round-trip distance to the reflector. A burst of chirps per frame, across multiple receive antennas, is what lets the sensor extract range, velocity, *and* angle — see [Radar Signal Processing Pipeline](radar-signal-processing-pipeline.md) for how those are actually computed.

## TX/RX antenna arrays and virtual antennas

A single TX/RX antenna pair can only measure range and Doppler (radial velocity) — not direction. To resolve **angle of arrival**, a radar needs multiple antennas spaced apart so the same reflection arrives at each with a slightly different phase. Rather than wiring up a large physical antenna grid, mmWave radars exploit **MIMO (multiple-input, multiple-output)**: with *M* transmit and *N* receive antennas time- or code-multiplexed, the radar synthesizes *M × N* **virtual antenna positions** — e.g. TI's IWR6843 family uses 3 TX × 4 RX to synthesize 12 virtual receive channels, giving enough spatial diversity to estimate angle in both **azimuth** (horizontal) and **elevation** (vertical), which is what makes overhead/ceiling-mounted people-tracking installations possible instead of just a flat 2D azimuth-only field of view.

## Why it's useful alongside a camera

| Capability | Camera | mmWave radar |
|---|---|---|
| Classify *what* an object/action is | Strong | Very limited |
| Precise position, velocity, direction | Moderate (needs depth estimation/calibration) | Native output |
| Works in darkness / low light | Poor | Unaffected |
| Occlusion (partial/full) | Loses the object | Continues tracking through many occluders |
| Privacy | Captures identifiable imagery | No visual identity — reflections only |
| 3D motion (height, vertical movement) | Requires stereo/depth setup | Native (with elevation-capable antennas) |

Radar is largely blind to *what* is happening (a wave and a punch look similar in raw motion) but very good at *where* and *how fast* — which is why it's typically paired with a camera for action recognition rather than used alone. See [Sensor Fusion](../robotics/sensor-fusion.md), [Camera-Radar Calibration](../robotics/camera-radar-calibration.md), and [Radar Point Cloud](radar-point-cloud.md).

## Common form factors

- **Automotive radar (77 GHz)** — long range (100m+), used for ACC/AEB in vehicles.
- **Short-range industrial/consumer mmWave (60 GHz)** — shorter range (~10–15m) but finer resolution and available unlicensed spectrum worldwide; used for presence detection, gesture sensing, people counting/tracking. TI's [IWR6843ISK-ODS](ti-iwr6843isk-ods.md) is a 60 GHz example built specifically for overhead people-tracking.

## Related

- [TI IWR6843ISK-ODS](ti-iwr6843isk-ods.md)
- [Radar Signal Processing Pipeline](radar-signal-processing-pipeline.md)
- [Radar Point Cloud](radar-point-cloud.md)
- [Sensor Fusion](../robotics/sensor-fusion.md)
- [Camera-Radar Calibration](../robotics/camera-radar-calibration.md)
