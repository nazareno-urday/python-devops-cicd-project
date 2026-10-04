from click.testing import CliRunner
from simple_http_checker.cli import main
from pytest_mock import MockFixture

def test_no_urls():
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.exit_code == 0

def test_main_single_url(mocker: MockFixture):
    url = "https://www.example.com"

    mock_check = mocker.patch("simple_http_checker.cli.check_urls")
    mock_check.return_value = {url: "200 OK"}

    runner = CliRunner()
    result = runner.invoke(main, [url])

    assert result.exit_code == 0
    mock_check.assert_called_once_with([url], 5)
    assert url in result.output

def test_main_timeout_option(mocker: MockFixture):
    url = "https://www.timeout.com"

    mock_check = mocker.patch("simple_http_checker.cli.check_urls")
    mock_check.return_value = {url: "TIMEOUT"}

    runner = CliRunner()
    result = runner.invoke(main, [url, "--timeout", "10"])

    assert result.exit_code == 0
    mock_check.assert_called_once_with([url], 10)

    assert url in result.output
    assert "TIMEOUT" in result.output