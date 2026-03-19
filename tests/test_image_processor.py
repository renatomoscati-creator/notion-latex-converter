import io
import base64
import pytest
from PIL import Image
from converter.image_processor import (
    preprocess_image,
    encode_image_to_base64,
    load_image_from_bytes,
)


def test_small_image_upscaled(small_image):
    result = preprocess_image(small_image)
    assert result.width >= 100
    assert result.height >= 100


def test_large_image_downscaled(large_image):
    result = preprocess_image(large_image)
    assert max(result.width, result.height) <= 2000


def test_normal_image_unchanged_size(sample_rgb_image):
    result = preprocess_image(sample_rgb_image)
    assert result.width == 100
    assert result.height == 100


def test_rgba_converted_to_rgb():
    rgba_image = Image.new("RGBA", (100, 100), (255, 255, 255, 128))
    result = preprocess_image(rgba_image)
    assert result.mode == "RGB"


def test_encode_returns_valid_base64(sample_rgb_image):
    b64, media_type = encode_image_to_base64(sample_rgb_image)
    assert media_type == "image/png"
    decoded = base64.b64decode(b64)
    assert len(decoded) > 0


def test_encode_jpeg_media_type(sample_rgb_image):
    _, media_type = encode_image_to_base64(sample_rgb_image, format="JPEG")
    assert media_type == "image/jpeg"


def test_load_from_bytes_valid_png(sample_rgb_image):
    buf = io.BytesIO()
    sample_rgb_image.save(buf, format="PNG")
    png_bytes = buf.getvalue()
    result = load_image_from_bytes(png_bytes)
    assert isinstance(result, Image.Image)


def test_load_from_bytes_invalid_raises():
    with pytest.raises(Exception):
        load_image_from_bytes(b"not an image")
