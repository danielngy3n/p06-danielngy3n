from pathlib import Path

from tests.base import TestCase
from tests.fixtures.transformer_test_data import TestData
from thumbor.engines.pil import Engine
from thumbor.transformer import Transformer

SOURCE_940X2 = Path(__file__).parent.parent / "course" / "images" / "940x2.png"


class AutoCropMinimumSizeTestCase(TestCase):
    def test_auto_crop_never_produces_an_empty_crop(self):
        # Issue #4: a 1x1 source resized to 50x25 rounds the crop height
        # to 0, so the engine gets an empty crop and returns a blank image.
        data = TestData(
            source_width=1,
            source_height=1,
            target_width=50,
            target_height=25,
            halign="center",
            valign="middle",
            focal_points=[],
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
        )
        ctx = data.to_context()
        engine = ctx.modules.engine
        trans = Transformer(ctx)

        trans._calculate_target_dimensions()
        trans.adjust_focal_points()
        trans.auto_crop()

        assert engine.calls["crop"], "auto_crop should call the engine crop"
        crop = engine.calls["crop"][0]
        assert crop["right"] > crop["left"]
        assert crop["bottom"] > crop["top"]

    def test_fit_in_1x1_of_wide_source_resizes_to_1x1(self):
        # Issue #4: /unsafe/fit-in/1x1/940x2.png rounds the resized height
        # of 940x2 down to 0 and the engine rejects it.
        data = TestData(
            source_width=940,
            source_height=2,
            target_width=1,
            target_height=1,
            halign="center",
            valign="middle",
            focal_points=[],
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
            fit_in=True,
        )
        ctx = data.to_context()
        engine = ctx.modules.engine
        trans = Transformer(ctx)

        trans._calculate_target_dimensions()
        trans.adjust_focal_points()
        trans.fit_in_resize()

        assert engine.calls["resize"] == [{"width": 1, "height": 1}]

    def test_fit_in_width_only_of_wide_source_resizes_to_100x1(self):
        # Issue #4: /unsafe/fit-in/100x0/940x2.png asks for a width only.
        # The real engine rounds the proportional height 0.21 down to 0,
        # and fit_in_resize then divides by it.
        data = TestData(
            source_width=940,
            source_height=2,
            target_width=100,
            target_height=0,
            halign="center",
            valign="middle",
            focal_points=[],
            crop_left=None,
            crop_top=None,
            crop_right=None,
            crop_bottom=None,
            fit_in=True,
        )
        ctx = data.to_context()
        engine = Engine(ctx)
        engine.load(SOURCE_940X2.read_bytes(), ".png")
        ctx.modules.engine = engine
        ctx.request.engine = engine
        trans = Transformer(ctx)

        trans._calculate_target_dimensions()
        trans.adjust_focal_points()
        trans.fit_in_resize()

        assert engine.size == (100, 1)
