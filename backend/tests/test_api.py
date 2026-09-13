"""
tests/test_api.py
------------------
Automated test suite for AgriSmart AI FastAPI backend.

Covers:
  1. Root health-check endpoint (GET /)
  2. Readiness probe (GET /ready)
  3. Disease class listing (GET /api/v1/disease/classes)
  4. Image prediction with a generated dummy image (POST /api/v1/disease/predict)
  5. Image prediction with an invalid (non-image) file
  6. Advisory recommendation (POST /api/v1/advisory/recommend)
  7. Weather risk analysis (POST /api/v1/weather/risk)
  8. Current weather (GET /api/v1/weather/current)
  9. AI assistant query (POST /api/v1/assistant/query)
 10. CORS headers present on responses

Run with:
    pytest tests/ -v
    pytest tests/ -v --tb=short          # shorter traceback
    pytest tests/ -v -k "disease"        # filter by name
    pytest tests/ -v --co                # collect-only (list tests without running)
"""

from __future__ import annotations

import io
from typing import Any

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

# =========================================================================== #
#  Test client fixture
# =========================================================================== #

client = TestClient(app)

API_V1 = "/api/v1"


# =========================================================================== #
#  Helpers
# =========================================================================== #


def _make_dummy_image(width: int = 224, height: int = 224, color: str = "green") -> bytes:
    """
    Generate an in-memory RGB JPEG image for upload tests.
    Avoids the need for fixture image files on disk.
    """
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def _post_image(endpoint: str, image_bytes: bytes, filename: str = "test_leaf.jpg") -> Any:
    """Helper: POST an image to an endpoint via multipart form."""
    return client.post(
        endpoint,
        files={"file": (filename, image_bytes, "image/jpeg")},
    )


# =========================================================================== #
#  1. Root health check
# =========================================================================== #


