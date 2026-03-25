import ipaddress
import subprocess


def shutdown_server(ip: str, ssh_user: str = "jellyfin") -> bool:
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        return False

    command = [
        'ssh',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'ConnectTimeout=5',
        f'{ssh_user}@{ip}',
        'sudo', 'shutdown', 'now',
    ]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        return result.returncode == 0
    except Exception:
        return False
