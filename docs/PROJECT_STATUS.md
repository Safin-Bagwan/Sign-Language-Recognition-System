# Project Status

Last updated: 2026-06-03

## Current Project Architecture

The repository is organized as a full-stack Sign Language Recognition System:

- `frontend/`
  - Static single-page web interface served from `frontend/index.html`.
  - Styling in `frontend/css/style.css`.
  - Browser logic in `frontend/js/app.js`.
  - API wrapper in `frontend/js/api.js`.
  - `frontend/pages/` currently contains only `.gitkeep`; there are no separate page files.
- `backend/`
  - Flask app entry point in `backend/app.py`.
  - WSGI export in `backend/wsgi.py`.
  - Configuration classes in `backend/config.py`.
  - API routes in `backend/routes/api.py`.
  - Recognition runtime in `backend/services/recognition_service.py`.
  - Text-to-speech runtime in `backend/services/tts_service.py`.
  - Shared paths and response helpers in `backend/utils/`.
  - Legacy training/data-collection scripts in `backend/app/`.
  - Model file at `backend/models/cnn_model_keras2.h5`.
  - SQLite label database at `backend/data/database/gesture_db.db`.

## Completion Percentages

These percentages reflect the current working tree, including uncommitted changes.

| Area | Completion |
| --- | ---: |
| Frontend | 75% |
| Backend | 80% |
| Frontend-backend integration | 60% |
| Overall project | 68% |

## Current Branch

`feature/frontend`

## Last Major Changes

The current working tree contains partial integration work that has not been committed:

- Frontend mock prediction implementation was removed from `frontend/js/api.js`.
- Frontend API calls now target real Flask endpoints only.
- `frontend/js/app.js` now includes browser webcam startup, canvas frame capture, JPEG data URL generation, `/api/predict` calls with a frame payload, and periodic `/api/stats` plus `/api/history` refreshes.
- `backend/routes/api.py` now requires a base64 frame for normal web prediction and allows `source: "server"` only for explicit server-camera mode.
- `backend/services/recognition_service.py` now supports `source="browser"` and `source="server"` recognition modes. Browser mode no longer opens `cv2.VideoCapture`.
- `backend/config.py` was added with development/testing/production configuration classes.
- `backend/wsgi.py` was added for WSGI serving.
- `backend/app.py` now loads configuration, applies configured CORS, and adds security headers.
- `backend/services/tts_service.py` was hardened to pass text as a PowerShell argument instead of interpolating it directly into a command string.

## Current Blockers

- Browser webcam prediction has not been verified end-to-end in an actual browser after the latest edits.
- No formal backend or frontend automated test files exist yet.
- The frontend README and root README still contain stale references to mock fallback behavior.
- Legacy duplicate scripts remain under `backend/app/`, including `final.py` and `final_backup.py`.
- New integration files are untracked in Git.
- Large model and dataset files are still tracked in the repository.
- Production deployment is not fully documented.
- No committed package/test configuration exists for frontend testing.
- No CI workflow exists.

## Verification Completed In Current State

The following checks were run after the partial integration edits:

- `backend\venv\Scripts\python.exe -m compileall -q backend`
  - Result: passed.
- Flask test-client smoke check:
  - `GET /api/health` returned `200`.
  - `POST /api/predict` with no frame returned `400`.
  - `GET /api/stats` returned `200`.
  - `GET /api/history` returned `200`.
  - `POST /api/text-to-speech` with empty text returned `400`.

No browser test, webcam test, Playwright test, or model-positive prediction test has been completed after the latest edits.

## Production Readiness Assessment

Current state: **Not production ready**.

Reasoning:

- The backend has a real Flask API, configuration classes, CORS configuration, security headers, WSGI export, TensorFlow model loading, MediaPipe processing, OpenCV preprocessing, SQLite label lookup, stats, history, and TTS support.
- The frontend now appears to be wired toward browser-frame prediction, but the end-to-end browser path has not been tested.
- Automated tests are missing.
- Documentation is stale in places.
- Git state is not clean.
- Legacy duplicate code remains.
- Production asset/model/data management is unresolved.

