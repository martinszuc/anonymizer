"""Simulated phone photos (`benchmark.photo_sim`)."""

import numpy as np
import pytest
from PIL import Image, ImageDraw

from benchmark.photo_sim import TABLE, photo_warp, simulate_photo

SIZE = (300, 420)


def _page_with_dot(x: int, y: int) -> Image.Image:
    page = Image.new("L", SIZE, 255)
    ImageDraw.Draw(page).rectangle((x - 4, y - 4, x + 4, y + 4), fill=0)
    return page


def _levels(picture: Image.Image) -> np.ndarray:
    return np.asarray(picture.convert("L"), dtype=np.int16)


def test_the_same_seed_gives_the_same_photo_and_another_seed_another():
    page = _page_with_dot(150, 200)
    first = _levels(simulate_photo(page, 7))
    assert np.array_equal(first, _levels(simulate_photo(page, 7)))
    assert not np.array_equal(first, _levels(simulate_photo(page, 8)))


@pytest.mark.parametrize("seed", [0, 1, 2, 3])
def test_ink_lands_where_the_warp_says(seed: int):
    page = _page_with_dot(80, 300)
    photo = _levels(simulate_photo(page, seed))
    x, y = photo_warp(SIZE, seed).forward(80, 300)
    assert photo[round(y), round(x)] < 60


def test_backward_undoes_forward():
    warp = photo_warp(SIZE, 5)
    x, y = warp.backward(*warp.forward(123.0, 45.0))
    assert (x, y) == pytest.approx((123.0, 45.0), abs=1e-6)


def test_the_page_corners_land_on_the_warp_corners():
    warp = photo_warp(SIZE, 11)
    width, height = SIZE
    page_corners = [(0, 0), (width, 0), (width, height), (0, height)]
    for corner, expected in zip(page_corners, warp.corners, strict=True):
        assert warp.forward(*corner) == pytest.approx(expected, abs=1e-6)


def test_outside_the_page_is_the_table():
    photo = simulate_photo(Image.new("L", SIZE, 255), 3, strength=0.0)
    assert photo.getpixel((1, 1)) == TABLE


def test_paper_stays_lighter_than_ink_under_light_and_shadow():
    page = Image.new("L", SIZE, 255)
    warp = photo_warp(SIZE, 4)
    photo = _levels(simulate_photo(page, 4))
    xs = [x for x, _ in warp.corners]
    ys = [y for _, y in warp.corners]
    # Well inside the page's quadrilateral, away from the table.
    inner = photo[int(max(ys[:2])) + 10 : int(min(ys[2:])) - 10, int(max(xs[0], xs[3])) + 10 :]
    inner = inner[:, : int(min(xs[1], xs[2])) - int(max(xs[0], xs[3])) - 20]
    assert inner.min() > 100
    assert inner.max() - inner.min() > 30


def test_strength_zero_lights_the_page_evenly():
    photo = _levels(simulate_photo(Image.new("L", SIZE, 255), 9, strength=0.0))
    assert photo[100:300, 50:250].min() == 255


def test_blur_and_jpeg_change_the_picture_but_not_its_size():
    page = _page_with_dot(150, 200)
    plain = simulate_photo(page, 2)
    degraded = simulate_photo(page, 2, blur=1.5, jpeg_quality=30)
    assert degraded.size == plain.size == SIZE
    assert degraded.mode == "RGB"
    assert not np.array_equal(_levels(plain), _levels(degraded))


@pytest.mark.parametrize("strength", [-0.1, 1.5])
def test_a_strength_outside_zero_to_one_is_refused(strength: float):
    with pytest.raises(ValueError, match="strength"):
        simulate_photo(Image.new("L", SIZE, 255), 0, strength=strength)
