import logging
import requests
from typing import Collection

logger = logging.getLogger(__name__)


def check_urls(
    urls: Collection[str], timeout: int = 5
) -> dict[str, str]:
    logger.info(
        f"Starting check for {len(urls)} URLs with a timeout of {timeout} seconds"
    )
    results: dict[str, str] = {}

    for url in urls:
        status = "UNKNOWN"

        try:
            logger.debug(f"Checking URL: {url}")
            response = requests.get(url, timeout=timeout)

            if response.ok:
                status = f"{response.status_code} OK"
            else:
                status = f"{response.status_code}, [{response.reason}]"

        except requests.exceptions.Timeout:
            status = "TIMEOUT"
            logger.warning(f"Request to {url} timed out")

        except requests.exceptions.ConnectionError:
            status = "CONNECTION ERROR"
            logger.warning(f"Connection error for {url}")

        except requests.exceptions.RequestException as error:
            status = f"ERROR: {error}"
            logger.error(
                f"An unexpected error occurred while checking {url}"
            )

        results[url] = status
        logger.debug(f"Checked URL: {url:<40} -> {status}")

    logger.info("URL check finished")
    return results
