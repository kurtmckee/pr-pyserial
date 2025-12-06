import json
import pathlib
import typing

import pytest

import serial.tools.list_ports_linux


@pytest.fixture
def prepare_filesystem(fs):
    """Provide a helper function that creates a fake filesystem given a test asset."""

    def _prepare_filesystem(asset_path: str) -> dict[str, typing.Any]:
        path = pathlib.Path(__file__).parent / asset_path
        fs.add_real_file(path)
        data = json.loads(path.read_text())

        for info in data["filesystem"]:
            if info["type"] == "char_device":
                fs.create_file(info["path"])
            if info["type"] == "file" and info["os_error"] is None:
                contents = info["contents"].encode(info["encoding"])
                fs.create_file(info["path"], contents=contents)
            if info["type"] == "symlink":
                fs.create_symlink(info["path"], info["realpath"])

        return data

    return _prepare_filesystem


def test_aten_uc_232a_pl2303(prepare_filesystem):
    """Test sysfs loading for the ATEN UC-232A USB-to-serial port adapter."""

    data = prepare_filesystem("assets/sysfs/ATEN--UC-232A.json")

    info = serial.tools.list_ports_linux.SysFS(data["filesystem"][0]["path"])

    assert info.device == '/dev/ttyUSB0'
    assert info.name == 'ttyUSB0'
    assert info.description == 'USB-Serial Controller D'
    assert info.hwid == 'USB VID:PID=0557:2008 LOCATION=3-4.2.7.3'
    assert info.vid == 0x0557
    assert info.pid == 0x2008
    assert info.serial_number is None
    assert info.location == '3-4.2.7.3'
    assert info.manufacturer == 'Prolific Technology Inc.'
    assert info.product == 'USB-Serial Controller D'
    assert info.interface is None
    assert info.usb_device_path == '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-4/3-4.2/3-4.2.7/3-4.2.7.3'
    assert info.device_path == '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-4/3-4.2/3-4.2.7/3-4.2.7.3/3-4.2.7.3:1.0/ttyUSB0'
    assert info.subsystem == 'usb-serial'
    assert info.usb_interface_path == '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-4/3-4.2/3-4.2.7/3-4.2.7.3/3-4.2.7.3:1.0'

    ports = serial.tools.list_ports_linux.comports()
    assert len(ports) == 1
    assert ports[0].device == '/dev/ttyUSB0'


def test_sparkfun_iot_redboard_rp2350(prepare_filesystem):
    """Test sysfs loading for the SparkFun IoT RedBoard RP2350."""

    data = prepare_filesystem("assets/sysfs/SparkFun--IoT-RedBoard-RP2350.json")

    info = serial.tools.list_ports_linux.SysFS(data["filesystem"][0]["path"])

    assert info.device == '/dev/ttyACM0'
    assert info.name == 'ttyACM0'
    assert info.description == 'Board in FS mode - Board CDC'
    assert info.hwid == 'USB VID:PID=1B4F:0047 SER=ffaae61c8e6fdd10 LOCATION=3-5:1.0'
    assert info.vid == 0x1B4F
    assert info.pid == 0x0047
    assert info.serial_number == 'ffaae61c8e6fdd10'
    assert info.location == '3-5:1.0'
    assert info.manufacturer == 'MicroPython'
    assert info.product == 'Board in FS mode'
    assert info.interface == 'Board CDC'
    assert info.usb_device_path == '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-5'
    assert info.device_path == '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-5/3-5:1.0'
    assert info.subsystem == 'usb'
    assert info.usb_interface_path == '/sys/devices/pci0000:00/0000:00:14.0/usb3/3-5/3-5:1.0'

    ports = serial.tools.list_ports_linux.comports()
    assert len(ports) == 1
    assert ports[0].device == '/dev/ttyACM0'
