import subprocess
import ipaddress
from wakeonlan import send_magic_packet

"""
    DESC: Function validates ip address, pings ip once. Designed for bash
    VARIABLES: ip address, timeout defaults to 5 seconds
    RETURNS: Success if ip address was successfully ping
"""
def ping_host(ip, timeout=5):

    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        return False

    command = ['ping', '-c', '1', ip]

    try:
        response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        return response.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def check_and_wake(ip, mac_address, broadcast_address):
    if ping_host(ip):
        return True
    else:
        try:
            send_magic_packet(mac_address, ip_address=broadcast_address)
            return True
        except Exception:
            return False