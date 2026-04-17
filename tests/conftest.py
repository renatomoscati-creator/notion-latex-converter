import pytest
from PIL import Image


@pytest.fixture
def mock_gemini_client(mocker):
    """Mock google.genai.Client so no real API calls are made."""
    mock_client = mocker.MagicMock()
    mock_client.models.generate_content.return_value = mocker.MagicMock(
        text=r"$$x^2 + y^2 = z^2$$"
    )
    return mock_client


@pytest.fixture
def mock_gemini_client_low_confidence(mocker):
    mock_client = mocker.MagicMock()
    mock_client.models.generate_content.return_value = mocker.MagicMock(
        text=r"[LOW_CONFIDENCE]\square"
    )
    return mock_client


@pytest.fixture
def mock_gemini_client_api_error(mocker):
    mock_client = mocker.MagicMock()
    mock_client.models.generate_content.side_effect = Exception("API error")
    return mock_client


@pytest.fixture
def sample_rgb_image():
    return Image.new("RGB", (100, 100), color=(255, 255, 255))


@pytest.fixture
def small_image():
    return Image.new("RGB", (50, 50))


@pytest.fixture
def large_image():
    return Image.new("RGB", (3000, 3000))
