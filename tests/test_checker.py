import pytest
import requests
from pytest_mock import MockerFixture

from simple_http_checker.checker import check_urls


def test_check_urls_success(mocker):
    mock_requests_get = mocker.patch(
        "simple_http_checker.checker.requests.get"
    )

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_response.ok = True
    mock_requests_get.return_value = mock_response

    urls = ["https://www.example.com"]
    results = check_urls(urls)

    mock_requests_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == "200 OK"


def test_check_urls_client_error(mocker: MockerFixture):
    mock_requests_get = mocker.patch(
        "simple_http_checker.checker.requests.get"
    )

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mock_response.ok = False
    mock_requests_get.return_value = mock_response

    urls = ["https://www.example.com/nonexistent"]
    results = check_urls(urls)

    mock_requests_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == "404, [Not Found]"


@pytest.mark.parametrize(
    "error_exception,expected_status",
    [
        (requests.exceptions.Timeout, "TIMEOUT"),
        (
            requests.exceptions.ConnectionError,
            "CONNECTION ERROR",
        ),
        (
            requests.exceptions.RequestException,
            "ERROR: Simulated error",
        ),
    ],
)
def test_check_urls_requests_exceptions(
    mocker: MockerFixture,
    error_exception: type[requests.exceptions.RequestException],
    expected_status: str,
):

    mock_requests_get = mocker.patch(
        "simple_http_checker.checker.requests.get"
    )

    mock_requests_get.side_effect = error_exception(
        "Simulated error"
    )

    urls = ["https://www.problem.com"]
    results = check_urls(urls)

    mock_requests_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == expected_status


def test_check_urls_with_multiple_urls(mocker: MockerFixture):
    mock_requests_get = mocker.patch(
        "simple_http_checker.checker.requests.get"
    )

    # First call: OK
    mock_response_ok = mocker.MagicMock(spec=requests.Response)
    mock_response_ok.status_code = 200
    mock_response_ok.reason = "OK"
    mock_response_ok.ok = True

    # Second call: Timeout
    timeout_exception = requests.exceptions.Timeout(
        "Simulated timeout"
    )

    # Third call: 500 Server Error
    mock_response_fail = mocker.MagicMock(spec=requests.Response)
    mock_response_fail.status_code = 500
    mock_response_fail.reason = "Server Error"
    mock_response_fail.ok = False

    mock_requests_get.side_effect = [
        mock_response_ok,
        timeout_exception,
        mock_response_fail,
    ]

    urls = [
        "https://success.com",
        "https://timeout.com",
        "https://servererror.com",
    ]
    results = check_urls(urls)

    assert len(results) == 3
    assert mock_requests_get.call_count == 3
    assert results[urls[0]] == "200 OK"
    assert results[urls[1]] == "TIMEOUT"
    assert results[urls[2]] == "500, [Server Error]"


def test_check_urls_empty_list():
    urls = []
    results = check_urls(urls)
    assert len(results) == 0
    assert results == {}


def test_check_urls_custom_timeout(mocker):
    mock_requests_get = mocker.patch(
        "simple_http_checker.checker.requests.get"
    )

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_response.ok = True
    mock_requests_get.return_value = mock_response

    urls = ["https://www.example.com"]
    custom_timeout = 10
    results = check_urls(urls, timeout=custom_timeout)

    mock_requests_get.assert_called_once_with(
        urls[0], timeout=custom_timeout
    )
    assert results[urls[0]] == "200 OK"
