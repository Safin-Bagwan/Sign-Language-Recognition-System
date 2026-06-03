import { recognitionApi } from "./api.js";

const PREDICTION_INTERVAL_MS = 1400;
const MAX_HISTORY_ITEMS = 10;
const FRAME_CAPTURE_WIDTH = 320;

const state = {
  running: false,
  loading: false,
  timerId: null,
  sessionTimerId: null,
  dashboardTimerId: null,
  sessionStart: null,
  history: [],
  sentence: [],
  totalDetected: 0,
  totalConfidence: 0,
  cameraAvailable: false,
  apiMode: recognitionApi.mode,
};

const elements = {
  navToggle: document.querySelector(".nav-toggle"),
  navLinks: document.querySelector(".nav-links"),
  videoFrame: document.getElementById("videoFrame"),
  webcamVideo: document.getElementById("webcamVideo"),
  cameraPlaceholder: document.getElementById("cameraPlaceholder"),
  liveBadge: document.getElementById("liveBadge"),
  connectionStatus: document.getElementById("connectionStatus"),
  startBtn: document.getElementById("startBtn"),
  stopBtn: document.getElementById("stopBtn"),
  clearBtn: document.getElementById("clearBtn"),
  speakBtn: document.getElementById("speakBtn"),
  gestureLabel: document.getElementById("gestureLabel"),
  confidenceScore: document.getElementById("confidenceScore"),
  confidenceBar: document.getElementById("confidenceBar"),
  recognizedText: document.getElementById("recognizedText"),
  sentenceBox: document.getElementById("sentenceBox"),
  audioStatus: document.getElementById("audioStatus"),
  totalGestures: document.getElementById("totalGestures"),
  accuracyStat: document.getElementById("accuracyStat"),
  sessionDuration: document.getElementById("sessionDuration"),
  backendMode: document.getElementById("backendMode"),
  historyTable: document.getElementById("historyTable"),
  appAlert: document.getElementById("appAlert"),
};

const frameCanvas = document.createElement("canvas");
const frameContext = frameCanvas.getContext("2d");

function setText(element, text) {
  if (element) {
    element.textContent = text;
  }
}

function setAlert(message, type = "info") {
  if (!elements.appAlert) return;

  elements.appAlert.textContent = message;
  elements.appAlert.className = `app-alert ${type}`;
  elements.appAlert.hidden = !message;
}

function setLoading(isLoading, label = "Starting...") {
  state.loading = isLoading;
  elements.startBtn.disabled = isLoading || state.running;
  elements.stopBtn.disabled = isLoading || !state.running;
  elements.clearBtn.disabled = isLoading;
  elements.startBtn.setAttribute("aria-busy", String(isLoading));

  if (isLoading) {
    elements.startBtn.dataset.originalText ||= elements.startBtn.textContent;
    elements.startBtn.textContent = label;
  } else if (elements.startBtn.dataset.originalText) {
    elements.startBtn.textContent = elements.startBtn.dataset.originalText;
  }
}

function setStatusDot(container, text, modifier = "") {
  container.replaceChildren();

  const dot = document.createElement("span");
  dot.className = modifier ? `status-dot ${modifier}` : "status-dot";
  dot.setAttribute("aria-hidden", "true");

  container.append(dot, document.createTextNode(text));
}

function normalizePrediction(prediction) {
  const gesture = String(prediction?.gesture || "Unknown");
  const text = String(prediction?.text || "");
  const confidence = Math.max(0, Math.min(100, Number(prediction?.confidence || 0)));

  return {
    gesture,
    text,
    confidence,
    detected: Boolean(prediction?.detected ?? text),
    source: prediction?.source || state.apiMode,
    warning: prediction?.warning || "",
    message: prediction?.message || "",
  };
}

