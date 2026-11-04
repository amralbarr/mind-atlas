# RTSP (Real-Time Streaming Protocol)

RTSP is a network **control** protocol — standardized as RFC 2326 in 1998 — for establishing and controlling a media streaming session between a client and a server: think VCR-style commands (`PLAY`, `PAUSE`, `TEARDOWN`) sent over the network rather than the video itself. It remains the dominant protocol for how IP cameras, NVRs (network video recorders), and DVRs publish live video in surveillance/CCTV systems, which is where it most commonly shows up in a computer-vision pipeline that ingests live camera feeds.

## RTSP controls the session, RTP carries the media

This is the detail that trips people up: RTSP itself doesn't transport audio/video data. It's a request-response control protocol, typically over [TCP](../networking/tcp.md) on port 554, that negotiates and controls a session; the actual media is delivered by a separate protocol — usually **RTP (Real-time Transport Protocol)** over UDP (or sometimes tunneled over [TCP](../networking/tcp.md)).

```text
Client                          Camera (RTSP server)
  │── DESCRIBE ──────────────────────▶│   (what streams are available?)
  │◀───────── SDP description ────────│
  │── SETUP ─────────────────────────▶│   (negotiate transport, ports)
  │◀───────── 200 OK ──────────────────│
  │── PLAY ──────────────────────────▶│   (start streaming)
  │◀═══ RTP video/audio packets ══════│   (actual media, separate stream)
  │── TEARDOWN ──────────────────────▶│   (end session)
```

## Typical RTSP URL

```text
rtsp://username:password@192.168.1.50:554/stream1
```

Most IP cameras expose one or more RTSP endpoints (often a high-resolution "main" stream and a lower-resolution "sub" stream) that any RTSP-capable client can pull continuously.

## Where it fits in a video pipeline

```text
IP Camera → RTSP stream ──▶ OpenCV (cv2.VideoCapture) / FFmpeg ──▶ frames ──▶ YOLO / detection pipeline
```

In Python, OpenCV can open an RTSP stream directly the same way it opens a local video file:

```python
import cv2

cap = cv2.VideoCapture("rtsp://192.168.1.50:554/stream1")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    # frame → detection / tracking / pose pipeline
```

## Why it's still the default for CCTV, despite its limitations

RTSP's ~1–2 second latency is entirely acceptable for monitoring/recording use cases (unlike, say, live interactive video), and because it's built into camera firmware at the hardware level, there's no per-device software licensing cost the way there might be with a proprietary vendor SDK. Its main practical limitation is that **web browsers don't natively support RTSP playback** — viewing a raw RTSP stream in a browser-based dashboard typically requires transcoding it to a browser-friendly protocol (e.g. HLS or [WebSockets](../networking/websockets.md)-based relay) on a server in between, rather than pointing a `<video>` tag directly at the RTSP URL.

## Related

- [WebSockets](../networking/websockets.md) — common relay target when a browser dashboard needs to display an RTSP feed
- [Server-Sent Events (SSE)](sse.md) — a different one-way streaming pattern, more commonly used for structured event data than raw video
- [YOLO](../ai/computer-vision/yolo.md) — the typical next stage after frames are pulled off an RTSP stream
