import { readFile } from "node:fs/promises";
import { test } from "node:test";
import assert from "node:assert/strict";

const apiSource = await readFile(new URL("../frontend/js/api.js", import.meta.url), "utf8");
const appSource = await readFile(new URL("../frontend/js/app.js", import.meta.url), "utf8");

test("API wrapper uses the Flask backend without mock fallbacks", () => {
  assert.match(apiSource, /const API_BASE_URL =/);
  assert.match(apiSource, /http:\/\/127\.0\.0\.1:5000\/api/);
  assert.doesNotMatch(apiSource, /apiOrMock|mock|fallback/i);
});

test("start session requests browser-frame recognition mode", () => {
  assert.match(apiSource, /\/start-recognition/);
  assert.match(apiSource, /JSON\.stringify\(\{\s*source:\s*"browser"\s*\}\)/);
});

test("prediction requests send the captured frame payload", () => {
  assert.match(apiSource, /async getPrediction\(frame\)/);
  assert.match(apiSource, /\/predict/);
  assert.match(apiSource, /JSON\.stringify\(\{\s*frame\s*\}\)/);
});

test("webcam startup uses browser media permissions and handles denied access", () => {
  assert.match(appSource, /navigator\.mediaDevices\?\.getUserMedia/);
  assert.match(appSource, /getUserMedia\(\{\s*video:\s*true,\s*audio:\s*false\s*\}\)/);
  assert.match(appSource, /Camera access was denied or unavailable/);
});

test("frame capture converts the video preview to a JPEG data URL", () => {
  assert.match(appSource, /drawImage\(video/);
  assert.match(appSource, /toDataURL\("image\/jpeg",\s*0\.82\)/);
});

test("dashboard refresh reads live stats and history APIs", () => {
  assert.match(appSource, /recognitionApi\.stats\(\)/);
  assert.match(appSource, /recognitionApi\.history\(\)/);
  assert.match(appSource, /applyStats\(statsResult\.stats\)/);
  assert.match(appSource, /applyHistory\(historyResult\.history\)/);
});

test("prediction and initialization errors surface user-visible alerts", () => {
  assert.match(appSource, /setAlert\(error\.message \|\| "Prediction failed/);
  assert.match(appSource, /setAlert\(error\.message \|\| "Backend API is unavailable\.", "error"\)/);
});
