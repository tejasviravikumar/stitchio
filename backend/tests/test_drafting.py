import numpy as np
import pytest
from shapely.geometry import Polygon

from app.schemas.measurement import Measurements
from app.services.drafting import draft_pattern
from app.services.drafting.geometry import sample_outline
from app.services.export.pdf_tiled import render_pdf
from app.services.export.svg import render_svg


def _m(**kw):
    base = dict(height_cm=165, bust_cm=92, waist_cm=72, hip_cm=98)
    return Measurements(**{**base, **kw})


def test_bodice_basic_structure():
    piece = draft_pattern("bodice", _m()).pieces[0]
    assert piece.cut_on_fold and piece.fold_line and piece.grainline
    assert len(piece.darts) == 1 and piece.darts[0].intake_cm > 0
    assert len(piece.notches) >= 2


def test_outline_is_a_valid_polygon():
    piece = draft_pattern("bodice", _m()).pieces[0]
    poly = Polygon(sample_outline(piece.outline))
    assert poly.is_valid and poly.area > 500


def test_waist_edge_matches_waist_measurement():
    m = _m()
    piece = draft_pattern("bodice", m).pieces[0]
    waist_len = piece.outline[4].x - piece.outline[5].x - piece.darts[0].intake_cm
    assert waist_len == pytest.approx((m.waist_cm + 4) / 4, abs=0.01)


def test_seam_allowance_grows_outline_but_not_past_fold():
    piece = draft_pattern("bodice", _m(), 1.5).pieces[0]
    stitch, cut = Polygon(sample_outline(piece.outline)), Polygon(piece.cutting_line)
    assert cut.area > stitch.area
    assert min(x for x, _ in piece.cutting_line) >= -1e-6


def test_zero_seam_allowance_has_no_cutting_line():
    assert draft_pattern("bodice", _m(), 0).pieces[0].cutting_line == []


def test_larger_waist_means_smaller_dart():
    small = draft_pattern("bodice", _m(waist_cm=66)).pieces[0].darts[0].intake_cm
    large = draft_pattern("bodice", _m(waist_cm=80)).pieces[0].darts[0].intake_cm
    assert small > large


def test_waist_bigger_than_bust_gives_no_dart_and_a_warning():
    pattern = draft_pattern("bodice", _m(bust_cm=90, waist_cm=100, hip_cm=105))
    assert pattern.pieces[0].darts == []
    assert any("Waist larger than bust" in warning for warning in pattern.meta["warnings"])


def test_inconsistent_measurements_raise():
    with pytest.raises(ValueError):
        draft_pattern("bodice", _m(bust_cm=160, waist_length_cm=30))


def test_unknown_garment():
    with pytest.raises(ValueError):
        draft_pattern("spaceship", _m())


def test_svg_and_pdf_export():
    pattern = draft_pattern("bodice", _m())
    svg = render_svg(pattern)
    assert svg.startswith("<svg") and "PLACE ON FOLD" in svg and "FRONT BODICE" in svg
    pdf = render_pdf(pattern)
    pages = pdf.count(b"/Type /Page") - pdf.count(b"/Type /Pages")
    assert pdf.startswith(b"%PDF") and pages >= 2


def test_fitting_recovers_parameters():
    from app.services.fitting.cmaes_fit import fit_bodice_to_outline

    truth = _m(shoulder_width_cm=41, waist_length_cm=43, ease_cm=9)
    target = np.array(sample_outline(draft_pattern("bodice", truth, 0).pieces[0].outline, 24))
    result = fit_bodice_to_outline(target, _m(), max_evals=500)
    assert result.loss < 0.15
    assert result.params["shoulder_width_cm"] == pytest.approx(41, abs=1.0)
    assert result.params["waist_length_cm"] == pytest.approx(43, abs=1.0)
    assert result.params["ease_cm"] == pytest.approx(9, abs=1.5)
