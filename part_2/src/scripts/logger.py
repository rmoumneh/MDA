import logging
from typing import Union
from pathlib import Path
from datetime import datetime
import os


def get_logger(
    logger_name: str,
    level=logging.DEBUG,
    log_dir: Union[str, Path, None] = None,
) -> logging.Logger:
    """_summary_

    Args:
        logger_name (str): _description_
        level (_type_, optional): _description_. Defaults to logging.DEBUG.
        log_dir (str, optional): _description_. Defaults to None.

    Returns:
        logging.Logger: _description_
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_dir:
        log_dir = Path(log_dir)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = log_dir.joinpath(datetime.now().strftime(("%d%m%Y_%H%M")))

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
