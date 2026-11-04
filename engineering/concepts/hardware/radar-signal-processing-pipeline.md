# Radar Signal Processing Pipeline (Range → Doppler → Angle → Point Cloud → Tracking)

The chain of transformations that turns raw ADC samples from an [mmWave radar](mmwave-radar.md) into the thing an application actually wants — a list of tracked objects with position and velocity. On evaluation boards like the [TI IWR6843ISK-ODS](ti-iwr6843isk-ods.md), this whole chain runs on-chip; an application developer typically consumes only the final output and doesn't need to reimplement any of it.

## The pipeline

```text
Raw ADC samples (per chirp, per RX antenna)
         │
    Range FFT           → distance to each reflector
         │
   Doppler FFT           → radial velocity of each reflector
         │
 Angle-of-arrival estimation → azimuth / elevation direction
         │
   CFAR detection        → discard noise, keep real reflections
         │
    Clustering (DBSCAN)  → group nearby detections into objects
         │
  Point Cloud            → one frame's set of (x, y, z, velocity) points
         │
  Tracking (Kalman/EKF)  → persistent objects with an ID over time
         │
  Tracked Objects: {id, x, y, z, velocity, ...}
```

## Stage by stage

### Range FFT

The radar transmits an FMCW chirp (a linear frequency sweep) and mixes the transmitted and received signal to get an intermediate-frequency (IF) signal. Taking an FFT of the IF signal across the samples of a *single* chirp turns beat frequency into distance — a peak in the range FFT corresponds to a reflector at a specific range.

### Doppler FFT

A single chirp only gives range. To get radial velocity, the radar transmits a whole burst of chirps per frame and looks at how the *phase* at a given range bin changes chirp-to-chirp — a second FFT, taken across chirps (not within one), turns that phase progression into a velocity estimate via the Doppler effect.

### Angle-of-arrival (AoA) estimation

With multiple receive antennas (and the [virtual antenna array](mmwave-radar.md#txrx-antenna-arrays-and-virtual-antennas) synthesized via TX/RX multiplexing), the same reflection arrives at each antenna with a slightly different phase depending on its direction. A further FFT (or more advanced estimator like Capon/MUSIC) across the antenna dimension resolves azimuth and, if the antenna geometry supports it (like the [IWR6843ISK-ODS](ti-iwr6843isk-ods.md)'s ODS antenna), elevation too.

### CFAR detection

Constant False Alarm Rate thresholding — an adaptive noise-floor threshold applied to the range-Doppler-angle data to decide which cells are real reflections vs. background noise, without a fixed threshold that would either miss weak targets or flood the output with clutter as conditions change.

### Clustering

A single real-world object (a person) usually produces multiple nearby detections rather than one clean point. A clustering algorithm — commonly DBSCAN — groups spatially close detections in the current frame into a single object candidate, producing the frame's [point cloud](radar-point-cloud.md).

### Tracking

Frame-to-frame, a Kalman filter (or Extended Kalman Filter, since motion isn't purely linear) predicts where each already-tracked object should be, then associates new clusters to existing tracks (or spins up a new track / retires a stale one). This is what turns a sequence of disconnected point clouds into persistent, ID-stable objects that can be followed over time — including through brief radar dropouts, since the filter can coast on its prediction for a few frames.

## Why this matters for an application developer

Because vendor SDKs (like TI's mmWave SDK/Radar Toolbox) implement this entire chain on-chip, most projects never touch range/Doppler/angle math directly — they consume the final tracked-object stream and build application logic (zone rules, [sensor fusion](../robotics/sensor-fusion.md) with a camera, event detection) on top of it. Reimplementing this pipeline from raw ADC data (via a [DCA1000EVM](dca1000evm.md)) is only necessary for research or when the vendor's built-in tracking behavior doesn't fit the use case.

## Related

- [mmWave Radar](mmwave-radar.md)
- [Radar Point Cloud](radar-point-cloud.md)
- [TI IWR6843ISK-ODS](ti-iwr6843isk-ods.md)
- [DCA1000EVM](dca1000evm.md)
- [Sensor Fusion](../robotics/sensor-fusion.md)
