import logging


def _init_logger():
    logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
    logging.debug('Logger Initialized')

_init_logger()
log = logging.getLogger('Liquidator')