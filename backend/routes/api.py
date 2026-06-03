import base64
import binascii
import logging

import cv2
import numpy as np
from flask import Blueprint, request

from backend.services.recognition_service import RecognitionError, recognition_service
from backend.services.tts_service import tts_service
from backend.utils.responses import error, success

LOGGER = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/health")
def health():
    return success({"service": recognition_service.health()})


@api_bp.post("/start-recognition")
def start_recognition():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source", "browser")
    try:
        return success(recognition_service.start(source=source))
    except RecognitionError as exc:
        LOGGER.exception("Failed to start recognition")
        return error(str(exc), 503, "recognition_start_failed")


@api_bp.post("/stop-recognition")
def stop_recognition():
    return success(recognition_service.stop())


@api_bp.post("/predict")
def predict():
    try:
        payload = request.get_json(silent=True) or {}
        frame = _frame_from_request()
        if frame is None and payload.get("source") != "server":
            return error("A base64 encoded image frame is required for web prediction.", 400, "frame_required")
        prediction = recognition_service.predict(frame=frame)
        return success({"prediction": prediction})
    except RecognitionError as exc:
        return error(str(exc), 409, "prediction_failed")
    except ValueError as exc:
        return error(str(exc), 400, "invalid_frame")
    except Exception as exc:
        LOGGER.exception("Unexpected prediction error")
        return error(str(exc), 500, "prediction_error")


@api_bp.post("/text-to-speech")
def text_to_speech():
    payload = request.get_json(silent=True) or {}
    try:
        result = tts_service.speak(payload.get("text", ""))
        return success(result)
    except ValueError as exc:
        return error(str(exc), 400, "invalid_text")


@api_bp.get("/stats")
def stats():
    return success({"stats": recognition_service.stats()})


@api_bp.get("/history")
def history():
    return success({"history": recognition_service.history()})


@api_bp.post("/clear")
def clear():
    return success({"stats": recognition_service.clear(), "history": []})


def _frame_from_request():
    payload = request.get_json(silent=True) or {}
    encoded_frame = payload.get("frame")
    if not encoded_frame:
        return None

    if "," in encoded_frame:
        encoded_frame = encoded_frame.split(",", 1)[1]

    try:
        frame_bytes = base64.b64decode(encoded_frame, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Frame must be a valid base64 encoded image.") from exc

    buffer = np.frombuffer(frame_bytes, dtype=np.uint8)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Frame could not be decoded as an image.")

    return frame
