const API_BASE_URL = window.location.origin.includes("5000")
  ? `${window.location.origin}/api`
  : "http://127.0.0.1:5000/api";
const REQUEST_TIMEOUT_MS = 5000;

function withTimeout(promiseFactory, timeoutMs = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);

  return promiseFactory(controller.signal).finally(() => window.clearTimeout(timer));
}

function normalizeError(error) {
  if (error.name === "AbortError") {
    return new Error("The backend did not respond before the request timeout.");
  }
  return error;
}

async function requestJson(path, options = {}) {
  try {
    const response = await withTimeout((signal) =>
      fetch(`${API_BASE_URL}${path}`, {
        ...options,
        signal,
        headers: {
          "Content-Type": "application/json",
          ...(options.headers || {}),
        },
      })
    );

    const payload = await response.json().catch(() => ({}));
    if (!response.ok || payload.ok === false) {
      const message = payload.error?.message || `API request failed: ${response.status}`;
      throw new Error(message);
    }

    return {
      ...payload,
      source: "backend",
    };
  } catch (error) {
    throw normalizeError(error);
  }
}

export const recognitionApi = {
  get mode() {
    return "backend";
  },

  async health() {
    return requestJson("/health", { method: "GET" });
  },

  async startSession() {
    return requestJson("/start-recognition", {
      method: "POST",
      body: JSON.stringify({ source: "browser" }),
    });
  },

  async stopSession() {
    return requestJson("/stop-recognition", { method: "POST" });
  },

  async getPrediction(frame) {
    const payload = await requestJson("/predict", {
      method: "POST",
      body: JSON.stringify({ frame }),
    });
    return {
      ...payload.prediction,
      source: "backend",
    };
  },

  async speak(text) {
    return requestJson("/text-to-speech", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
  },

  async stats() {
    return requestJson("/stats", { method: "GET" });
  },

  async history() {
    return requestJson("/history", { method: "GET" });
  },

  async clear() {
    return requestJson("/clear", { method: "POST" });
  },
};
