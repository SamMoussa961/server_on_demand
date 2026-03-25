import ipaddress
import logging
import subprocess

logger = logging.getLogger(__name__)


def shutdown_server(ip: str, ssh_user: str = "jellyfin") -> bool:
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        logger.warning("shutdown_server called with invalid IP address: %r", ip)
        return False

    command = [
        'ssh',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'ConnectTimeout=5',
        f'{ssh_user}@{ip}',
        'sudo', 'shutdown', 'now',
    ]

    logger.info("Sending shutdown command to %s@%s", ssh_user, ip)
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        if result.returncode == 0:
            logger.info("Shutdown command accepted by %s", ip)
            return True
        else:
            logger.warning("Shutdown command failed for %s (returncode=%d)", ip, result.returncode)
            return False
    except subprocess.TimeoutExpired:
        logger.warning("SSH connection to %s timed out during shutdown", ip)
        return False
    except Exception as e:
        logger.error("Unexpected error during shutdown of %s: %s", ip, e)
        return False
