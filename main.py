import logging
import os
import sys
import time

from dotenv import load_dotenv

from src.controller import controller
from src.shutdown_server import shutdown_server
from src.wake_server import ping_host

load_dotenv()

logger = logging.getLogger(__name__)

REQUIRED_VARS = [
    "CLIENT_IP_ADDRESS",
    "STORAGE_SERVER_MAC",
    "BROADCAST_ADDRESS",
    "JELLYFIN_API_URL",
    "JELLYFIN_API_KEY",
    "SHUTDOWN_SSH_USER"
]


def configure_logging(level_name: str = "INFO") -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logging.root.setLevel(level)
    logging.root.addHandler(handler)


def main():
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    ip = os.getenv("CLIENT_IP_ADDRESS")
    mac = os.getenv("STORAGE_SERVER_MAC")
    broadcast = os.getenv("BROADCAST_ADDRESS")
    api_url = os.getenv("JELLYFIN_API_URL")
    api_key = os.getenv("JELLYFIN_API_KEY")
    check_interval = int(os.getenv("CHECK_INTERVAL"))
    packet_cooldown = int(os.getenv("PACKET_COOLDOWN_TIME"))
    cooldown_time = int(os.getenv("COOLDOWN_TIME"))
    ssh_user = os.getenv("SHUTDOWN_SSH_USER")
    log_level = os.getenv("LOG_LEVEL", "INFO")

    configure_logging(log_level)

    logger.info("server_on_demand starting up")
    logger.info("Polling every %ds | WoL cooldown: %ds | Shutdown after: %ds idle",
                check_interval, packet_cooldown, cooldown_time)
    logger.info("Target: %s (%s) | Broadcast: %s", ip, mac, broadcast)
    logger.info("Jellyfin: %s", api_url)

    last_wol_sent = None
    last_activity_time = time.time()
    last_result = None

    try:
        while True:
            now = time.time()
            logger.debug("--- cycle start | idle: %.0fs | last_wol: %.0fs ago ---",
                         now - last_activity_time,
                         (now - last_wol_sent) if last_wol_sent is not None else float('inf'))
            skip_wol = last_wol_sent is not None and (now - last_wol_sent) < packet_cooldown
            # how_long: minutes to look back for Jellyfin activity
            how_long = cooldown_time // 60

            result = controller(ip, mac, broadcast, api_url, api_key, how_long, skip_wol=skip_wol)

            if result == "wol_sent":
                logger.info("WoL sent to %s — waiting for server to boot", mac)
                last_wol_sent = time.time()
                last_activity_time = time.time()
            elif result == "already_on":
                logger.debug("Active sessions detected, server already online")
                last_activity_time = time.time()
            elif result == "no_activity":
                idle_seconds = time.time() - last_activity_time
                if last_result != "no_activity":
                    logger.info("No active sessions — server will shut down in %.0fs if idle continues",
                                max(0.0, cooldown_time - idle_seconds))
                else:
                    logger.debug("No active sessions (idle: %.0fs)", idle_seconds)
                if idle_seconds >= cooldown_time:
                    if ping_host(ip):
                        logger.info("Server idle for %.0fs — sending shutdown to %s", idle_seconds, ip)
                        if shutdown_server(ip, ssh_user):
                            logger.info("Shutdown command sent successfully")
                            last_activity_time = time.time()
                        else:
                            logger.warning("Shutdown command failed — will retry next cycle")
            elif result == "wol_failed":
                logger.warning("WoL packet failed for %s — will retry next cycle", mac)
            elif result == "wol_skipped":
                logger.debug("Active sessions detected, WoL skipped — cooldown active (%ds remaining)",
                              int(packet_cooldown - (time.time() - last_wol_sent)))

            last_result = result
            time.sleep(check_interval)
    except KeyboardInterrupt:
        logger.info("Received interrupt — shutting down cleanly")
        sys.exit(0)


if __name__ == "__main__":
    main()
