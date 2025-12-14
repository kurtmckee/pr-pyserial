#! /usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import io

import serial


def test_hello_raw():
    s = serial.serial_for_url('loop://', timeout=0.0)
    text_wrapper = io.TextIOWrapper(io.BufferedRWPair(s, s))
    text_wrapper.write('hello\n')
    text_wrapper.flush()  # it is buffering. required to get the data out
    hello = text_wrapper.readline()
    assert hello == 'hello\n'
    s.close()
