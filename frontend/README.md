# Frontend

Static portfolio-quality frontend for the Sign Language Recognition System.

## Structure

```text
frontend/
├── index.html
├── css/
│   └── style.css
├── js/
│   ├── api.js
│   └── app.js
├── assets/
│   ├── images/
│   │   └── hero-ai-sign-language.png
│   └── icons/
└── pages/
```

## Backend Integration

`js/api.js` centralizes API integration for the Flask service:

- `GET /api/health`
- `POST /api/start-recognition`
- `POST /api/stop-recognition`
- `POST /api/predict`
- `POST /api/text-to-speech`
- `GET /api/stats`
- `GET /api/history`
- `POST /api/clear`

The UI calls the Flask API by default. If the Flask API is unavailable, the frontend uses a small mock fallback so the page remains presentable during demos.

To require real backend responses and disable fallback mock data from the browser console:

```js
localStorage.setItem("slrs-disable-mock-fallback", "true");
location.reload();
```

To allow fallback mock mode again:

```js
localStorage.removeItem("slrs-disable-mock-fallback");
location.reload();
```
