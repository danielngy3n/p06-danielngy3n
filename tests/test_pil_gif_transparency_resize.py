from io import BytesIO
from pathlib import Path

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine

STICKER = Path(__file__).parent.parent / "course" / "images" / "sticker.gif"


def test_resized_sticker_gif_keeps_transparency_index():
    # Issue #3: resizing sticker.gif and writing GIF with
    # PILLOW_PRESERVE_INDEXED_MODE on must keep the transparent background.
    config = Config()
    config.PILLOW_PRESERVE_INDEXED_MODE = True
    context = Context(config=config)

    engine = Engine(context)
    engine.load(STICKER.read_bytes(), ".gif")
    engine.resize(240, 160)
    out = engine.read(".gif")

    result = Image.open(BytesIO(out))
    assert "transparency" in result.info
    assert result.convert("RGBA").getpixel((0, 0))[3] == 0
