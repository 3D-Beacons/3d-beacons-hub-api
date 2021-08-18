import pytest
from click.testing import CliRunner

from app import cli


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def test_main(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
