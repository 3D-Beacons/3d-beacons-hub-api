from click.testing import CliRunner
import pytest

from app import cli


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def test_main(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
