# ROS2 (Robot Operating System 2)

ROS2 is an open-source **[middleware](../backend/middleware.md) framework for robotics and multi-sensor systems** — not an operating system in the kernel sense, but a set of libraries, conventions, and tooling for structuring a program as a graph of independent processes (**nodes**) that communicate over well-defined channels (**topics**, **services**, **actions**) instead of calling each other directly. It's built on **DDS (Data Distribution Service)**, a [publish-subscribe](../distributed-systems/messaging/publish-subscribe.md) [middleware](../backend/middleware.md) standard, which ROS2 wraps with a simpler ROS-specific interface while exposing DDS's quality-of-service (QoS) configuration where needed.

## Core concepts

| Term | Meaning |
|---|---|
| **Node** | An independent process — e.g. a camera driver, a detector, a fusion engine — each a separate unit of code and deployment |
| **Topic** | A named [pub/sub](../distributed-systems/messaging/publish-subscribe.md) channel nodes publish/subscribe to (e.g. `/camera/image`, `/radar/tracks`) — decouples publishers from subscribers entirely |
| **Message** | The typed data structure sent over a topic (e.g. `sensor_msgs/PointCloud2`) |
| **Service** | A synchronous request/response call between nodes, for one-off queries rather than continuous streams |
| **Action** | A long-running, cancelable, progress-reporting request (e.g. "navigate to point X") |
| **Launch file** | Declarative configuration for starting a whole graph of nodes together with their parameters |
| **QoS (Quality of Service)** | Per-topic tuning (reliability, durability, history depth) inherited from DDS — e.g. best-effort vs. reliable delivery |

A typical graph looks like:

```text
Camera Node → /camera/image → Detection Node → /detections ─┐
                                                              ├→ Fusion Node
Radar Node  → /radar/tracks ─────────────────────────────────┘
```

## When it earns its complexity

ROS2 is genuinely valuable once a system has most of the following, at once:

- Several heterogeneous sensors (camera, radar, LiDAR, IMU, GPS) that all need independent drivers.
- A need to swap/upgrade individual components (a detector, a driver) without touching the rest of the system.
- Multiple computers/processes that need to communicate over a network transparently.
- Existing hardware drivers already published as ROS2 packages (many sensor vendors, including Texas Instruments' [mmWave radar](../hardware/mmwave-radar.md) line, ship a ROS2 node) — using them as-is avoids writing a driver from scratch.
- A roadmap toward navigation, SLAM, motion planning, or other genuinely robotic capabilities where the wider ROS2 ecosystem (Nav2, TF for coordinate frames, RViz for visualization) pays for itself.

## When it's not needed

For a first version of a project with a fixed, small number of sensors (e.g. one camera + one radar) feeding a single fusion/decision pipeline on one machine, ROS2 adds a layer of ceremony — nodes, topics, message types, launch files, DDS discovery/QoS tuning — that a plain application doesn't need. A direct pipeline is simpler to build, run, and debug:

```text
Camera → OpenCV/RTSP → Detector/Tracker ─┐
                                          ├→ Sensor Fusion → Event Detection → Alerts
Radar  → Vendor SDK / Serial ────────────┘
```

implemented as ordinary Python/C++ modules calling each other directly (or via a lightweight queue if some decoupling is wanted), with no ROS2 dependency at all.

## The upgrade path is real

Because ROS2's node/topic model maps cleanly onto "swap a direct function call for a publish/subscribe channel," a project that starts without ROS2 isn't locked out of adopting it later — each existing pipeline stage (camera capture, detection, radar driver, fusion) can become a node with comparatively little redesign once the system's scope genuinely grows to justify it (more sensors, more machines, a move toward general robotics/navigation). Starting without it and adding it if/when needed is a reasonable default, rather than adopting it upfront "in case."

## Related

- [Sensor Fusion](sensor-fusion.md)
- [Sensor Synchronization](sensor-synchronization.md)
- [mmWave Radar](../hardware/mmwave-radar.md)
