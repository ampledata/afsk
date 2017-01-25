#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python Command Line Methods."""

import logging
import logging.handlers
import struct
import sys
import argparse

from bitarray import bitarray
import audiogen

import afsk

import aprs

__author__ = 'Christopher H. Casebeer <c@chc.name>'
__copyright__ = 'Copyright (c) 2013 Christopher H. Casebeer. All rights reserved.'
__license__ = 'Simplified BSD License'



def cli(arguments=None):
	parser = argparse.ArgumentParser(description='')
	parser.add_argument(
		'-c',
		'--callsign',
		required=True,
		help='Callsign.'
	)
	parser.add_argument(
		'info',
		metavar='INFO',
		help='APRS message body'
	)
	parser.add_argument(
		'--destination',
		default=b'APRS',
		help='AX.25 destination address. See http://www.aprs.org/aprs11/tocalls.txt'
	)
	parser.add_argument(
		'-d',
		'--digipeaters',
		default=b'WIDE1-1,WIDE2-1',
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

	args = parser.parse_args(args=arguments)

	if args.verbose == 0:
		logging.basicConfig(level=logging.INFO)

	elif args.verbose >=1:
		logging.basicConfig(level=logging.DEBUG)

	packet = afsk.UI(
		destination=args.destination,
		source=args.callsign,
		info=args.info,
		digipeaters=args.digipeaters.split(b','),
	)
	frame = aprs.Frame()
	frame.destination = aprs.Callsign(args.destination),
	frame.source = aprs.Callsign(args.callsign)
	frame.text = args.info
	frame.path = args.digipeaters.split(b',')

	logger.info(r"Sending packet: '{0}'".format(packet))
	logger.debug(r"Packet bits:\n{0!r}".format(packet.unparse()))

	audio = afsk.encode(packet.unparse())
	#audio = afsk.encode(frame)

	if args.output == '-':
		audiogen.sampler.write_wav(sys.stdout, audio)
	elif args.output is not None:
		with open(args.output, 'wb') as f:
			audiogen.sampler.write_wav(f, audio)
	else:
		audiogen.sampler.play(audio, blocking=True)
