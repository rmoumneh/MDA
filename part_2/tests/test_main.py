import pytest
from scripts.main import main


@pytest.fixture
def mock_requests(mocker):
    return mocker.patch("scripts.main.requests")


def test_main_success(mock_requests):
    mock_response = mock_requests.Response()
    mock_response.status_code = 200

    mock_requests.get.return_value = mock_response

    result = main()

    assert result == 200
    mock_requests.get.assert_called_once_with("https://www.google.com")


def test_main_fail(mock_requests):
    mock_response = mock_requests.Response()
    mock_response.status_code = 404

    mock_requests.get.return_value = mock_response

    result = main()

    assert result != 200
    mock_requests.get.assert_called_once_with("https://www.google.com")
