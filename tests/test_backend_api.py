import base64
import unittest
from unittest.mock import Mock, patch

import cv2
import numpy as np

from backend.app import create_app


class BackendApiTestCase(unittest.TestCase):
    def setUp(self):
        self.recognition = Mock()
        self.recognition.health.return_value = {
            "status": "ready",
            "running": False,
            "source": None,
        }
        self.recognition.start.return_value = {
            "status": "started",
            "running": True,
            "source": "browser",
        }
        self.recognition.stop.return_value = {
            "status": "stopped",
            "running": False,
            "source": None,
        }
        self.recognition.predict.return_value = {
            "detected": True,
            "gesture": "Hello",
            "text": "Hello",
            "confidence": 91.5,
            "class_id": 1,
            "message": "Prediction ready",
            "timestamp": "2026-06-04T00:00:00+00:00",
        }
        self.recognition.stats.return_value = {
            "running": True,
            "source": "browser",
            "total_gestures": 1,
            "average_confidence": 91.5,
            "history_count": 1,
            "last_prediction": self.recognition.predict.return_value,
        }
        self.recognition.history.return_value = [self.recognition.predict.return_value]
        self.recognition.clear.return_value = {
            "running": True,
            "source": "browser",
            "total_gestures": 0,
            "average_confidence": 0,
            "history_count": 0,
            "last_prediction": None,
        }
        self.tts = Mock()
        self.tts.speak.return_value = {"status": "queued", "text": "Hello"}

        self.recognition_patch = patch("backend.routes.api.recognition_service", self.recognition)
        self.tts_patch = patch("backend.routes.api.tts_service", self.tts)
        self.recognition_patch.start()
        self.tts_patch.start()
        self.addCleanup(self.recognition_patch.stop)
        self.addCleanup(self.tts_patch.stop)

        self.app = create_app("testing")
        self.client = self.app.test_client()

    def test_health_returns_service_status(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["ok"])
        self.assertEqual(response.json["service"]["status"], "ready")

    def test_start_recognition_defaults_to_browser_source(self):
        response = self.client.post("/api/start-recognition", json={})

        self.assertEqual(response.status_code, 200)
        self.recognition.start.assert_called_once_with(source="browser")
        self.assertEqual(response.json["status"], "started")

    def test_start_recognition_accepts_server_source(self):
        response = self.client.post("/api/start-recognition", json={"source": "server"})

        self.assertEqual(response.status_code, 200)
        self.recognition.start.assert_called_once_with(source="server")

    def test_stop_recognition_stops_session(self):
        response = self.client.post("/api/stop-recognition")

        self.assertEqual(response.status_code, 200)
        self.recognition.stop.assert_called_once()
        self.assertEqual(response.json["status"], "stopped")

    def test_predict_requires_frame_for_browser_prediction(self):
        response = self.client.post("/api/predict", json={})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json["ok"])
        self.assertEqual(response.json["error"]["code"], "frame_required")
        self.recognition.predict.assert_not_called()

    def test_predict_accepts_base64_data_url_frame(self):
        response = self.client.post("/api/predict", json={"frame": self._jpeg_data_url()})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["ok"])
        self.assertEqual(response.json["prediction"]["gesture"], "Hello")
        frame = self.recognition.predict.call_args.kwargs["frame"]
        self.assertIsInstance(frame, np.ndarray)
        self.assertGreater(frame.size, 0)

    def test_predict_rejects_invalid_base64_frame(self):
        response = self.client.post("/api/predict", json={"frame": "data:image/jpeg;base64,not-valid"})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json["ok"])
        self.assertEqual(response.json["error"]["code"], "invalid_frame")
        self.recognition.predict.assert_not_called()

    def test_predict_allows_explicit_server_source_without_frame(self):
        response = self.client.post("/api/predict", json={"source": "server"})

        self.assertEqual(response.status_code, 200)
        self.recognition.predict.assert_called_once_with(frame=None)

    def test_text_to_speech_sends_text(self):
        response = self.client.post("/api/text-to-speech", json={"text": "Hello"})

        self.assertEqual(response.status_code, 200)
        self.tts.speak.assert_called_once_with("Hello")
        self.assertEqual(response.json["status"], "queued")

    def test_text_to_speech_returns_validation_error(self):
        self.tts.speak.side_effect = ValueError("Text is required.")

        response = self.client.post("/api/text-to-speech", json={"text": ""})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"]["code"], "invalid_text")

    def test_stats_returns_recognition_stats(self):
        response = self.client.get("/api/stats")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["stats"]["total_gestures"], 1)

    def test_history_returns_recent_predictions(self):
        response = self.client.get("/api/history")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["history"][0]["gesture"], "Hello")

    def test_clear_resets_history_and_stats(self):
        response = self.client.post("/api/clear")

        self.assertEqual(response.status_code, 200)
        self.recognition.clear.assert_called_once()
        self.assertEqual(response.json["history"], [])
        self.assertEqual(response.json["stats"]["total_gestures"], 0)

    def test_frontend_index_is_served(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sign Language Recognition System", response.data)

    def _jpeg_data_url(self):
        image = np.zeros((8, 8, 3), dtype=np.uint8)
        ok, buffer = cv2.imencode(".jpg", image)
        self.assertTrue(ok)
        encoded = base64.b64encode(buffer.tobytes()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"


if __name__ == "__main__":
    unittest.main()
