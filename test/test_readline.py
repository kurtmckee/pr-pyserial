#! /usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2010-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Some tests for the serial module.
Part of pyserial (https://github.com/pyserial/pyserial)  (C)2010 cliechti@gmx.net

Intended to be run on different platforms, to ensure portability of
the code.

For all these tests a simple hardware is required.
Loopback HW adapter:
Shortcut these pin pairs:
 TX  <-> RX
 RTS <-> CTS
 DTR <-> DSR

On a 9 pole DSUB these are the pins (2-3) (4-6) (7-8)
"""

import unittest
import serial

#~ print serial.VERSION

# on which port should the tests be performed:
PORT = 'loop://'


class Test_Readline(unittest.TestCase):
    """Test readline function"""

    def setUp(self):
        self.s = serial.serial_for_url(PORT, timeout=1)

    def tearDown(self):
        self.s.close()

    def test_readline(self):
        """Test readline method"""
        self.s.write(b'1\n2\n3\n')
        self.assertEqual(self.s.readline(), b'1\n')
        self.assertEqual(self.s.readline(), b'2\n')
        self.assertEqual(self.s.readline(), b'3\n')
        # this time we will get a timeout
        self.assertEqual(self.s.readline(), b'')

    def test_readlines(self):
        """Test readlines method"""
        self.s.write(b'1\n2\n3\n')
        self.assertEqual(self.s.readlines(), [b'1\n', b'2\n', b'3\n'])

    def test_dunder_iter(self):
        """Test `s.__iter__()` (used in `for line in s`, for example)."""
        self.s.write(b'1\n2\n3\n')
        lines = list(self.s)
        self.assertEqual(lines, [b'1\n', b'2\n', b'3\n'])


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
