"""Extract a seam-label hint and an optional size from a user's note."""
from dataclasses import dataclass
import re

from app.schemas.taxonomy import SeamLabel


@dataclass(frozen=True)
class ParsedNote:
    label_hint: SeamLabel | None = None
    size_cm: float | None = None

    @property
    def is_dart(self) -> bool:
        return self.label_hint in {SeamLabel.BUST_DART, SeamLabel.WAIST_DART, SeamLabel.SHOULDER_DART}


_HINTS: tuple[tuple[tuple[str, ...], SeamLabel], ...] = (
    (("armhole", "armscye"), SeamLabel.ARMHOLE),
    (("side seam", "side-seam"), SeamLabel.SIDE_SEAM),
    (("shoulder seam",), SeamLabel.SHOULDER_SEAM),
    (("neckline",), SeamLabel.NECKLINE),
    (("center front", "centre front", "cf"), SeamLabel.CENTER_FRONT),
    (("center back", "centre back", "cb"), SeamLabel.CENTER_BACK),
    (("waist seam",), SeamLabel.WAIST_SEAM),
    (("hem",), SeamLabel.HEM),
    (("sleeve cap",), SeamLabel.SLEEVE_CAP),
    (("underarm",), SeamLabel.SLEEVE_UNDERARM),
    (("french dart", "bust dart", "bust-dart"), SeamLabel.BUST_DART),
    (("waist dart",), SeamLabel.WAIST_DART),
    (("shoulder dart",), SeamLabel.SHOULDER_DART),
    (("princess seam",), SeamLabel.PRINCESS_SEAM),
    (("yoke",), SeamLabel.YOKE),
    (("pocket",), SeamLabel.POCKET_EDGE),
    (("placket",), SeamLabel.PLACKET),
    (("dart",), SeamLabel.BUST_DART),
)


def parse_note(note: str | None) -> ParsedNote:
    if not note:
        return ParsedNote()
    text = note.casefold()
    label = next((candidate for terms, candidate in _HINTS if any(term in text for term in terms)), None)
    match = re.search(r"(\d+(?:\.\d+)?)\s*(cm|centimeters?|inches|inch|in\b|\")", text)
    size_cm = None
    if match:
        size_cm = float(match.group(1))
        if match.group(2).startswith("in") or match.group(2) == '"':
            size_cm *= 2.54
    return ParsedNote(label_hint=label, size_cm=size_cm)
