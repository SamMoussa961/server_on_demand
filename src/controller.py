from src.wake_server import ping_host
from src.wake_server import send_magic
from src.fetch import process_results

def ensure_awake(ip):
    if ping_host(ip):
        return True
    return False

def controller(ip_address, mac_address, broadcast_address, api_url, api_key, how_long, skip_wol=False):
    active = process_results(api_url, api_key, how_long)

    if not active:
        return "no_activity"

    if ensure_awake(ip_address):
        return "already_on"

    if skip_wol:
        return "wol_skipped"

    return "wol_sent" if send_magic(mac_address, broadcast_address) else "wol_failed"