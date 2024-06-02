"""Main function example/template"""

import requests
import logging
from scripts.logger import get_logger

LOGGER = get_logger("simple-logger", level=logging.INFO, log_dir=None)


def main(url="https://www.google.com") -> int:
    """_summary_

    Args:
        name (str, optional): _description_. Defaults to "python".

    Returns:
        str: _description_
    """

    response = requests.get(url)
    response_status = response.status_code
    LOGGER.info(f" Response from {url} : {response_status}")

    return response_status


if __name__ == "__main__":
    main()
