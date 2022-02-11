import subprocess
from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, HTTPServer

class wg_metrics_handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if(self.path == '/metrics'):
            result = subprocess.run(['wg', 'show', 'all', 'dump'], capture_output=True, text=True)
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            message = self.parse_wg_output(result.stdout)
            self.wfile.write(bytes(message, 'utf-8'))
    
    def parse_wg_output(self, wg_output):
        # Check the doc for the output format: https://manpages.debian.org/unstable/wireguard-tools/wg.8.en.html#show
        self.wg_interface = ''
        self.connected_peers = 0
        lines = wg_output.splitlines()
        parsed_result = self.parse_server_info(lines[0].split('\t'))
        for peer_info in lines[1:]: # will be empty if no peers
            parsed_result += self.parse_peer_info(peer_info.split('\t'))
        parsed_result += f'wg_connected_peers{{interface="{self.wg_interface}"}} {self.connected_peers}\n'
        return parsed_result
    
    def parse_server_info(self, server_info):
        self.wg_interface = server_info[0]
        return f'wg_server_info{{pkey="{server_info[2]}", interface="{server_info[0]}"}} {server_info[3]}\n'
    
    def parse_peer_info(self, peer_info):
        peer_latest_handshake = f'wg_peer_latest_handshake{{pkey="{peer_info[1]}", interface="{peer_info[0]}"}} {peer_info[5]}\n'
        peer_latest_transfer_rx = f'wg_peer_transfer_rx{{pkey="{peer_info[1]}", interface="{peer_info[0]}"}} {peer_info[6]}\n'
        peer_latest_transfer_tx = f'wg_peer_transfer_tx{{pkey="{peer_info[1]}", interface="{peer_info[0]}"}} {peer_info[7]}\n'
        peer_ip_address = peer_info[4].split('/')[0]
        is_peer_up = 1 if subprocess.run(['ping', '-W', '1', '-c', '1', '-t','1', peer_ip_address], capture_output=True).returncode == 0 else 0
        peer_connection_status = f'wg_peer_connection_status{{pkey="{peer_info[1]}", interface="{peer_info[0]}"}} {is_peer_up}\n'
        if(is_peer_up):
            self.connected_peers += 1
        return peer_latest_handshake + peer_latest_transfer_rx + peer_latest_transfer_tx + peer_connection_status


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--bind', type=str, help='The interface to bind the server to. Defaults to localhost', default='127.0.0.1')
    parser.add_argument('--port', type=int, help='The port to listen to', default=8400)
    args = parser.parse_args()
    with HTTPServer((args.bind, args.port), wg_metrics_handler) as server:
        server.serve_forever()
