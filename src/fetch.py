import logging
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ACTIVE_TYPES = {"SessionStarted", "VideoPlayback"}


def api_response(api, api_key, how_long):
    logger.debug("Polling activity log: %s (window: %d min)", api, how_long)
    response = requests.get(
        api,
        headers={'X-Emby-Token': api_key},
        params={
            'minDate': (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
                minutes=how_long)).isoformat()
        }
    )
    if response.status_code != 200:
        logger.warning("Activity log returned HTTP %d — treating as no activity", response.status_code)
        return response.status_code, {}, []

    data = response.json()
    if 'Items' not in data:
        logger.warning("Activity log response missing 'Items' key — treating as empty")
    items = data.get('Items', [])
    logger.debug("Activity log response: status=%d, items=%d", response.status_code, len(items))
    return response.status_code, data, items

def process_results(api, api_key, how_long):
    status_code, _, items = api_response(api, api_key, how_long)
    if status_code != 200:
        return False
    result = any(item.get('Type') in ACTIVE_TYPES for item in items)
    if result:
        logger.info("Active session detected in last %d minutes", how_long)
    else:
        logger.debug("No activity in last %d minutes", how_long)
    return result
