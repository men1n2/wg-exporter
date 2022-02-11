# wg-exporter
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/C0C8AHIE0)

*wg-exporter* is a simple yet effective Prometheus exporter for Wireguard.

## What are the collected metrics ?
- General:
    - `wg_connected_peers`: number of connected peers to the VPN server
- Server:
    - `wg_server_info{pkey, interface}`: the listen port of the VPN server, labeled by the public key of the server, and the interface name
- Peers: (All labeled by the public key of the peer and the interface name connected to)
    - `wg_peer_latest_handshake{pkey, interface}`: unit timestamp of the last handshake
    - `wg_peer_transfer_rx{pkey, interface}`: data received in bytes
    - `wg_peer_transfer_tx{pkey, interface}`: data transmitted in bytes
    - `wg_peer_connection_status{pkey, interface}`: is the peer connected now ? 0 for False, 1 for True

## Install
Clone the project
```bash
git clone git@github.com:men1n2/wg-exporter.git
```

## Usage
After running your Wireguard interface, run the script using sudo (it needs the rights to execute "`wg show all`"):
```
sudo python3 src/app.py
```
And that's it :) The exporter will listen by default to port `8400`.

Add the exporter to your `scrape_configs` in your prometheus `.yml` config file:
```yml
scrape_configs:

  - job_name: "wg"
    static_configs:
      - targets: ["localhost:8400"]
```
