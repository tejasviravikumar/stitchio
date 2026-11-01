from app.schemas.taxonomy import LABEL_INFO, LABELS, LABEL_TO_INDEX, SeamLabel


def test_every_label_has_help_text():
    assert set(LABEL_INFO) == set(LABELS)


def test_values_are_unique_and_indices_stable():
    assert len({label.value for label in LABELS}) == len(LABELS)
    assert [LABEL_TO_INDEX[label] for label in LABELS] == list(range(len(LABELS)))


def test_unknown_is_last():
    assert LABELS[-1] == SeamLabel.UNKNOWN


def test_notes_parser():
    from app.services.inference.notes_parser import parse_note

    note = parse_note("French dart, about 4 cm")
    assert note.label_hint == SeamLabel.BUST_DART and note.size_cm == 4
    assert parse_note("a dart of 1.5 in").is_dart
    assert abs(parse_note("a dart of 1.5 in").size_cm - 3.81) < 1e-6
    assert parse_note(None).label_hint is None
