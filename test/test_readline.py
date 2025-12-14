#! /usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2010-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import typing

import pytest

import serial


@pytest.fixture
def port() -> typing.Iterable[serial.Serial]:
    port_ = serial.serial_for_url("loop://", timeout=0.0)
    yield port_
    port_.close()


def test_readline(port):
    """Test readline method"""
    port.write(b'1\n2\n3\n')
    assert port.readline() == b'1\n'
    assert port.readline() == b'2\n'
    assert port.readline() == b'3\n'
    # this time we will get a timeout
    assert port.readline() == b''


def test_readlines(port):
    """Test readlines method"""
    port.write(b'1\n2\n3\n')
    assert port.readlines() == [b'1\n', b'2\n', b'3\n']


def test_dunder_iter(port):
    """Test `s.__iter__()` (used in `for line in s`, for example)."""
    port.write(b'1\n2\n3\n')
    lines = list(port)
    assert lines == [b'1\n', b'2\n', b'3\n']
