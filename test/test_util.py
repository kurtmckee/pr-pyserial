#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Tests for utility functions of serualutil.
"""

import pytest

import serial.serialutil


@pytest.mark.parametrize(
    "arg, expected",
    (
        ([1, 2, 3], b'\x01\x02\x03'),
        (b'\x01\x02\x03', b'\x01\x02\x03'),
        (bytearray([1, 2, 3]), b'\x01\x02\x03'),
        (memoryview(b'\x01\x02\x03'), b'\x01\x02\x03'),
    )
)
def test_to_bytes(arg, expected):
    assert serial.serialutil.to_bytes(arg) == expected


def test_to_bytes_string():
    with pytest.raises(TypeError, match='strings are not supported'):
        serial.serialutil.to_bytes('hello')


@pytest.mark.parametrize(
    "arg, expected",
    (
        (b'', []),
        (b'123', [b'1', b'2', b'3']),
        (memoryview(b''), []),
        (memoryview(b'123'), [b'1', b'2', b'3']),
    )
)
def test_iterbytes(arg, expected):
    assert list(serial.serialutil.iterbytes(arg)) == expected
