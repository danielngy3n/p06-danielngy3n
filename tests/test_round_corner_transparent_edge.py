from thumbor.ext.filters import _round_corner


def test_transparent_round_corner_edge_is_not_opaque_and_dark():
    # Issue #2: with the transparent flag, edge pixels of a rounded corner
    # keep alpha 255 while their RGB is scaled toward black, which draws a
    # dark ring. A white fill on a white image must never leave an opaque
    # pixel that is darker than white.
    width, height = 100, 100
    data = bytes([255, 255, 255, 255]) * (width * height)

    out = _round_corner.apply(
        1, "RGBA", 20, 20, 255, 255, 255, width, height, data, 1
    )

    pixels = [tuple(out[i : i + 4]) for i in range(0, len(out), 4)]
    ring = [p for p in pixels if p[3] == 255 and p[:3] != (255, 255, 255)]
    assert ring == []
