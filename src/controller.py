from src.wake_server import ping_host
from src.wake_server import send_magic
from src.fetch import process_results

def ensure_awake(ip):
    if ping_host(ip):
        return True
    return False

def controller(ip_address, mac_address, broadcast_address, api_url, api_key, how_long):
    active = process_results(api_url, api_key, how_long)

    if not active:
        return False

    if ensure_awake(ip_address):
        return True

    return send_magic(mac_address, broadcast_address)