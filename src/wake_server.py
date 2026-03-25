import logging
import subprocess
import ipaddress
from wakeonlan import send_magic_packet
import re

logger = logging.getLogger(__name__)

"""
    DESC: Function validates ip address, pings ip once. Designed for bash
    VARIABLES: ip address, timeout defaults to 5 seconds
    RETURNS: Success if ip address was successfully ping
"""
def ping_host(ip, timeout=5):

    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        logger.warning("ping_host called with invalid IP address: %r", ip)
        return False

    logger.debug("Pinging %s (timeout: %ds)", ip, timeout)
    command = ['ping', '-c', '1', ip]

    try:
        response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        result = response.returncode == 0
        logger.debug("Ping %s: %s", ip, "reachable" if result else "unreachable")
        return result
    except subprocess.TimeoutExpired:
        logger.warning("Ping timed out after %ds for %s", timeout, ip)
        return False


"""
    DESC: Function validates broadcast address, Mac address and send magic packet if both are valid
    VARIABLES: mac_address(target mac address), broadcast_address(target broadcast address)
    RETURNS: Success if magic packet was successfully sent
    """
def send_magic(mac_address, broadcast_address):
    MAC_REGEX = re.compile(r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}')

    if not MAC_REGEX.fullmatch(mac_address):
        logger.warning("send_magic called with invalid MAC address: %r", mac_address)
        return False

    try:
        ipaddress.IPv4Address(broadcast_address)
    except ValueError:
        logger.warning("send_magic called with invalid broadcast address: %r", broadcast_address)
        return False

    logger.info("Sending WoL magic packet to %s via broadcast %s", mac_address, broadcast_address)
    try:
        send_magic_packet(mac_address, ip_address=broadcast_address)
        logger.info("WoL packet sent successfully to %s", mac_address)
        return True
    except Exception as e:
        logger.warning("Failed to send WoL packet to %s: %s", mac_address, e)
        return False
