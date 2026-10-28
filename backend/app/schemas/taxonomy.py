"""Seam label taxonomy.

FIXED EARLY ON PURPOSE: the ML model's output layer is sized from this list.
Never reorder or delete labels once a model is trained; only append at the end.
"""
from enum import Enum


class SeamLabel(str, Enum):
    SIDE_SEAM = "side_seam"
    SHOULDER_SEAM = "shoulder_seam"
    ARMHOLE = "armhole"
    NECKLINE = "neckline"
    CENTER_FRONT = "center_front"
    CENTER_BACK = "center_back"
    WAIST_SEAM = "waist_seam"
    HEM = "hem"
    SLEEVE_CAP = "sleeve_cap"
    SLEEVE_UNDERARM = "sleeve_underarm"
    BUST_DART = "bust_dart"
    WAIST_DART = "waist_dart"
    SHOULDER_DART = "shoulder_dart"
    PRINCESS_SEAM = "princess_seam"
    YOKE = "yoke"
    POCKET_EDGE = "pocket_edge"
    PLACKET = "placket"
    UNKNOWN = "unknown"


LABELS: list[SeamLabel] = list(SeamLabel)
LABEL_TO_INDEX: dict[SeamLabel, int] = {label: i for i, label in enumerate(LABELS)}

# Plain-language explanations for beginners (also used for tooltips in the UI).
LABEL_INFO: dict[SeamLabel, str] = {
    SeamLabel.SIDE_SEAM: "Joins the front and back under the arm, down to the hem.",
    SeamLabel.SHOULDER_SEAM: "Joins the front and back over the shoulder.",
    SeamLabel.ARMHOLE: "The curved opening where a sleeve attaches.",
    SeamLabel.NECKLINE: "The curved edge around the neck.",
    SeamLabel.CENTER_FRONT: "The vertical line down the middle of the front.",
    SeamLabel.CENTER_BACK: "The vertical line down the middle of the back.",
    SeamLabel.WAIST_SEAM: "A horizontal seam at the waist joining a top and a skirt.",
    SeamLabel.HEM: "The bottom edge, usually folded and stitched.",
    SeamLabel.SLEEVE_CAP: "The curved top of a sleeve that fits into the armhole.",
    SeamLabel.SLEEVE_UNDERARM: "The seam along the underside of the sleeve.",
    SeamLabel.BUST_DART: "A folded wedge that shapes fabric over the bust.",
    SeamLabel.WAIST_DART: "A folded wedge that shapes fabric in at the waist.",
    SeamLabel.SHOULDER_DART: "A small wedge at the shoulder for shaping.",
    SeamLabel.PRINCESS_SEAM: "A long curved seam from shoulder or armhole to hem that shapes the body.",
    SeamLabel.YOKE: "A shaped panel across the shoulders or hips.",
    SeamLabel.POCKET_EDGE: "The opening edge of a pocket.",
    SeamLabel.PLACKET: "A reinforced strip where a garment opens and closes.",
    SeamLabel.UNKNOWN: "Not sure yet. Add a note and the bunny will try again.",
}