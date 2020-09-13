import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(threadName)s][%(levelname)s][%(name)s][%(funcName)s()] - '
           '%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_logger(name):
    logger = logging.getLogger(name)
    return logger
