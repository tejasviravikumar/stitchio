"""End-to-end upload, trace, measurement, pattern, and export checks."""


def _upload(client, png_bytes):
    response = client.post("/api/images", files={"file": ("dress.png", png_bytes, "image/png")})
    assert response.status_code == 201, response.text
    return response.json()


def test_upload_rejects_non_images(client):
    response = client.post("/api/images", files={"file": ("x.png", b"definitely not a png", "image/png")})
    assert response.status_code == 400


def test_trace_flow(client, png_bytes):
    image = _upload(client, png_bytes)
    assert (image["width"], image["height"]) == (120, 160)
    side = [{"x": 0.15, "y": 0.3 + i * 0.05} for i in range(10)]
    response = client.post("/api/traces", json={"image_id": image["id"], "points": side})
    assert response.status_code == 201, response.text
    trace = response.json()
    assert trace["label"] == "side_seam" and not trace["confirmed_by_user"]
    response = client.patch(f"/api/traces/{trace['id']}", json={"label": "princess_seam", "note": "curved"})
    assert response.json()["label"] == "princess_seam" and response.json()["confirmed_by_user"]
    assert len(client.get(f"/api/traces?image_id={image['id']}").json()) >= 1
    assert client.delete(f"/api/traces/{trace['id']}").status_code == 204


def test_note_overrides_geometry(client):
    points = [{"x": 0.5, "y": 0.2 + i * 0.05} for i in range(8)]
    response = client.post("/api/traces/classify", json={"points": points, "note": "this is the armhole"})
    assert response.json()["suggestions"][0]["label"] == "armhole"


def test_trace_on_someone_elses_image_is_404(client):
    response = client.post("/api/traces", json={"image_id": 99999, "points": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]})
    assert response.status_code == 404


def test_invalid_trace_points_rejected(client):
    response = client.post("/api/traces/classify", json={"points": [{"x": 2, "y": 0}, {"x": 0, "y": 0}]})
    assert response.status_code == 422


def test_labels_endpoint(client):
    labels = client.get("/api/traces/labels").json()
    assert any(label["label"] == "bust_dart" for label in labels)


def test_measurements_and_pattern_flow(client, measurements):
    response = client.post("/api/measurements", json={"name": "me", "measurements": measurements})
    assert response.status_code == 201
    measurement_id = response.json()["id"]
    response = client.post("/api/patterns/generate", json={"measurements_id": measurement_id})
    assert response.status_code == 200
    pattern = response.json()
    assert pattern["pieces"][0]["darts"]
    response = client.post("/api/patterns", json={"name": "My bodice", "pattern": pattern})
    assert response.status_code == 201
    pattern_id = response.json()["id"]
    svg = client.get(f"/api/patterns/{pattern_id}/svg")
    assert svg.status_code == 200 and svg.headers["content-type"].startswith("image/svg+xml")
    pdf = client.get(f"/api/patterns/{pattern_id}/pdf")
    assert pdf.content.startswith(b"%PDF")
    pattern["pieces"][0]["name"] = "front_bodice_edited"
    response = client.put(f"/api/patterns/{pattern_id}", json={"name": "Edited", "pattern": pattern})
    assert response.json()["data"]["pieces"][0]["name"] == "front_bodice_edited"


def test_generate_needs_measurements(client):
    assert client.post("/api/patterns/generate", json={}).status_code == 422


def test_generate_inconsistent_measurements_is_422(client):
    body = {"measurements": {"height_cm": 165, "bust_cm": 165, "waist_cm": 120, "hip_cm": 150, "waist_length_cm": 30}}
    response = client.post("/api/patterns/generate", json=body)
    assert response.status_code == 422 and "inconsistent" in response.json()["detail"]


def test_measurement_warning_is_friendly(client):
    response = client.post("/api/measurements/check", json={"height_cm": 165, "bust_cm": 80, "waist_cm": 90, "hip_cm": 100})
    assert "rare" in response.json()["warnings"][0]