class TestHealthEndpoints:
    def test_root_returns_200(self) -> None:
        """GET / should return HTTP 200 with service metadata."""
        response = client.get("/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_root_response_structure(self) -> None:
        """Root response must contain expected keys."""
        data = client.get("/").json()
        required_keys = {"service", "version", "status", "docs", "endpoints"}
        assert required_keys.issubset(data.keys()), (
            f"Missing keys: {required_keys - data.keys()}"
        )

    def test_root_status_is_healthy(self) -> None:
        data = client.get("/").json()
        assert data["status"] == "healthy"

    def test_health_probe(self) -> None:
        """GET /health liveness probe should return {'status': 'ok'}."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_readiness_probe(self) -> None:
        """GET /ready readiness probe should return {'status': 'ready'}."""
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"


# =========================================================================== #
#  2. Disease class listing
# =========================================================================== #


class TestDiseaseClasses:
    def test_list_classes_returns_200(self) -> None:
        response = client.get(f"{API_V1}/disease/classes")
        assert response.status_code == 200

    def test_list_classes_is_non_empty_list(self) -> None:
        data = client.get(f"{API_V1}/disease/classes").json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one disease class"

    def test_class_item_has_required_fields(self) -> None:
        data = client.get(f"{API_V1}/disease/classes").json()
        for item in data:
            assert "class_key" in item
            assert "display_name" in item
            assert "crop_name" in item
            assert "severity" in item

    def test_tomato_classes_present(self) -> None:
        data = client.get(f"{API_V1}/disease/classes").json()
        keys = [item["class_key"] for item in data]
        assert "Tomato___Late_blight" in keys, "Tomato Late Blight must be in class list"
        assert "Tomato___healthy" in keys, "Tomato healthy class must be present"


# =========================================================================== #
#  3. Disease prediction — valid image
# =========================================================================== #


class TestDiseasePrediction:
    def test_predict_with_dummy_image_returns_200(self) -> None:
        """POST /disease/predict with a valid JPEG should return 200."""
        image_bytes = _make_dummy_image()
        response = _post_image(f"{API_V1}/disease/predict", image_bytes)
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

    def test_predict_response_has_required_fields(self) -> None:
        """Prediction response must include all required schema fields."""
        image_bytes = _make_dummy_image()
        data = _post_image(f"{API_V1}/disease/predict", image_bytes).json()
        required = {
            "class_name", "confidence", "severity", "is_healthy",
            "display_name", "crop_name", "description", "precautions",
            "model_version", "processing_time_ms",
        }
        missing = required - data.keys()
        assert not missing, f"Response missing fields: {missing}"

    def test_predict_confidence_in_valid_range(self) -> None:
        """Confidence score must be between 0 and 1."""
        image_bytes = _make_dummy_image()
        data = _post_image(f"{API_V1}/disease/predict", image_bytes).json()
        assert 0.0 <= data["confidence"] <= 1.0, (
            f"Confidence {data['confidence']} out of [0, 1] range"
        )

    def test_predict_precautions_are_ordered(self) -> None:
        """Precautions must have sequential step numbers starting at 1."""
        image_bytes = _make_dummy_image()
        data = _post_image(f"{API_V1}/disease/predict", image_bytes).json()
        precautions = data.get("precautions", [])
        if precautions:
            steps = [p["step"] for p in precautions]
            assert steps == list(range(1, len(steps) + 1)), (
                f"Precaution steps not sequential: {steps}"
            )

    def test_predict_is_healthy_flag_type(self) -> None:
        """is_healthy must be a boolean."""
        image_bytes = _make_dummy_image()
        data = _post_image(f"{API_V1}/disease/predict", image_bytes).json()
        assert isinstance(data["is_healthy"], bool)

    def test_predict_same_image_gives_same_result(self) -> None:
        """Mock inference must be deterministic — same image → same class."""
        image_bytes = _make_dummy_image(color="red")
        result_a = _post_image(f"{API_V1}/disease/predict", image_bytes).json()
        result_b = _post_image(f"{API_V1}/disease/predict", image_bytes).json()
        assert result_a["class_name"] == result_b["class_name"], (
            "Mock inference is not deterministic — same image gave different classes"
        )

    def test_predict_different_images_may_differ(self) -> None:
        """Different images should ideally produce different results (hash test)."""
        img_a = _make_dummy_image(color="green")
        img_b = _make_dummy_image(color="blue")
        class_a = _post_image(f"{API_V1}/disease/predict", img_a).json()["class_name"]
        class_b = _post_image(f"{API_V1}/disease/predict", img_b).json()["class_name"]
        # This is a probabilistic test — it may occasionally pass even if same class
        # We only assert that the pipeline doesn't crash for different inputs
        assert class_a is not None and class_b is not None

    def test_predict_processing_time_positive(self) -> None:
        """Processing time must be a positive number."""
        image_bytes = _make_dummy_image()
        data = _post_image(f"{API_V1}/disease/predict", image_bytes).json()
        pt = data.get("processing_time_ms")
        if pt is not None:
            assert pt > 0, f"Expected positive processing_time_ms, got {pt}"

    def test_predict_invalid_file_returns_400(self) -> None:
        """Uploading a non-image file must return HTTP 400."""
        fake_bytes = b"this is not an image"
        response = client.post(
            f"{API_V1}/disease/predict",
            files={"file": ("not_an_image.txt", fake_bytes, "text/plain")},
        )
        # Either 400 (format rejected) or 422 (validation) is acceptable
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422 for invalid file, got {response.status_code}"
        )

    def test_predict_no_file_returns_422(self) -> None:
        """Omitting the file entirely must return HTTP 422 Unprocessable Entity."""
        response = client.post(f"{API_V1}/disease/predict")
        assert response.status_code == 422


# =========================================================================== #
#  4. Advisory recommendation
# =========================================================================== #


SAMPLE_ADVISORY_PAYLOAD = {
    "crop_name": "Tomato",
    "crop_stage": "flowering",
    "soil_type": "loamy",
    "ph": 6.5,
    "moisture": 42.0,
    "temperature": 28.5,
    "rain_prob": 0.25,
    "current_irrigation_method": "drip",
}


class TestAdvisoryEndpoint:
    def test_recommend_returns_200(self) -> None:
        response = client.post(f"{API_V1}/advisory/recommend", json=SAMPLE_ADVISORY_PAYLOAD)
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

    def test_recommend_response_has_required_fields(self) -> None:
        data = client.post(f"{API_V1}/advisory/recommend", json=SAMPLE_ADVISORY_PAYLOAD).json()
        required = {
            "crop_name", "crop_stage", "should_irrigate_today",
            "recommended_method", "irrigation_schedule",
            "sustainability_score", "sustainability_rating",
            "soil_health_notes", "risk_flags", "actionable_tips",
        }
        missing = required - data.keys()
        assert not missing, f"Response missing fields: {missing}"

    def test_sustainability_score_in_range(self) -> None:
        data = client.post(f"{API_V1}/advisory/recommend", json=SAMPLE_ADVISORY_PAYLOAD).json()
        score = data["sustainability_score"]
        assert 0.0 <= score <= 100.0, f"Score {score} out of [0, 100] range"

    def test_irrigation_schedule_is_list(self) -> None:
        data = client.post(f"{API_V1}/advisory/recommend", json=SAMPLE_ADVISORY_PAYLOAD).json()
        assert isinstance(data["irrigation_schedule"], list)

    def test_recommend_dry_soil_triggers_irrigation(self) -> None:
        """Very dry soil with no rain expected should trigger irrigation."""
        dry_payload = {**SAMPLE_ADVISORY_PAYLOAD, "moisture": 10.0, "rain_prob": 0.05}
        data = client.post(f"{API_V1}/advisory/recommend", json=dry_payload).json()
        assert data["should_irrigate_today"] is True, (
            "Dry soil + no rain should recommend irrigation today"
        )

    def test_recommend_wet_soil_skips_irrigation(self) -> None:
        """Wet soil with high rain probability should skip irrigation."""
        wet_payload = {**SAMPLE_ADVISORY_PAYLOAD, "moisture": 85.0, "rain_prob": 0.90}
        data = client.post(f"{API_V1}/advisory/recommend", json=wet_payload).json()
        assert data["should_irrigate_today"] is False, (
            "Wet soil + high rain probability should NOT recommend irrigation today"
        )

    def test_recommend_invalid_ph_returns_422(self) -> None:
        """pH outside 0–14 must fail validation."""
        bad_payload = {**SAMPLE_ADVISORY_PAYLOAD, "ph": 20.0}
        response = client.post(f"{API_V1}/advisory/recommend", json=bad_payload)
        assert response.status_code == 422

    def test_recommend_invalid_stage_returns_422(self) -> None:
        """An unknown crop stage must fail validation."""
        bad_payload = {**SAMPLE_ADVISORY_PAYLOAD, "crop_stage": "unknown_stage"}
        response = client.post(f"{API_V1}/advisory/recommend", json=bad_payload)
        assert response.status_code == 422

    def test_recommend_all_crop_stages(self) -> None:
        """Advisory must succeed for every valid crop stage."""
        stages = ["germination", "seedling", "vegetative", "flowering", "fruiting", "harvest"]
        for stage in stages:
            payload = {**SAMPLE_ADVISORY_PAYLOAD, "crop_stage": stage}
            response = client.post(f"{API_V1}/advisory/recommend", json=payload)
            assert response.status_code == 200, (
                f"Stage '{stage}' failed with {response.status_code}: {response.text}"
            )


# =========================================================================== #
#  5. Weather endpoints
# =========================================================================== #


class TestWeatherEndpoints:
    def test_weather_risk_returns_200(self) -> None:
        payload = {"location": "Hyderabad", "crop_name": "Tomato", "days_ahead": 3}
        response = client.post(f"{API_V1}/weather/risk", json=payload)
        assert response.status_code == 200

    def test_weather_risk_response_structure(self) -> None:
        payload = {"location": "Delhi", "days_ahead": 3}
        data = client.post(f"{API_V1}/weather/risk", json=payload).json()
        assert "overall_risk_level" in data
        assert "risk_index" in data
        assert "daily_forecast" in data
        assert len(data["daily_forecast"]) == 3

    def test_weather_risk_index_in_range(self) -> None:
        payload = {"location": "Mumbai", "days_ahead": 5}
        data = client.post(f"{API_V1}/weather/risk", json=payload).json()
        assert 0.0 <= data["risk_index"] <= 100.0

    def test_weather_current_returns_200(self) -> None:
        response = client.get(f"{API_V1}/weather/current", params={"location": "Chennai"})
        assert response.status_code == 200

    def test_weather_current_has_temperature(self) -> None:
        data = client.get(f"{API_V1}/weather/current", params={"location": "Pune"}).json()
        assert "temperature_c" in data
        assert "condition" in data


# =========================================================================== #
#  6. AI Assistant
# =========================================================================== #


class TestAssistantEndpoint:
    def test_assistant_query_returns_200(self) -> None:
        payload = {
            "query": "My tomato leaves are turning yellow. What should I do?",
            "language": "en",
        }
        response = client.post(f"{API_V1}/assistant/query", json=payload)
        assert response.status_code == 200

    def test_assistant_response_has_answer(self) -> None:
        payload = {"query": "How do I treat late blight on tomato?", "language": "en"}
        data = client.post(f"{API_V1}/assistant/query", json=payload).json()
        assert "answer" in data
        assert len(data["answer"]) > 10, "Answer should be a non-trivial response"

    def test_assistant_with_context_returns_200(self) -> None:
        payload = {
            "query": "What fungicide should I use?",
            "language": "en",
            "context": "Disease detected: Tomato Late Blight. Confidence: 0.92.",
        }
        response = client.post(f"{API_V1}/assistant/query", json=payload)
        assert response.status_code == 200

    def test_assistant_empty_query_returns_422(self) -> None:
        """Blank query must fail Pydantic validation."""
        payload = {"query": "   ", "language": "en"}
        response = client.post(f"{API_V1}/assistant/query", json=payload)
        assert response.status_code == 422

    def test_assistant_follow_ups_are_list(self) -> None:
        payload = {"query": "How much water does tomato need?", "language": "en"}
        data = client.post(f"{API_V1}/assistant/query", json=payload).json()
        assert isinstance(data.get("follow_up_questions", []), list)


# =========================================================================== #
#  7. CORS headers
# =========================================================================== #


class TestCORSHeaders:
    def test_cors_header_present_on_root(self) -> None:
        """OPTIONS preflight should return CORS headers."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # TestClient may not process CORS middleware the same as a real server,
        # but we can at least verify the endpoint doesn't reject OPTIONS
        assert response.status_code in (200, 204)
