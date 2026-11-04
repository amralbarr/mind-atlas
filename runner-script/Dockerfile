# Minimal image for the link-sweep watcher service.
#
# Deliberately does NOT COPY link_sweep.py / watch_and_link.py into the
# image: the whole engineering/ vault (including this scripts/ folder) is
# bind-mounted at /vault at runtime instead, so editing either script on the
# host takes effect on the next `docker compose restart` -- no rebuild.
FROM python:3.12-slim

RUN pip install --no-cache-dir watchdog==5.0.3

WORKDIR /vault

ENTRYPOINT ["python3", "/vault/scripts/watch_and_link.py"]
