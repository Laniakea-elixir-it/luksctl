#!/usr/bin/env python
''' Common logging options '''

import logging

def set_log(log_file, debug_level):

  log = logging.getLogger(__name__)

  logging.basicConfig(filename=log_file, format='%(levelname)s %(asctime)s %(message)s', level=debug_level)

  return log
