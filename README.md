# server_on_demand

## Summary

This project automatically powers on a jellyfin storage server on whenever user activity is detected. 

The goal is to reduce unnecessary power consumption by keeping a high-power storage machine offline until is actually needed, while still providing a good experience for jellyfin users.

## Motivation

My media library is hosted on a high-power machine, that is inefficient to run 24/7 or on fixed schedule. Instead, I use a low-power server as the primary Jellyfin host and wake the storage server only when user activity occurs.

This project serves two purposes:
- Practical: Reduce power usage without impacting user experience.
- Educational: Practice systems programming, API integration, networking, and hardware interaction (Wake on Lan).

## High Level Architecture

- Server A (Low-power / Always on)
    - Runs Jellyfin in Docker
    - Runs this monitoring service
- Server B (High-power / Storage)
    - Hosts media storage
    - Woken via wake on lan When needed

## Flow

1. A Python service polls the Jellyfin API at a configurable interval.
2. if active users or playback sessions are detected:
    - A Wake-on-Lan magic packet is sent to Server B.
3. A cooldown period prevents repeated wake requests.

## Features

- Jellyfin API polling for active sessions
- Wake-on-Lan trigger via MAC Address
- Configurable polling interval and cooldown
- Designed to run as a lightweight container or service

## Prerequisites

### Software 

- [Docker](https://docs.docker.com)
- [Docker Compose](https://wiki.archlinux.org/title/Docker#:~:text=deprecated%20legacy%20builder.-,Docker%20Compose,-Docker%20Compose%20is)
- [Python](https://wiki.archlinux.org/title/Python) 3.x
- [Jellyfin](https://jellyfin.org/docs/general/installation/container) (Docker container)

### Python Dependencies

- wakeonlan
- requests

### Hardware

- Server A: Low-power machine (e.g. tiny PC)
- Server B: Storage server with Wake-on-Lan

## Configuration 

The application is configured via environment variables:

| Variable                  | Description                                   |
| :---                      |   :----                                       |
| STORAGE_SERVER_MAC        | MAC address of server B                       |
| BROADCAST_ADDRESS         | Network broadcast address                     |
| JELLYFIN_API_URL          | Jellyfin server Jellyfin server [API endpoint](https://api.jellyfin.org/) |
| JELLYFIN_API_KEY          | Jellyfin API key                              |
| CHECK_INTERVAL            | Polling interval (seconds)                    |
| PACKET_COOLDOWN_TIME      | Minimum time between WOL packets              |
| COOLDOWN_TIME             | Minimum inactivity time to poweroff server B  |


## Status

This project is currently in active development and primarily intended as a learning and experimentation tool. Statbility and edge cases are still being refined.


## Future Improvements

- TODO

