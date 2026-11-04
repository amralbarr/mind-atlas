# Installing Docker (Linux)

For the conceptual overview — images, containers, volumes, and networks — see [Docker](../../concepts/containers/docker.md). This page is a short install stub for [Docker Engine](../../concepts/containers/docker-daemon.md) on Linux.

## Install

```bash
# Debian/Ubuntu
sudo apt update && sudo apt install docker.io docker-compose-plugin

# Fedora/RHEL
sudo dnf install docker docker-compose-plugin
```

Add your user to the `docker` group so you don't need `sudo` for every command, then enable and start the systemd service:

```bash
sudo usermod -aG docker $USER
newgrp docker

sudo systemctl enable --now docker
```

Verify with `docker run hello-world`.