function initNavigation() {
  elements.navToggle.addEventListener("click", () => {
    const isOpen = elements.navToggle.getAttribute("aria-expanded") === "true";
    elements.navToggle.setAttribute("aria-expanded", String(!isOpen));
    elements.navLinks.classList.toggle("is-open", !isOpen);
    document.body.classList.toggle("nav-open", !isOpen);
  });

  elements.navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      elements.navToggle.setAttribute("aria-expanded", "false");
      elements.navLinks.classList.remove("is-open");
      document.body.classList.remove("nav-open");
    });
  });
}

function initRevealAnimations() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    document.querySelectorAll(".reveal").forEach((item) => item.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.16 }
  );

  document.querySelectorAll(".reveal").forEach((item) => observer.observe(item));
}

async function startCameraPreview() {
  if (!navigator.mediaDevices?.getUserMedia) {
    state.cameraAvailable = false;
    throw new Error("This browser does not support webcam access.");
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    elements.webcamVideo.srcObject = stream;
    await elements.webcamVideo.play();
    elements.webcamVideo.hidden = false;
    elements.cameraPlaceholder.hidden = true;
    state.cameraAvailable = true;
    return true;
  } catch (error) {
    state.cameraAvailable = false;
    elements.cameraPlaceholder.hidden = false;
    throw new Error("Camera access was denied or unavailable. Enable camera permission and try again.");
  }
}

function stopCameraPreview() {
  const stream = elements.webcamVideo.srcObject;
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }

  elements.webcamVideo.srcObject = null;
  elements.webcamVideo.hidden = true;
  elements.cameraPlaceholder.hidden = false;
}

function setRecognitionStatus(isRunning) {
  state.running = isRunning;
  elements.startBtn.disabled = state.loading || isRunning;
  elements.stopBtn.disabled = state.loading || !isRunning;
  elements.liveBadge.textContent = isRunning ? "Live" : "Idle";
  elements.liveBadge.classList.toggle("active", isRunning);
  elements.videoFrame.classList.toggle("is-running", isRunning);

  const label = isRunning
    ? state.cameraAvailable
      ? "Recognition active"
      : "Camera unavailable"
    : "Recognition idle";
  setText(elements.connectionStatus, label);
}

async function startRecognition() {
  if (state.running || state.loading) return;

  setAlert("", "info");
  setLoading(true, "Starting...");

  try {
    await startCameraPreview();
    const session = await recognitionApi.startSession();

    state.apiMode = session.source || "backend";

    setRecognitionStatus(true);
    state.sessionStart = Date.now();
    updateSessionDuration();
    state.sessionTimerId = window.setInterval(updateSessionDuration, 1000);
    state.dashboardTimerId = window.setInterval(refreshDashboard, 3000);
    state.timerId = window.setInterval(runPredictionCycle, PREDICTION_INTERVAL_MS);
    await refreshDashboard();
    await runPredictionCycle();
  } catch (error) {
    console.error(error);
    setAlert(error.message || "Recognition could not start. Check camera permissions or backend availability.", "error");
    stopCameraPreview();
    setRecognitionStatus(false);
  } finally {
    setLoading(false);
  }
}

async function stopRecognition() {
  if (!state.running || state.loading) return;

  setLoading(true, "Stopping...");

  try {
    await recognitionApi.stopSession();
  } catch (error) {
    console.error(error);
    setAlert("The backend did not confirm stop, but the local session was closed.", "warning");
  } finally {
    window.clearInterval(state.timerId);
    window.clearInterval(state.sessionTimerId);
    window.clearInterval(state.dashboardTimerId);
    state.timerId = null;
    state.sessionTimerId = null;
    state.dashboardTimerId = null;
    stopCameraPreview();
    setRecognitionStatus(false);
    await refreshDashboard().catch((error) => console.error(error));
    setLoading(false);
  }
}

