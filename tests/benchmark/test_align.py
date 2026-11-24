"""Locating ground-truth items in OCR text by character alignment (`benchmark.align`)."""

import unicodedata

import pytest

from benchmark.align import aligned_characters, locate, spaced

NAME = "Jiří Čermák"
TRUTH = f"Kupující: {NAME}, nar. 1. 2. 1980\nTel.: +420 777 123 456"


def _span(text: str, item: str) -> tuple[int, int]:
    start = text.index(item)
    return start, start + len(item)


def _located(truth: str, item: str, ocr: str) -> str | None:
    (span,) = locate(truth, [_span(truth, item)], ocr)
    return None if span is None else ocr[span[0] : span[1]]


class TestSpaced:
    def test_whitespace_runs_become_one_space_and_edges_go(self):
        result = spaced("  Jan \n\t Novák \n")
        assert result.text == "Jan Novák"

    def test_each_character_keeps_its_original_offsets(self):
        text = "a \n b"
        result = spaced(text)
        assert result.text == "a b"
        assert result.starts == (0, 1, 4)
        assert result.ends == (1, 4, 5)

    def test_decomposed_letters_are_composed_and_point_at_their_whole_cluster(self):
        text = unicodedata.normalize("NFD", "Čáp")
        result = spaced(text)
        assert result.text == "Čáp"
        assert result.starts == (0, 2, 4)
        assert result.ends == (2, 4, 5)


class TestAlignedCharacters:
    def test_identical_texts_align_one_to_one(self):
        assert aligned_characters("abc", "abc") == [0, 1, 2]

    def test_a_substitution_is_aligned_and_a_deletion_is_not(self):
        assert aligned_characters("abcdef", "abXdf") == [0, 1, 2, 3, None, 4]

    def test_insertions_shift_what_follows(self):
        assert aligned_characters("ab", "xxabyy") == [2, 3]

    def test_an_empty_reading_aligns_nothing(self):
        assert aligned_characters("abc", "") == [None, None, None]


class TestLocate:
    def test_an_exact_reading_locates_the_item_where_it_is(self):
        assert _located(TRUTH, NAME, TRUTH) == NAME

    def test_substitutions_inside_an_item_keep_it_located_whole(self):
        ocr = TRUTH.replace(NAME, "Jiři Cerrnák")
        assert _located(TRUTH, NAME, ocr) == "Jiři Cerrnák"

    def test_lost_diacritics_still_locate_the_item(self):
        ocr = TRUTH.replace(NAME, "Jiri Cermak")
        assert _located(TRUTH, NAME, ocr) == "Jiri Cermak"

    def test_an_item_fully_deleted_is_not_read(self):
        ocr = TRUTH.replace(f"{NAME}, ", "")
        assert _located(TRUTH, NAME, ocr) is None

    def test_an_item_partly_read_is_located_on_what_was_read(self):
        ocr = TRUTH.replace(NAME, "Jiří")
        assert _located(TRUTH, NAME, ocr) == "Jiří"

    def test_junk_read_before_and_after_the_page_stays_outside_the_item(self):
        ocr = f"|||  ~~ = \n{TRUTH}\n__ |  1 ;"
        assert _located(TRUTH, NAME, ocr) == NAME

    def test_junk_between_the_lines_of_a_table_stays_outside_the_item(self):
        truth = f"Jméno\n{NAME}\nTelefon"
        ocr = f"Jméno | —\n| {NAME} |\n— Telefon"
        assert _located(truth, NAME, ocr) == NAME

    def test_junk_inside_the_item_belongs_to_it(self):
        ocr = TRUTH.replace(NAME, "Jiří | Čermák")
        assert _located(TRUTH, NAME, ocr) == "Jiří | Čermák"

    def test_an_item_split_across_a_line_break_is_located_across_it(self):
        truth = "Smlouvu podepsal Jiří\nČermák, jednatel."
        ocr = "Smlouvu podepsal Jiří\n\nČermák, jednatel."
        assert _located(truth, "Jiří\nČermák", ocr) == "Jiří\n\nČermák"

    def test_an_item_read_on_one_line_after_a_break_is_located(self):
        truth = "Smlouvu podepsal Jiří\nČermák, jednatel."
        ocr = "Smlouvu podepsal Jiří Čermák, jednatel."
        assert _located(truth, "Jiří\nČermák", ocr) == NAME

    def test_offsets_index_the_ocr_text_as_given_not_its_normalized_form(self):
        ocr = unicodedata.normalize("NFD", f"   header\n\n{TRUTH}")
        span = locate(TRUTH, [_span(TRUTH, NAME)], ocr)[0]
        assert span is not None
        assert unicodedata.normalize("NFC", ocr[span[0] : span[1]]) == NAME

    def test_several_items_are_located_in_order(self):
        phone = "+420 777 123 456"
        spans = [_span(TRUTH, NAME), _span(TRUTH, phone)]
        ocr = TRUTH.replace("777", "7?7")
        located = locate(TRUTH, spans, ocr)
        assert [ocr[span[0] : span[1]] for span in located if span] == [NAME, "+420 7?7 123 456"]

    def test_a_repeated_text_is_located_at_its_own_occurrence(self):
        truth = "Jan Novák a Jan Novák"
        second = (12, 21)
        ocr = "Jan Novák a Jan Novak"
        span = locate(truth, [second], ocr)[0]
        assert span == (12, 21)

    def test_an_item_whose_letters_became_spaces_is_not_read(self):
        truth = "ab XY cd"
        ocr = "ab    cd"
        assert locate(truth, [(3, 5)], ocr) == [None]

    def test_nothing_read_locates_nothing(self):
        assert locate(TRUTH, [_span(TRUTH, NAME)], "") == [None]

    @pytest.mark.parametrize("ocr", ["Jiří Čermák", "  Jiří   Čermák  "])
    def test_spacing_around_and_inside_does_not_move_the_item(self, ocr: str):
        assert _located(NAME, NAME, ocr) == ocr.strip()
