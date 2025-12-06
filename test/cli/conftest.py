import json
import pathlib
import typing

import pytest


required_test_assets: set[str] = set()


def require_test_asset(relative_path: str):
    """A decorator, used to register that a test asset is used by a test.

    Parameterizes the test with a single parameter: `test_asset`.

    This allows tests that are skipped due to platform differences
    to still register that they *would* require a given test asset.
    At test suite teardown, the set of required test assets is compared
    to the set of all test assets (found simply by globbing the `assets/` directory).
    """

    required_test_assets.add(relative_path)

    def decorator(fn: typing.Callable) -> typing.Callable:
        return pytest.mark.parametrize("test_asset", [relative_path])(fn)

    return decorator


@pytest.fixture(scope="session", autouse=True)
def require_all_assets_to_be_tested():
    """At test suite teardown, confirm that all test assets were required by tests."""

    yield

    # At teardown, confirm that all test assets were used.
    #
    # The registered test asset paths may have been created while pyfakefs was enabled,
    # and their "Path" classes will not be the same as Python's "Path" classes
    # and cannot be used for direct comparisons.
    # Only string comparisons can be used between the instances.
    all_assets = (pathlib.Path(__file__).parent.parent / "assets").rglob("*.json")
    all_relative_assets = {
        str(path.relative_to(pathlib.Path(__file__).parent.parent))
        for path in all_assets
    }
    untested_assets = all_relative_assets - required_test_assets
    assert not untested_assets, "Some assets were untested"


@pytest.fixture
def prepare_filesystem(fs):
    """Provide a helper function that creates a fake filesystem given a test asset."""

    def _prepare_filesystem(asset_path: str) -> dict[str, typing.Any]:
        path = pathlib.Path(__file__).parent.parent / asset_path
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