function captureFrame() {
  const video = elements.webcamVideo;
  if (!state.cameraAvailable || !video.srcObject || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) {
    throw new Error("Camera frame is not ready yet.");
  }

  const sourceWidth = video.videoWidth || FRAME_CAPTURE_WIDTH;
  const sourceHeight = video.videoHeight || Math.round(FRAME_CAPTURE_WIDTH * 0.75);
  const scale = FRAME_CAPTURE_WIDTH / sourceWidth;
  frameCanvas.width = FRAME_CAPTURE_WIDTH;
  frameCanvas.height = Math.max(1, Math.round(sourceHeight * scale));
  frameContext.drawImage(video, 0, 0, frameCanvas.width, frameCanvas.height);
  return frameCanvas.toDataURL("image/jpeg", 0.82);
}

async function runPredictionCycle() {
  if (!state.running) return;

  try {
    const frame = captureFrame();
    const prediction = normalizePrediction(await recognitionApi.getPrediction(frame));
    appendPrediction(prediction);
    await refreshDashboard();

    if (prediction.warning) {
      setAlert(prediction.warning, "warning");
    }
  } catch (error) {
    console.error(error);
    setAlert(error.message || "Prediction failed. Waiting for the next recognition frame.", "error");
  }
}

function appendPrediction(prediction) {
  state.apiMode = prediction.source === "backend" ? "backend" : state.apiMode;

  if (prediction.detected && prediction.text) {
    const event = {
      ...prediction,
      time: new Date(),
    };

    state.history.unshift(event);
    state.history = state.history.slice(0, MAX_HISTORY_ITEMS);
    state.totalDetected += 1;
    state.totalConfidence += prediction.confidence;
    state.sentence.push(prediction.text);
  }

  setText(elements.gestureLabel, prediction.gesture);
  setText(elements.confidenceScore, `${prediction.confidence}%`);
  elements.confidenceBar.style.width = `${prediction.confidence}%`;
  setText(elements.recognizedText, prediction.text || prediction.message || "Waiting for a confident gesture.");

  renderSentence();
}

function renderSentence() {
  if (!state.sentence.length) {
    setText(elements.sentenceBox, "Your generated sentence will appear here.");
    elements.sentenceBox.classList.add("is-empty");
    elements.speakBtn.disabled = true;
    return;
  }

  setText(elements.sentenceBox, state.sentence.join(" ").replace(/\s+/g, " ").trim());
  elements.sentenceBox.classList.remove("is-empty");
  elements.speakBtn.disabled = false;
}

function renderStats() {
  setText(elements.totalGestures, String(state.totalDetected));
  const averageConfidence = state.totalDetected ? Math.round(state.totalConfidence / state.totalDetected) : 0;
  setText(elements.accuracyStat, `${averageConfidence}%`);
  setText(elements.backendMode, "Backend");
}

function createCell(text) {
  const cell = document.createElement("td");
  cell.textContent = text;
  return cell;
}

function renderHistory() {
  elements.historyTable.replaceChildren();

  if (!state.history.length) {
    const row = document.createElement("tr");
    row.className = "empty-row";
    const cell = createCell("No recognition events yet.");
    cell.colSpan = 4;
    row.append(cell);
    elements.historyTable.append(row);
    return;
  }

  state.history.forEach((item) => {
    const row = document.createElement("tr");
    row.append(
      createCell(item.time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })),
      createCell(item.gesture),
      createCell(item.text),
      createCell(`${item.confidence}%`)
    );
    elements.historyTable.append(row);
  });
}

function parseHistoryItem(item) {
  return {
    gesture: item.gesture || "Waiting",
    text: item.text || "",
    confidence: Number(item.confidence || 0),
    time: item.timestamp ? new Date(item.timestamp) : new Date(),
  };
}

function applyStats(stats) {
  if (!stats) return;
  state.totalDetected = Number(stats.total_gestures || 0);
  state.totalConfidence = state.totalDetected * Number(stats.average_confidence || 0);
  if (stats.session_started_at && !state.sessionStart) {
    state.sessionStart = Date.parse(stats.session_started_at);
  }
  renderStats();
}

