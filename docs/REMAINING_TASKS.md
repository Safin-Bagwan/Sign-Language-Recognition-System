# Remaining Tasks

Last updated: 2026-06-03

## High Priority

| Task | Estimated effort | Dependencies |
| --- | --- | --- |
| Verify browser webcam prediction end-to-end against Flask. | Medium | Backend server running; browser with camera permission; current frame-capture frontend. |
| Add backend automated tests for all API endpoints. | Medium | Stable Flask app factory and test mocks for recognition/TTS services. |
| Add frontend automated tests for API communication, webcam startup handling, UI updates, and error states. | High | Test tooling decision, likely Node/Vitest or Playwright. |
| Update stale README files to remove obsolete mock fallback instructions. | Low | Confirm final frontend API behavior. |
| Fix any runtime issues found during browser verification. | Unknown | Browser verification results. |
| Clean up Git state by staging/committing or intentionally reverting partial work. | Low | User decision on commit strategy. |

## Medium Priority

| Task | Estimated effort | Dependencies |
| --- | --- | --- |
| Refactor or archive duplicate legacy scripts under `backend/app/`. | Medium | Confirm which scripts are still required for training/data collection. |
| Document production deployment with WSGI server, environment variables, CORS origins, and model/database setup. | Medium | Finalized backend configuration. |
| Add model-positive prediction test using a known frame fixture. | Medium | Suitable fixture image and expected class/confidence behavior. |
| Add CI workflow for compile checks and tests. | Medium | Automated tests exist. |
| Validate accessibility and responsive behavior after frontend changes. | Medium | Browser test setup. |

## Low Priority

| Task | Estimated effort | Dependencies |
| --- | --- | --- |
| Move large datasets/models out of normal Git tracking or document Git LFS/artifact setup. | High | Repository ownership decision; artifact hosting or LFS setup. |
| Add structured logging around prediction request latency and errors. | Low | Production logging requirements. |
| Add request-size and frame-rate guidance for deployment. | Low | Final prediction performance measurements. |
| Add frontend package metadata if formal frontend tests are adopted. | Low | Test tooling decision. |

## Known Dependencies Between Tasks

- Browser verification should happen before final README updates because the docs should describe confirmed behavior.
- Backend tests should be added before CI.
- Frontend tests require a tooling decision and may require `package.json`.
- Legacy cleanup should happen after confirming training/data-generation workflows still work or are intentionally out of scope.
- Production deployment docs should be finalized after configuration and test coverage are stable.

