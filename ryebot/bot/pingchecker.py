import logging


def check_ping(wikiname: str, logger: logging.Logger):
    logger.info(f'Started pingchecker on the "{wikiname}" wiki.')