function applyHistory(history) {
  if (!Array.isArray(history)) return;
  state.history = history.slice(0, MAX_HISTORY_ITEMS).map(parseHistoryItem);
  state.sentence = state.history
    .slice()
    .reverse()
    .map((item) => item.text)
    .filter(Boolean);
  renderSentence();
  renderHistory();
}

async function refreshDashboard() {
  const [statsResult, historyResult] = await Promise.all([
    recognitionApi.stats(),
    recognitionApi.history(),
  ]);
  applyStats(statsResult.stats);
  applyHistory(historyResult.history);
}

function updateSessionDuration() {
  if (!state.sessionStart) return;

  const elapsed = Math.floor((Date.now() - state.sessionStart) / 1000);
  const minutes = String(Math.floor(elapsed / 60)).padStart(2, "0");
  const seconds = String(elapsed % 60).padStart(2, "0");
  setText(elements.sessionDuration, `${minutes}:${seconds}`);
}

async function clearText() {
  state.history = [];
  state.sentence = [];
  state.totalDetected = 0;
  state.totalConfidence = 0;

  setText(elements.gestureLabel, "Waiting");
  setText(elements.confidenceScore, "0%");
  elements.confidenceBar.style.width = "0";
  setText(elements.recognizedText, "No gestures detected yet.");
  setText(elements.sessionDuration, "00:00");
  setAlert("", "info");
  state.sessionStart = state.running ? Date.now() : null;

  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
  setStatusDot(elements.audioStatus, "Audio idle", "muted");

  try {
    await recognitionApi.clear();
    await refreshDashboard();
  } catch (error) {
    console.error(error);
    setAlert("Local text was cleared, but backend history could not be reset.", "warning");
  }

  renderSentence();
  renderStats();
  renderHistory();
}

async function speakGeneratedSentence() {
  const text = state.sentence.join(" ").trim();
  if (!text) {
    setStatusDot(elements.audioStatus, "No sentence available", "muted");
    return;
  }

  elements.speakBtn.disabled = true;
  setStatusDot(elements.audioStatus, "Preparing speech");

  try {
    const speechResult = await recognitionApi.speak(text);

    setStatusDot(elements.audioStatus, speechResult.status === "queued" ? "Speech queued" : "Speech sent");

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);

      utterance.onstart = () => setStatusDot(elements.audioStatus, "Speaking");
      utterance.onend = () => {
        setStatusDot(elements.audioStatus, "Audio idle", "muted");
        elements.speakBtn.disabled = false;
      };
      utterance.onerror = () => {
        setStatusDot(elements.audioStatus, "Speech failed", "error");
        elements.speakBtn.disabled = false;
      };

      window.speechSynthesis.speak(utterance);
    } else {
      setStatusDot(elements.audioStatus, "Speech API unavailable", "error");
      elements.speakBtn.disabled = false;
    }
  } catch (error) {
    console.error(error);
    setStatusDot(elements.audioStatus, "Speech failed", "error");
    elements.speakBtn.disabled = false;
  }
}

function bindEvents() {
  elements.startBtn.addEventListener("click", startRecognition);
  elements.stopBtn.addEventListener("click", stopRecognition);
  elements.clearBtn.addEventListener("click", clearText);
  elements.speakBtn.addEventListener("click", speakGeneratedSentence);
}

async function initBackendStatus() {
  const health = await recognitionApi.health();
  state.apiMode = health.source || recognitionApi.mode;
  setText(elements.backendMode, "Backend");
  setText(elements.connectionStatus, health.service?.status === "ready" ? "Backend connected" : "Backend degraded");
  await refreshDashboard();
}

async function initApp() {
  initNavigation();
  initRevealAnimations();
  bindEvents();
  renderSentence();
  renderStats();
  renderHistory();

  try {
    await initBackendStatus();
  } catch (error) {
    console.error(error);
    setText(elements.connectionStatus, "Backend unavailable");
    setAlert(error.message || "Backend API is unavailable.", "error");
  }
}

document.addEventListener("DOMContentLoaded", initApp);
