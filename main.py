import logging
import os
import sys
import time

from dotenv import load_dotenv

from src.controller import controller

load_dotenv()

REQUIRED_VARS = [
    "CLIENT_IP_ADDRESS",
    "STORAGE_SERVER_MAC",
    "BROADCAST_ADDRESS",
    "JELLYFIN_API_URL",
    "JELLYFIN_API_KEY",
]


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

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    last_wol_sent = None
    last_activity_time = None

    try:
        while True:
            now = time.time()
            skip_wol = last_wol_sent is not None and (now - last_wol_sent) < packet_cooldown
            # how_long: minutes to look back for Jellyfin activity
            how_long = cooldown_time // 60

            result = controller(ip, mac, broadcast, api_url, api_key, how_long, skip_wol=skip_wol)

            if result == "wol_sent":
                logging.info("No active sessions, server offline — WoL packet sent to %s", mac)
                last_wol_sent = time.time()
            elif result == "already_on":
                logging.debug("Active sessions detected, server already online")
                last_activity_time = time.time()
            elif result == "no_activity":
                logging.debug("No active sessions")
                if last_activity_time is not None and (time.time() - last_activity_time) > cooldown_time:
                    logging.warning("Server idle for %ds — shutdown threshold reached", cooldown_time)
            elif result == "wol_failed":
                logging.warning("WoL packet failed for %s — will retry next cycle", mac)
            elif result == "wol_skipped":
                logging.debug("Active sessions detected, WoL skipped — cooldown active (%ds remaining)",
                              int(packet_cooldown - (time.time() - last_wol_sent)))

            time.sleep(check_interval)
    except KeyboardInterrupt:
        logging.info("Shutting down")
        sys.exit(0)


if __name__ == "__main__":
    main()
