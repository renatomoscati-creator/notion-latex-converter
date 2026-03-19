import pytest
from PIL import Image


@pytest.fixture
def mock_anthropic_client(mocker):
    client = mocker.MagicMock()
    client.messages.create.return_value = mocker.MagicMock(
        content=[mocker.MagicMock(text=r"$$x^2 + y^2 = z^2$$")]
    )
    return client


@pytest.fixture
def mock_anthropic_client_low_confidence(mocker):
    client = mocker.MagicMock()
    client.messages.create.return_value = mocker.MagicMock(
        content=[mocker.MagicMock(text=r"[LOW_CONFIDENCE]\square")]
    )
    return client


@pytest.fixture
def mock_anthropic_client_api_error(mocker):
    import anthropic
    client = mocker.MagicMock()
    client.messages.create.side_effect = anthropic.APIError(
        message="API error", request=mocker.MagicMock(), body=None
    )
    return client


@pytest.fixture
def sample_rgb_image():
    return Image.new("RGB", (100, 100), color=(255, 255, 255))


@pytest.fixture
def small_image():
    return Image.new("RGB", (50, 50))


@pytest.fixture
def large_image():
    return Image.new("RGB", (3000, 3000))
