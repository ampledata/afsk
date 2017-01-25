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

    __slots__ = ['frame', 'source', 'destination', 'path', 'text']

    def __init__(self, source, text, destination=None, path=[]):
        self.source = source
        self.text = text or afsk.DEFAULT_INFO
        self.destination = destination or afsk.DEFAULT_DESTINATION
        self.path = path

        self.flag = chr(0x7E)
        self.control_field = chr(0x03)
        self.protocol_id = chr(0xF0)

        self._logger.info(locals())

    def __repr__(self):
        full_path = [str(self.destination)]
        full_path.extend([str(p) for p in self.path])
        frame = b"{source}>{path}:{text}".format(
            self.source,
            ','.join(full_path),
            self.text
        )
        return frame.encode('UTF-8')

    @classmethod
    def callsign_encode(cls, callsign):
        callsign = callsign.upper()
        if callsign.find(b'-') > 0:
            callsign, ssid = callsign.split(b'-')
        else:
            ssid = b'0'

        assert len(ssid) == 1
        assert len(callsign) <= 6

        callsign = b"{callsign:6s}{ssid}".format(callsign=callsign, ssid=ssid)

        # now shift left one bit, argh
        return b''.join([chr(ord(char) << 1) for char in callsign])

    def encoded_addresses(self):
        address_bytes = bytearray(
            b"{destination}{source}{digis}".format(
                destination=AX25.callsign_encode(self.destination),
                source=AX25.callsign_encode(self.source),
                digis=b''.join(
                    [AX25.callsign_encode(digi) for digi in self.path])
            )
        )

        # set the low order (first, with eventual little bit endian encoding)
        # bit in order to flag the end of the address string
        address_bytes[-1] |= 0x01

        return address_bytes

    def header(self):
        header = b"{addresses}{control}{protocol}".format(
            addresses=self.encoded_addresses(),
            control=self.control_field,  # * 8,
            protocol=self.protocol_id,
        )

        self._logger.debug("header='%s'", header.encode('hex'))
        return header

    def packet(self):
        packet = b"{header}{info}{fcs}".format(
            flag=self.flag,
            header=self.header(),
            info=self.text,
            fcs=self.fcs()
        )

        self._logger.debug("packet='%s'", packet)
        return packet

    def unparse(self):
        flag = bitarray(endian='little')
        flag.frombytes(self.flag)
        self._logger.debug("flag='%s'", flag)

        bits = bitarray(endian='little')
        bits.frombytes(''.join([self.header(), self.text, self.fcs()]))
        self._logger.debug("bits='%s'", bits)

        return flag + afsk.bit_stuff(bits) + flag

    def fcs(self):
        content = bitarray(endian='little')
        content.frombytes(''.join([self.header(), self.text]))

        fcs = FCS()
        for bit in content:
            fcs.update_bit(bit)

        self._logger.debug("fcs.digest()='%s'", fcs.digest().encode('hex'))
        return fcs.digest()

class UI(AX25):

    def __init__(self, source, text, destination=None, path=[]):
        super(UI, self).__init__(source, text, destination, path)
        self.control_field = chr(0x03)
        self.protocol_id = chr(0xF0)


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
