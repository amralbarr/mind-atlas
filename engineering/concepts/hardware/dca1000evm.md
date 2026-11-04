# TI DCA1000EVM

The DCA1000EVM is a Texas Instruments **real-time data capture board** that streams *raw* ADC (analog-to-digital converter) data — the unprocessed IQ samples straight off a [mmWave radar](mmwave-radar.md) chip like the [IWR6843](ti-iwr6843isk-ods.md) — out to a host PC. It's the tool you reach for when TI's own on-chip [signal processing pipeline](radar-signal-processing-pipeline.md) (range FFT → Doppler → angle → point cloud) isn't what you want, and you need the raw radar cube to run your own custom DSP, or for research/offline analysis in tools like MATLAB.

## Why it exists

The radar chip's LVDS output can carry far more raw data (all ADC samples, all RX channels, every chirp) than a USB or UART link can practically sustain in real time. The DCA1000EVM solves this by bridging the chip's high-speed **LVDS** interface to **Gigabit Ethernet**, avoiding the bandwidth ceiling that a serial/USB link would hit when streaming multi-channel raw ADC data continuously.

## How it connects

```text
IWR6843 (raw ADC samples, LVDS)
        │
   DCA1000EVM (LVDS → Ethernet bridge)
        │
     Ethernet
        │
      Host PC (mmWave Studio / custom capture software)
```

It attaches to the antenna module via the same 60-pin connector used by the [MMWAVEICBOOST](mmwaveicboost.md), and integrates with TI's **mmWave Studio** software for automated capture sequences, real-time visualization, and recording raw captures to disk for offline processing.

## When you actually need it

For most application-level work — people tracking, point-cloud-based event detection, the kind of pipeline described in [Radar Point Cloud](radar-point-cloud.md) — you don't need the DCA1000EVM at all: the radar chip's on-chip processing already outputs a usable point cloud and tracked objects over a simple UART/USB link. The DCA1000EVM matters specifically when the project needs to:

- Develop or validate a **custom** radar signal-processing algorithm (different from TI's onboard firmware).
- Do offline research on raw waveform data (e.g. training an ML model directly on range-Doppler-angle cubes rather than post-processed detections).
- Debug or characterize the sensor's raw RF behavior.

## Related

- [TI IWR6843ISK-ODS](ti-iwr6843isk-ods.md)
- [MMWAVEICBOOST](mmwaveicboost.md)
- [Radar Signal Processing Pipeline](radar-signal-processing-pipeline.md)
- [Radar Point Cloud](radar-point-cloud.md)
