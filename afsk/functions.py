#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bell 202 Audio Frequency Shift Keying

http://n1vg.net/packet/
"""

__author__ = 'Christopher H. Casebeer <c@chc.name>'
__copyright__ = 'Copyright (c) 2013 Christopher H. Casebeer. All rights reserved.'
__license__ = 'Simplified BSD License'


import itertools
import logging
import math
import struct
import sys

from bitarray import bitarray

import audiogen

from audiogen.util import multiply
from audiogen.util import constant

import afsk


logger = logging.getLogger(__name__)


def bit_stuff(data):
	count = 0
	for bit in data:
		if bit:
			count += 1
		else:
			count = 0
		yield bit
		# todo: do we stuff *after* fifth '1' or *before* sixth '1?'
		if count == 5:
			logger.debug("Stuffing bit")
			yield False
			count = 0


def bit_unstuff(data):
	pass


def fcs(bits):
	'''
	Append running bitwise FCS CRC checksum to end of generator
	'''
	fcs = FCS()
	for bit in bits:
		yield bit
		fcs.update_bit(bit)

#	test = bitarray()
#	for byte in (digest & 0xff, digest >> 8):
#		print byte
#		for i in range(8):
#			b = (byte >> i) & 1 == 1
#			test.append(b)
#			yield b

	# append fcs digest to bit stream

	# n.b. wire format is little-bit-endianness in addition to little-endian
	digest = bitarray(endian="little")
	digest.frombytes(fcs.digest())
	for bit in digest:
		yield bit


def fcs_validate(bits):
	buffer = bitarray()
	fcs = FCS()

	for bit in bits:
		buffer.append(bit)
		if len(buffer) > 16:
			bit = buffer.pop(0)
			fcs.update(bit)
			yield bit

	if buffer.tobytes() != fcs.digest():
		raise Exception("FCS checksum invalid.")


def encode(binary_data):
	"""
	Encode binary data using Bell-202 AFSK

	Expects a bitarray.bitarray() object of binary data as its argument.
	Returns a generator of sound samples suitable for use with the
	audiogen module.
	"""
	framed_data = frame(binary_data)

	# set volume to 1/2, preceed packet with 1/20 s silence to allow for
	# startup glitches
	for sample in itertools.chain(
		audiogen.silence(1.05),
		modulate(framed_data),
		# For some reason this results in choppy audio from the soundcard:
		#multiply(modulate(framed_data), constant(0.5)),
		audiogen.silence(1.05),
	):
		yield sample


def modulate(data):
	"""
	Generate Bell 202 AFSK samples for the given symbol generator

	Consumes raw wire symbols and produces the corresponding AFSK samples.
	"""
	seconds_per_sample = 1.0 / audiogen.sampler.FRAME_RATE
	phase, seconds, bits = 0, 0, 0

	# construct generators
	clock = (x / afsk.BAUD_RATE for x in itertools.count(1))
	tones = (afsk.MARK_HZ if bit else SPACE_HZ for bit in data)

	for boundary, frequency in itertools.izip(clock, tones):
		# frequency of current symbol is determined by how much
		# we advance the signal's phase in each audio frame
		phase_change_per_sample = afsk.TWO_PI / (
			audiogen.sampler.FRAME_RATE / frequency)

		# produce samples for the current symbol
		# until we reach the next clock boundary
		while seconds < boundary:
			yield math.sin(phase)

			seconds += seconds_per_sample
			phase += phase_change_per_sample

			if phase > afsk.TWO_PI:
				phase -= afsk.TWO_PI

		bits += 1
		logger.debug((
			"bits=%d, time=%.7f ms, expected time=%.7f ms, error=%.7f ms, "
			"baud rate=%.6f Hz",
			bits, 1000 * seconds, 1000 * bits / afsk.BAUD_RATE,
			1000 * (seconds - bits / afsk.BAUD_RATE), bits / seconds
		))


def nrzi(data):
	"""
	Packet uses NRZI (non-return to zero inverted) encoding, which means
	that a 0 is encoded as a change in tone, and a 1 is encoded as
	no change in tone.
	"""
	current = True
	for bit in data:
		if not bit:
			current = not current
		yield current


def frame(stuffed_data):
	"""
	Frame data in 01111110 flag bytes and NRZI encode.

	Data must be already checksummed and stuffed. Frame will be
	preceded by two bytes of all zeros (which NRZI will encode as
	continuously altenrating tones) to assist with decoder clock
	sync.
	"""
	return nrzi(
		itertools.chain(
			bitarray('00000000') * 20,
			bitarray('01111110') * 100,
			stuffed_data,
			bitarray('01111110')
		)
	)
