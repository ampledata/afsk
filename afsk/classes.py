#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python AFSK Module Class Definitions."""

import logging
import logging.handlers
import struct

from bitarray import bitarray

import afsk

__author__ = 'Christopher H. Casebeer <c@chc.name>'
__copyright__ = 'Copyright 2013 Christopher H. Casebeer. All rights reserved.'
__license__ = 'Simplified BSD License'


class AX25(object):

    """AX25 Class Object."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(afsk.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(afsk.LOG_LEVEL)
        _console_handler.setFormatter(afsk.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, source, info, destination=None, digipeaters=None):
        self.source = source
        self.info = info or afsk.DEFAULT_INFO
        self.destination = destination or afsk.DEFAULT_DESTINATION
        self.digipeaters = digipeaters or afsk.DEFAULT_DIGIPEATERS

        self.flag = b"\x7e"
        self._logger.info(locals())

    def __str__(self):
        return b"{source}>{destination},{digis}:{info}".format(
            destination=self.destination,
            source=self.source,
            digis=b",".join(self.digipeaters),
            info=self.info
        )

    @classmethod
    def callsign_encode(cls, callsign):
        callsign = callsign.upper()
        if callsign.find(b"-") > 0:
            callsign, ssid = callsign.split(b"-")
        else:
            ssid = b"0"

        assert len(ssid) == 1
        assert len(callsign) <= 6

        callsign = b"{callsign:6s}{ssid}".format(callsign=callsign, ssid=ssid)

        # now shift left one bit, argh
        return b"".join([chr(ord(char) << 1) for char in callsign])

    def encoded_addresses(self):
        address_bytes = bytearray(b"{destination}{source}{digis}".format(
            destination=AX25.callsign_encode(self.destination),
            source=AX25.callsign_encode(self.source),
            digis=b"".join(
                [AX25.callsign_encode(digi) for digi in self.digipeaters])
        ))

        # set the low order (first, with eventual little bit endian encoding)
        # bit in order to flag the end of the address string
        address_bytes[-1] |= 0x01

        return address_bytes

    def header(self):
        return b"{addresses}{control}{protocol}".format(
            addresses=self.encoded_addresses(),
            control=self.control_field,  # * 8,
            protocol=self.protocol_id,
        )

    def packet(self):
        return b"{header}{info}{fcs}".format(
            flag=self.flag,
            header=self.header(),
            info=self.info,
            fcs=self.fcs()
        )

    def unparse(self):
        flag = bitarray(endian="little")
        flag.frombytes(self.flag)

        bits = bitarray(endian="little")
        bits.frombytes("".join([self.header(), self.info, self.fcs()]))

        return flag + afsk.bit_stuff(bits) + flag

    def fcs(self):
        content = bitarray(endian="little")
        content.frombytes("".join([self.header(), self.info]))

        fcs = FCS()
        for bit in content:
            fcs.update_bit(bit)
#        fcs.update(self.header())
#        fcs.update(self.info)
        return fcs.digest()


class UI(AX25):

    def __init__(self, source, info, destination=None, digipeaters=None):
        super(UI, self).__init__(source, info, destination, digipeaters)
        self.control_field = b"\x03"
        self.protocol_id = b"\xf0"


class FCS(object):

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(afsk.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(afsk.LOG_LEVEL)
        _console_handler.setFormatter(afsk.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self):
        self.fcs = 0xffff

    def update_bit(self, bit):
        check = (self.fcs & 0x1 == 1)
        self.fcs >>= 1
        if check != bit:
            self.fcs ^= 0x8408

    def update(self, ubytes):
        for byte in (ord(b) for b in ubytes):
            for i in range(7, -1, -1):
                self.update_bit((byte >> i) & 0x01 == 1)

    def digest(self):
        # digest is two bytes, little endian
        return struct.pack("<H", ~self.fcs % 2**16)
