# TI IWR6843ISK-ODS

The IWR6843ISK-ODS is a Texas Instruments evaluation module for the [mmWave radar](mmwave-radar.md) — specifically the **Overhead Detection Sensor (ODS)** antenna variant of the IWR6843 60 GHz single-chip radar. It's an antenna-plug-in module, not a standalone USB device: TI documents it as normally paired with the [MMWAVEICBOOST](mmwaveicboost.md) carrier board for development, and with the [DCA1000EVM](dca1000evm.md) when raw ADC access is needed.

## What's on the board

- **IWR6843** — a single-chip 60–64 GHz [mmWave radar](mmwave-radar.md) transceiver with on-chip processing: a C67x DSP core, a hardware accelerator (HWA) for FFT/CFAR-style operations, and a low-power ARM Cortex-R4F controller. Signal processing (see [Radar Signal Processing Pipeline](radar-signal-processing-pipeline.md)) largely runs on-chip, so a host computer receives processed output rather than raw RF.
- **3 TX / 4 RX antenna array**, etched directly on the board (a Rogers substrate), synthesizing the 12-channel virtual antenna array described in [mmWave Radar](mmwave-radar.md#txrx-antenna-arrays-and-virtual-antennas).
- **ODS antenna geometry**: unlike the standard IWR6843ISK (wide azimuth, narrow elevation), the ODS variant is etched for a roughly **120° × 120°** azimuth-and-elevation field of view, and a documented range on the order of **12–15 m** for people detection — a shape specifically intended for a sensor mounted overhead (ceiling-mounted) looking down, rather than mounted at eye level looking across a room.

## Why the ODS variant matters

A standard forward-facing automotive-style radar antenna gives wide horizontal coverage but very little vertical (elevation) field of view — fine for a car looking down a road, useless for a sensor mounted on a ceiling that needs to see people directly underneath it. The ODS antenna trades some azimuth range for genuine elevation coverage, which is what makes overhead people-counting/tracking installations (train platforms, retail aisles, room occupancy) practical with this sensor family.

## Software stack

TI doesn't expect you to reimplement radar DSP from scratch. The **mmWave SDK / Radar Toolbox** already implements the chip-side chain (range FFT → Doppler FFT → angle estimation → CFAR detection → clustering → tracking) and ships example applications built specifically for this hardware, notably:

- **3D People Tracking** — general multi-person 3D tracking from a room-mounted radar.
- **Overhead 3D People Tracking** — the application built specifically for the ISK-ODS antenna geometry, explicitly supporting people who are standing, sitting, or lying down and remain stationary (relevant for fall/stuck-person detection use cases).

The host application (running on a PC, Raspberry Pi, or similar) receives already-processed output over UART/USB — [point cloud](radar-point-cloud.md) detections and tracked-object records (position, velocity, ID) — rather than raw ADC samples, unless a [DCA1000EVM](dca1000evm.md) is attached for raw-data capture.

## Related

- [mmWave Radar](mmwave-radar.md)
- [MMWAVEICBOOST](mmwaveicboost.md)
- [DCA1000EVM](dca1000evm.md)
- [Radar Signal Processing Pipeline](radar-signal-processing-pipeline.md)
- [Radar Point Cloud](radar-point-cloud.md)
- [Sensor Fusion](../robotics/sensor-fusion.md)
