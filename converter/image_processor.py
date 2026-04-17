import io
import base64
from PIL import Image, ImageEnhance

MAX_LONG_SIDE = 2000
MIN_SHORT_SIDE = 100


def load_image_from_bytes(raw_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(raw_bytes))


def preprocess_image(image: Image.Image) -> Image.Image:
    if image.mode != "RGB":
        image = image.convert("RGB")

    w, h = image.size

    if min(w, h) < MIN_SHORT_SIDE:
        scale = MIN_SHORT_SIDE / min(w, h)
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        w, h = image.size

    if max(w, h) > MAX_LONG_SIDE:
        scale = MAX_LONG_SIDE / max(w, h)
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.3)

    return image


def encode_image_to_base64(image: Image.Image, format: str = "PNG") -> tuple[str, str]:
    buf = io.BytesIO()
    image.save(buf, format=format)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    media_type = f"image/{format.lower()}"
    return b64, media_type
