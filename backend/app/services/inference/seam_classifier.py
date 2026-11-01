"""Small geometry-and-note classifier used until a trained model is available."""
from app.schemas.taxonomy import SeamLabel
from app.schemas.trace import LabelScore, TracePoint
from app.services.inference.notes_parser import parse_note


class SeamClassifier:
    def predict(self, points: list[TracePoint], note: str | None = None) -> list[LabelScore]:
        parsed = parse_note(note)
        label = parsed.label_hint
        confidence = 0.95 if label else 0.55
        if label is None and len(points) >= 2:
            dx = abs(points[-1].x - points[0].x)
            dy = abs(points[-1].y - points[0].y)
            center_x = sum(p.x for p in points) / len(points)
            if dy >= dx * 1.4 and (center_x < 0.25 or center_x > 0.75):
                label, confidence = SeamLabel.SIDE_SEAM, 0.82
            elif dx >= dy * 1.4:
                label, confidence = SeamLabel.HEM, 0.7
            else:
                label, confidence = SeamLabel.UNKNOWN, 0.4
        if label is None:
            label = SeamLabel.UNKNOWN
        return [LabelScore(label=label, score=confidence), LabelScore(label=SeamLabel.UNKNOWN, score=1 - confidence)]


_classifier = SeamClassifier()


def get_classifier() -> SeamClassifier:
    return _classifier
