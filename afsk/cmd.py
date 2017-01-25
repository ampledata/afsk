#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python Command Line Methods."""

import logging
import logging.handlers
import sys
import argparse

import aprs
import audiogen

import afsk

__author__ = 'Christopher H. Casebeer <c@chc.name>'
__copyright__ = 'Copyright 2013 Christopher H. Casebeer. All rights reserved.'
__license__ = 'Simplified BSD License'


def cli(arguments=None):
    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(afsk.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(afsk.LOG_LEVEL)
        _console_handler.setFormatter(afsk.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-c',
        '--callsign',
        required=True,
        help='Callsign.'
    )

    parser.add_argument(
        '-d', '--destination',
        default='APRS',
        help=(
            'AX.25 destination address. '
            'See http://www.aprs.org/aprs11/tocalls.txt'
        )
    )
    parser.add_argument(
        '-p', '--path',
        default='WIDE1-1,WIDE2-1',
        help='Comma separated list of digipeaters to address.'
    )
    parser.add_argument(
        '-o',
        '--output',
        default=None,
        help='Write audio to wav file. Use \'-\' for stdout.'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        help='Print more debugging output.'
    )
    parser.add_argument(
        'text',
        metavar='TEXT',
        help='APRS message text'
    )

    args = parser.parse_args(args=arguments)

    if args.verbose == 0:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose >= 1:
        logging.basicConfig(level=logging.DEBUG)

    packet = afsk.UI(
        source=args.callsign,
        text=args.text,
        destination=args.destination,
        path=args.path.split(b','),
    )
    packet_unparsed = packet.unparse()

    _logger.info("Sending Packet: '%s'", packet)
    _logger.debug("Unparsed Packet: '%s'", packet_unparsed)
    _logger.debug("Unparsed Packet: '%s'", packet_unparsed.tobytes().encode('hex'))

    audio = afsk.encode(packet_unparsed)

    if args.output == '-':
        audiogen.sampler.write_wav(sys.stdout, audio)
    elif args.output is not None:
        with open(args.output, 'wb') as out_fd:
            audiogen.sampler.write_wav(out_fd, audio)
    else:
        audiogen.sampler.play(audio, blocking=True)
