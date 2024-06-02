import logging

from scripts.logger import get_logger


def test_get_logger_console_only():
    logger_name = "test_logger_console_only"
    logger = get_logger(logger_name, level=logging.DEBUG)

    assert isinstance(logger, logging.Logger)


def test_get_logger_with_file_handler(tmp_path):
    logger_name = "test_logger_with_file_handler"
    log_dir = tmp_path / "logs"
    logger = get_logger(logger_name, level=logging.DEBUG, log_dir=log_dir)

    assert isinstance(logger, logging.Logger)

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    log_files = list(log_dir.glob("*"))
    assert len(log_files) == 1

    with open(log_files[0], "r") as log_file:
        log_content = log_file.read()

        assert "Debug message" in log_content
        assert "Info message" in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content
