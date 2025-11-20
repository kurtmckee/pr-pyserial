#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""
Test PTY related functionality.
"""

import os
import queue
import sys
import threading
import unittest

import serial

try:
    import pty
except ImportError:
    pty = None

DATA = b'Hello\n'


class Reader(threading.Thread):
    def __init__(self, open_fd, result_queue):
        super().__init__()
        self.open_fd = open_fd
        self.result_queue = result_queue

    def run(self):
        self.result_queue.put(self.open_fd.read(len(DATA)))

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.join()


@unittest.skipIf(pty is None, "pty module not supported on platform")
class Test_Pty_Serial_Open(unittest.TestCase):
    """Test PTY serial open"""

    def setUp(self):
        # Open PTY
        self.master, self.slave = pty.openpty()

    def test_pty_serial_open_slave(self):
        with serial.Serial(os.ttyname(self.slave), timeout=1) as slave:
            pass  # OK

    def test_pty_serial_write(self):
        with serial.Serial(os.ttyname(self.slave), timeout=1) as slave:
            with os.fdopen(self.master, "wb") as fd:
                fd.write(DATA)
                fd.flush()
                out = slave.read(len(DATA))
                self.assertEqual(DATA, out)

    def test_pty_serial_read(self):
        result_queue = queue.Queue()
        with (
            serial.Serial(os.ttyname(self.slave), timeout=1) as slave,
            os.fdopen(self.master, "rb") as open_fd,
            Reader(open_fd, result_queue),
        ):
            slave.write(DATA)
            slave.flush()
        out = result_queue.get()
        result_queue.task_done()
        self.assertEqual(DATA, out)

if __name__ == '__main__':
    sys.stdout.write(__doc__)
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
