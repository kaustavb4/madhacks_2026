// Push-to-talk on spacebar: hold to record, release to send to /converse,
// play the spoken reply back. Screen-reader friendly via aria-live regions.
const BACKEND_URL = "http://127.0.0.1:8000";

const statusEl = document.getElementById("status");
const transcriptEl = document.getElementById("transcript");
const audioEl = document.getElementById("reply-audio");

let mediaRecorder = null;
let chunks = [];
let recording = false;

function setStatus(text) {
  statusEl.textContent = text;
}

async function startRecording() {
  if (recording) return;
  recording = true;
  setStatus("Listening...");
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  chunks = [];
  mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
  mediaRecorder.onstop = sendRecording;
  mediaRecorder.start();
}

function stopRecording() {
  if (!recording || !mediaRecorder) return;
  recording = false;
  mediaRecorder.stop();
  mediaRecorder.stream.getTracks().forEach((t) => t.stop());
  setStatus("Thinking...");
}

async function sendRecording() {
  const blob = new Blob(chunks, { type: "audio/webm" });
  const form = new FormData();
  form.append("audio", blob, "speech.webm");

  const resp = await fetch(`${BACKEND_URL}/converse`, { method: "POST", body: form });
  const heard = resp.headers.get("X-Heard") || "";
  const reply = resp.headers.get("X-Reply") || "";
  transcriptEl.textContent = `You said: "${heard}". Jarvis: "${reply}"`;

  const audioBuffer = await resp.blob();
  if (audioBuffer.size > 0) {
    audioEl.src = URL.createObjectURL(audioBuffer);
    audioEl.play();
  }
  setStatus("Ready.");
}

document.addEventListener("keydown", (e) => {
  if (e.code === "Space" && !e.repeat) {
    e.preventDefault();
    startRecording();
  }
});

document.addEventListener("keyup", (e) => {
  if (e.code === "Space") {
    e.preventDefault();
    stopRecording();
  }
});
