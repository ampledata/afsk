#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python AFSK Module.

"""
Python AFSK Module.
~~~~


:author: Christopher H. Casebeer <c@chc.name>
:copyright: Copyright 2013 Christopher H. Casebeer. All rights reserved.
:license: Simplified BSD License
:source: <https://github.com/casebeer/afsk>

"""

from .constants import (LOG_LEVEL, LOG_FORMAT, MARK_HZ, SPACE_HZ,  # NOQA
                        BAUD_RATE, TWO_PI, DEFAULT_TEXT, DEFAULT_DESTINATION)

from .functions import (bit_stuff, fcs_crc, fcs_validate, encode,  # NOQA
                        modulate, nrzi, frame)

from .classes import FCS, AX25, UI  # NOQA


__author__ = 'Christopher H. Casebeer <c@chc.name>'
__copyright__ = 'Copyright 2013 Christopher H. Casebeer. All rights reserved.'
__license__ = 'Simplified BSD License'
