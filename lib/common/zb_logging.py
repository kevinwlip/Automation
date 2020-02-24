#!/usr/bin/python

import logging
import traceback


def handleError(self, record):
    traceback.print_stack()
logging.Handler.handleError = handleError


# create logger
logger = logging.getLogger('zbat')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s %(process)d_%(thread)d - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)