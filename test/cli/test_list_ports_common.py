import platform

import pytest

from serial.tools import list_ports_common

na_attributes = {
    "description",
    "hwid",
}

none_attributes = {
    "vid",
    "pid",
    "serial_number",
    "location",
    "manufacturer",
    "product",
    "interface",
}


@pytest.fixture
def device(fs):
    if platform.system().lower() == "windows":
        yield "COM1"
    else:
        device = "/dev/device"
        fs.create_file(device, 0)
        yield device


@pytest.fixture
def symlink(fs, device):
    if platform.system().lower() == "windows":
        yield device
    else:
        symlink = "/dev/symlink"
        fs.create_symlink(symlink, device)
        yield symlink


def test_list_port_info_basic(symlink):
    port = list_ports_common.ListPortInfo(symlink, skip_link_detection=True)
    assert port.device == symlink
    assert symlink.endswith(port.name)

    for attribute in na_attributes:
        assert getattr(port, attribute) == "n/a"
    for attribute in none_attributes:
        assert getattr(port, attribute) is None

    assert symlink.endswith(port.usb_description())
    assert port.usb_info() == "USB VID:PID=0000:0000"
    assert str(port) == f"{symlink} - n/a"
    assert hash(port) == hash(symlink)


@pytest.mark.skipif(platform.system().lower() != "windows", reason="Windows only")
def test_list_port_info_with_link_detection_windows(device, symlink):
    port = list_ports_common.ListPortInfo(symlink, skip_link_detection=False)
    assert port.device == symlink
    assert port.hwid == "n/a"

    for attribute in na_attributes - {"hwid"}:
        assert getattr(port, attribute) == "n/a"
    for attribute in none_attributes:
        assert getattr(port, attribute) is None


@pytest.mark.skipif(platform.system().lower() == "windows", reason="non-Windows only")
def test_list_port_info_with_link_detection_non_windows(device, symlink):
    port = list_ports_common.ListPortInfo(symlink, skip_link_detection=False)
    assert port.device == symlink
    assert port.hwid == f"LINK={device}"

    for attribute in na_attributes - {"hwid"}:
        assert getattr(port, attribute) == "n/a"
    for attribute in none_attributes:
        assert getattr(port, attribute) is None


@pytest.mark.parametrize(
    "vid, pid, serial_number, location, expected",
    (
        (0xA, 0xB, None, None, "USB VID:PID=000A:000B"),
        (0xA, 0xB, "SN", None, "USB VID:PID=000A:000B SER=SN"),
        (0xA, 0xB, None, "LC", "USB VID:PID=000A:000B LOCATION=LC"),
        (0xA, 0xB, "SN", "LC", "USB VID:PID=000A:000B SER=SN LOCATION=LC"),
    ),
)
def test_usb_info(symlink, vid, pid, serial_number, location, expected):
    port = list_ports_common.ListPortInfo(symlink, skip_link_detection=True)
    port.vid = vid
    port.pid = pid
    port.serial_number = serial_number
    port.location = location

    assert port.usb_info() == expected


@pytest.mark.parametrize(
    "product, interface, expected",
    (
        pytest.param(None, None, ..., id="name-fallback"),
        pytest.param("Product", None, "Product", id="product-only"),
        pytest.param(None, "Interface", "None - Interface", id="interface-only"),
        pytest.param("Product", "Interface", "Product - Interface", id="both"),
    ),
)
def test_list_port_info_usb_description(symlink, product, interface, expected):
    port = list_ports_common.ListPortInfo(symlink, skip_link_detection=True)
    port.product = product
    port.interface = interface

    if expected is ...:
        # Name fallback varies by platform and must be dynamically verified.
        assert port.usb_description() == port.name
    else:
        assert port.usb_description() == expected


def test_list_port_info_comparisons():
    port_1 = list_ports_common.ListPortInfo("a1", skip_link_detection=True)
    port_10 = list_ports_common.ListPortInfo("a010", skip_link_detection=True)

    assert port_1 != port_10
    assert port_1 < port_10
    assert port_10 > port_1


def test_list_port_info_comparisons_bad_comparisons():
    port_1 = list_ports_common.ListPortInfo("a1", skip_link_detection=True)

    assert port_1 != "a1"
    with pytest.raises(TypeError, match="unorderable types"):
        assert port_1 < "a2"


@pytest.mark.skipif(platform.system().lower() == "windows", reason="non-Windows only")
def test_list_links(symlink, device):
    devices = {device}
    links = list_ports_common.list_links(devices)
    assert links == [symlink], "The symlink was not found"
    assert devices == {device}, "The set of devices must not be mutated"
