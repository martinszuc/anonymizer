"""Code-degraded photo text for training (`benchmark.photo_noisy`)."""

import dataclasses

from anonymizer.core.types import EntityType
from PIL import Image, ImageStat

from benchmark.photo_noisy import DEV_SHARE, PROFILES, degradation, degrade, page_record, split_of
from benchmark.spec import GoldItem


def test_a_tenth_to_a_fifth_of_the_documents_go_to_dev_always_the_same():
    names = [f"cs-s{index:05d}-lease" for index in range(1, 401)]
    splits = [split_of(name) for name in names]
    assert splits == [split_of(name) for name in names]
    assert set(splits) == {"train", "dev"}
    assert abs(splits.count("dev") / len(names) * 100 - DEV_SHARE) < 5


def test_a_page_degradation_is_seeded_and_within_its_profile():
    drawn = [degradation(f"sk-s{index:05d}-loan", 0) for index in range(60)]
    assert drawn[0] == degradation("sk-s00000-loan", 0)
    assert drawn[0] != degradation("sk-s00000-loan", 1)
    assert {applied.profile for applied in drawn} == set(PROFILES)
    for applied in drawn:
        profile = PROFILES[applied.profile]
        assert profile.strength[0] <= applied.strength <= profile.strength[1]
        assert profile.blur[0] <= applied.blur <= profile.blur[1]
        assert profile.jpeg_quality[0] <= applied.jpeg_quality <= profile.jpeg_quality[1]
        assert profile.brightness[0] <= applied.brightness <= profile.brightness[1]


def test_a_degraded_page_keeps_its_size_and_a_dim_one_is_darker():
    page = Image.new("L", (200, 280), 255)
    dim = next(
        applied
        for index in range(50)
        if (applied := degradation(f"cs-s{index:05d}-x", 0)).profile == "dim"
    )
    photo = degrade(page, dim)
    assert photo.size == page.size
    brighter = degrade(page, dataclasses.replace(dim, brightness=1.0))
    assert (
        ImageStat.Stat(photo.convert("L")).mean[0] < ImageStat.Stat(brighter.convert("L")).mean[0]
    )


def test_items_are_placed_in_the_ocr_text_and_unread_ones_dropped():
    truth = "Nájomca: Ľubica Hrušková, tel. 0905 123 456"
    items = [
        (GoldItem(EntityType.PERSON, "Ľubica Hrušková", "page"), (9, 24)),
        (GoldItem(EntityType.PHONE, "0905 123 456", "page"), (31, 43)),
    ]
    ocr = "Najomca: Lubica Hruskova, tel."
    record, not_read = page_record("sk-s00001-lease/1", truth, items, ocr)
    assert not_read == 1
    assert record["document"] == "sk-s00001-lease/1"
    assert record["text"] == ocr
    assert [(span["type"], ocr[span["start"] : span["end"]]) for span in record["spans"]] == [
        ("person", "Lubica Hruskova")
    ]
