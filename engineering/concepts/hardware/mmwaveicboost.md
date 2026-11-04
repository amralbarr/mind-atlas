# TI MMWAVEICBOOST

The MMWAVEICBOOST is a Texas Instruments **carrier/debug board** for its 60 GHz mmWave antenna modules, including the [IWR6843ISK-ODS](ti-iwr6843isk-ods.md). It's not a sensor itself — the radar chip and antennas live on the plug-in antenna module (ISK/ODS/AOP variants), and the MMWAVEICBOOST is the board that provides power, USB connectivity, and debugging infrastructure so that module can actually talk to a host computer.

## What it provides

- A **60-pin connector** that the antenna module (e.g. IWR6843ISK-ODS) plugs into.
- **USB connectivity** for flashing firmware, streaming the processed output (point cloud, tracked objects) to a host PC, and running TI's configuration/visualization tools.
- **Advanced debug features** via TI's Code Composer Studio (CCS)-compatible debugger — trace and single-step debugging of the code running on the radar chip's onboard DSP/MCU, useful when developing or modifying the signal-processing firmware itself rather than just consuming its output.
- A path to attach a [DCA1000EVM](dca1000evm.md) alongside it when raw ADC data (rather than the chip's already-processed point cloud) is needed.

## Where it fits in the setup

```text
       IWR6843ISK-ODS  (antenna module — the actual radar)
              │
        60-pin connector
              │
       MMWAVEICBOOST    (carrier/debug board)
              │
             USB
              │
          Host PC
```

For a project that just needs the processed point cloud/tracking output — not raw ADC capture or firmware-level debugging — the MMWAVEICBOOST plus antenna module plus USB cable is the complete hardware chain to a laptop; a [DCA1000EVM](dca1000evm.md) is only needed on top when raw IQ/ADC data must be captured for custom offline signal processing.

## Related

- [TI IWR6843ISK-ODS](ti-iwr6843isk-ods.md)
- [DCA1000EVM](dca1000evm.md)
- [mmWave Radar](mmwave-radar.md)
- [Radar Signal Processing Pipeline](radar-signal-processing-pipeline.md)
