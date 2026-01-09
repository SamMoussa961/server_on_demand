import subprocess
import ipaddress
from wakeonlan import send_magic_packet
import re

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


"""
    DESC: Function validates broadcast address, Mac address and send magic packet if both are valid
    VARIABLES: mac_address(target mac address), broadcast_address(target broadcast address)
    RETURNS: Success if magic packet was successfully sent
    """
def send_magic(mac_address, broadcast_address):
    MAC_REGEX = re.compile(r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}')

    if not MAC_REGEX.fullmatch(mac_address):
        return False

    try:
        ipaddress.IPv4Address(broadcast_address)
        send_magic_packet(mac_address, ip_address=broadcast_address)
        return True
    except (ValueError, Exception):
        return False