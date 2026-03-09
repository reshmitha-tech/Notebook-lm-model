/**
 * app.js — AI Knowledge Helper Frontend Logic
 * Handles: file upload, Gemini processing, quiz, flashcards, audio, video, chat
 */

"use strict";

// ─── State ───────────────────────────────────────────
const state = {
  hasContent: false,
  content: null,
  chatHistory: [],
  audioGenerated: false,
  videoGenerated: false,
};

// ─── DOM References ───────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// Modals
const apiKeyModal = $("#apiKeyModal");
const uploadModal = $("#uploadModal");
const processingOvl = $("#processingOverlay");
const processingMsg = $("#processingMsg");

// Sidebar
const openUploadBtn = $("#openUploadBtn");
const welcomeUploadBtn = $("#welcomeUploadBtn");
const settingsBtn = $("#settingsBtn");
const sourcesList = $("#sourcesList");

// Upload
const dropZone = $("#dropZone");
const fileInput = $("#fileInput");
const closeUploadBtn = $("#closeUploadModal");
const uploadProgress = $("#uploadProgress");
const progressBar = $("#progressBar");
const uploadStatus = $("#uploadStatus");

// Tabs
const tabNav = $("#tabNav");
const welcomeState = $("#welcomeState");

// Summary
const summaryTitle = $("#summaryTitle");
const subjectTags = $("#subjectTags");
const summaryText = $("#summaryText");
const conceptsGrid = $("#conceptsGrid");
const manimSection = $("#manimSection");
const manimCode = $("#manimCode");

// Audio
const generateAudioBtn = $("#generateAudioBtn");
const audioLoading = $("#audioLoading");
const audioPlayerWrap = $("#audioPlayerWrap");
const audioPlayer = $("#audioPlayer");
const waveformViz = $("#waveformViz");

// Video
const generateVideoBtn = $("#generateVideoBtn");
const videoLoading = $("#videoLoading");
const videoLoadingMsg = $("#videoLoadingMsg");
const videoPlayerWrap = $("#videoPlayerWrap");
const videoPlayer = $("#videoPlayer");
const downloadVideoBtn = $("#downloadVideoBtn");

// Chat
const chatMessages = $("#chatMessages");
const chatInput = $("#chatInput");
const sendChatBtn = $("#sendChatBtn");
const clearChatBtn = $("#clearChatBtn");

// Badge
const aiBadge = $("#aiBadge");

// API Key
const apiKeyInput = $("#apiKeyInput");
const saveApiKeyBtn = $("#saveApiKeyBtn");

// ─── Initialization ───────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  buildWaveform();
  initTabs();
  checkApiKey();
});

// ─── API Key ──────────────────────────────────────────
async function checkApiKey() {
  try {
    const res = await fetch("/check-key");
    const data = await res.json();
    if (!data.has_key) showApiKeyModal();
  } catch (_) {
    showApiKeyModal();
  }
}

function showApiKeyModal() {
  apiKeyModal.style.display = "flex";
}

saveApiKeyBtn.addEventListener("click", async () => {
  const key = apiKeyInput.value.trim();
  if (!key || !key.startsWith("AIza")) {
    flashError(apiKeyInput, "Please enter a valid Gemini API key (starts with AIza…)");
    return;
  }
  const res = await fetch("/set-api-key", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: key }),
  });
  if (res.ok) {
    apiKeyModal.style.display = "none";
    toast("✅ API key saved for this session");
  }
});

settingsBtn.addEventListener("click", () => {
  apiKeyInput.value = "";
  apiKeyModal.style.display = "flex";
});

// ─── Upload Modal ─────────────────────────────────────
[openUploadBtn, welcomeUploadBtn].forEach((btn) => {
  btn?.addEventListener("click", () => {
    uploadModal.style.display = "flex";
    uploadProgress.style.display = "none";
    progressBar.style.width = "0";
  });
});

closeUploadBtn.addEventListener("click", () => {
  uploadModal.style.display = "none";
});

// Drag & Drop
dropZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault(); dropZone.classList.add("drag-over");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file && file.type === "application/pdf") handleFile(file);
  else toast("⚠️ Only PDF files are supported", "error");
});

async function handleFile(file) {
  // Show progress
  dropZone.style.display = "none";
  uploadProgress.style.display = "block";
  uploadStatus.textContent = "Uploading PDF…";
  animateProgress(0, 40, 800);

  const formData = new FormData();
  formData.append("file", file);

  let uploadData;
  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    uploadData = await res.json();
    if (!res.ok) throw new Error(uploadData.error || "Upload failed");
  } catch (err) {
    uploadModal.style.display = "none";
    dropZone.style.display = "block";
    toast(`❌ ${err.message}`, "error");
    return;
  }

  animateProgress(40, 70, 600);
  uploadStatus.textContent = "Analyzing with Gemini AI…";

  // Start processing
  uploadModal.style.display = "none";
  dropZone.style.display = "block";
  showProcessing("Analyzing your PDF with Gemini AI…");

  try {
    const res = await fetch("/process", { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Processing failed");

    state.content = data.content;
    state.hasContent = true;
    hideProcessing();
    populateUI(file.name, data.content);
    updateSourcesList(file.name);
    toast("✅ Your PDF has been analyzed!");
  } catch (err) {
    hideProcessing();
    toast(`❌ ${err.message}`, "error");
  }
}

function animateProgress(from, to, duration) {
  const start = Date.now();
  const step = () => {
    const t = Math.min(1, (Date.now() - start) / duration);
    progressBar.style.width = `${from + (to - from) * t}%`;
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

// ─── Processing Overlay ───────────────────────────────
function showProcessing(msg) {
  processingMsg.textContent = msg || "Processing…";
  processingOvl.style.display = "flex";
}
function hideProcessing() {
  processingOvl.style.display = "none";
}

// ─── Populate UI ─────────────────────────────────────
function populateUI(filename, content) {
  // Switch to summary tab
  welcomeState.style.display = "none";
  showTab("summary");

  // Badge
  aiBadge.textContent = "✨ Ready";
  aiBadge.className = "ai-badge ready";

  // Title & tags
  summaryTitle.textContent = filename.replace(/\.pdf$/i, "");
  subjectTags.innerHTML = "";
  const tagColors = ["tag-pink", "tag-teal", "tag-blue"];
  (content.subject_tags || []).forEach((tag, i) => {
    const span = document.createElement("span");
    span.className = `subject-tag ${tagColors[i % tagColors.length]}`;
    span.textContent = tag;
    subjectTags.appendChild(span);
  });

  // Summary
  summaryText.textContent = content.summary || "";

  // Key Concepts
  conceptsGrid.innerHTML = "";
  (content.key_concepts || []).forEach((c) => {
    const card = document.createElement("div");
    card.className = "concept-card";
    card.innerHTML = `<p class="concept-term">${escHtml(c.term)}</p><p class="concept-def">${escHtml(c.definition)}</p>`;
    conceptsGrid.appendChild(card);
  });

  // Manim Snippet
  if (content.is_stem && content.manim_snippet) {
    manimCode.textContent = content.manim_snippet;
    manimSection.style.display = "block";
  } else {
    manimSection.style.display = "none";
  }

  // Quiz
  buildQuiz(content.mcqs || []);

  // Flashcards
  buildFlashcards(content.key_concepts || []);

  // Reset audio/video
  state.audioGenerated = false;
  state.videoGenerated = false;
  audioPlayerWrap.style.display = "none";
  generateAudioBtn.style.display = "inline-flex";
  videoPlayerWrap.style.display = "none";
  generateVideoBtn.style.display = "inline-flex";

  // Chat welcome
  addChatBubble("ai", `I've analyzed "<strong>${escHtml(filename)}</strong>". I found ${(content.subject_tags || []).join(", ")} content with ${(content.key_concepts || []).length} key concepts. Ask me anything!`);
}

// ─── Tabs ─────────────────────────────────────────────
function initTabs() {
  tabNav.addEventListener("click", (e) => {
    const btn = e.target.closest(".tab-btn");
    if (!btn) return;
    if (!state.hasContent) {
      toast("Upload and process a PDF first!", "error");
      return;
    }
    showTab(btn.dataset.tab);
  });
}

function showTab(tabId) {
  // Update buttons
  $$(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tabId));
  // Show panel
  $$(".tab-panel").forEach((p) => (p.style.display = "none"));
  const panel = $(`#tab-${tabId}`);
  if (panel) panel.style.display = "block";
}

// ─── Quiz Builder ─────────────────────────────────────
function buildQuiz(mcqs) {
  const container = $("#quizContainer");
  container.innerHTML = "";
  mcqs.forEach((q, qi) => {
    const card = document.createElement("div");
    card.className = "quiz-card";
    const optLetters = ["A", "B", "C", "D"];
    const optionsHtml = (q.options || []).map((opt, oi) => `
      <div class="quiz-option" data-opt="${escHtml(opt)}" data-qi="${qi}">
        <span class="opt-letter">${optLetters[oi]}</span>
        <span>${escHtml(opt)}</span>
      </div>`).join("");

    card.innerHTML = `
      <p class="quiz-q"><span class="quiz-num">Q${qi + 1}.</span> ${escHtml(q.question)}</p>
      <div class="quiz-options">${optionsHtml}</div>
      <button class="quiz-check-btn" data-qi="${qi}" data-answer="${escHtml(q.answer)}">Check Answer</button>
      <div class="quiz-result" id="qr-${qi}"></div>`;
    container.appendChild(card);
  });

  // Option selection
  container.addEventListener("click", (e) => {
    const opt = e.target.closest(".quiz-option");
    const checkBtn = e.target.closest(".quiz-check-btn");

    if (opt) {
      const qi = opt.dataset.qi;
      $$(`[data-qi="${qi}"].quiz-option`).forEach((o) => o.classList.remove("selected"));
      opt.classList.add("selected");
    }

    if (checkBtn) {
      const qi = checkBtn.dataset.qi;
      const correctAns = checkBtn.dataset.answer;
      const selected = $(`.quiz-option.selected[data-qi="${qi}"]`);
      const resultDiv = $(`#qr-${qi}`);

      if (!selected) { toast("Select an option first!"); return; }
      const userAns = selected.dataset.opt;

      $$(`[data-qi="${qi}"].quiz-option`).forEach((o) => {
        if (o.dataset.opt === correctAns) o.classList.add("correct");
        else if (o === selected) o.classList.add("wrong");
      });

      if (userAns === correctAns) {
        resultDiv.className = "quiz-result show correct-res";
        resultDiv.textContent = "✅ Correct! Well done.";
      } else {
        resultDiv.className = "quiz-result show wrong-res";
        resultDiv.textContent = `❌ Incorrect. The correct answer is: "${correctAns}"`;
      }
      checkBtn.disabled = true;
    }
  });
}

// ─── Flashcards Builder ───────────────────────────────
function buildFlashcards(concepts) {
  const grid = $("#flashcardsGrid");
  grid.innerHTML = "";
  concepts.forEach((c, i) => {
    const wrap = document.createElement("div");
    wrap.className = "flashcard-wrap";
    wrap.innerHTML = `
      <div class="flashcard-inner">
        <div class="flashcard-front">
          <span class="fc-label">Term ${i + 1}</span>
          <p class="fc-term">${escHtml(c.term)}</p>
          <span class="fc-label" style="margin-top:10px;font-size:9px;opacity:0.5">Click to flip</span>
        </div>
        <div class="flashcard-back">
          <span class="fc-label">Definition</span>
          <p class="fc-def">${escHtml(c.definition)}</p>
        </div>
      </div>`;
    wrap.addEventListener("click", () => wrap.classList.toggle("flipped"));
    grid.appendChild(wrap);
  });
}

// ─── Audio Generation ─────────────────────────────────
generateAudioBtn?.addEventListener("click", async () => {
  if (!state.hasContent) { toast("Process a PDF first!", "error"); return; }
  generateAudioBtn.style.display = "none";
  audioLoading.style.display = "flex";

  try {
    const res = await fetch("/generate-audio", { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Audio generation failed");

    audioPlayer.src = data.audio_url + "?t=" + Date.now();
    audioPlayerWrap.style.display = "block";
    state.audioGenerated = true;
    toast("🎧 Audio summary generated!");
  } catch (err) {
    toast(`❌ ${err.message}`, "error");
    generateAudioBtn.style.display = "inline-flex";
  } finally {
    audioLoading.style.display = "none";
  }
});

// Animated waveform
function buildWaveform() {
  const heights = [8, 14, 22, 18, 30, 12, 25, 28, 16, 32, 20, 10, 26, 18, 24, 12, 30, 22, 8, 16];
  waveformViz.innerHTML = "";
  heights.forEach((h, i) => {
    const bar = document.createElement("div");
    bar.className = "wave-bar";
    bar.style.height = `${h}px`;
    bar.style.animationDelay = `${i * 0.07}s`;
    waveformViz.appendChild(bar);
  });
}

// ─── Video Generation ────────────────────────────────
generateVideoBtn?.addEventListener("click", async () => {
  if (!state.hasContent) { toast("Process a PDF first!", "error"); return; }
  generateVideoBtn.style.display = "none";
  videoLoading.style.display = "flex";
  videoLoadingMsg.textContent = "Rendering animated slides… this may take ~30s";

  // Rotate messages while generating
  const msgs = [
    "🎬 Creating animated slides…",
    "🎨 Applying gradient backgrounds…",
    "✨ Adding fade transitions…",
    "📽️ Encoding video frames…",
    "Almost there…",
  ];
  let mi = 0;
  const msgInterval = setInterval(() => {
    mi = (mi + 1) % msgs.length;
    videoLoadingMsg.textContent = msgs[mi];
  }, 6000);

  try {
    const res = await fetch("/generate-video", { method: "POST" });
    const data = await res.json();
    clearInterval(msgInterval);
    if (!res.ok) throw new Error(data.error || "Video generation failed");

    videoPlayer.src = data.video_url + "?t=" + Date.now();
    if (downloadVideoBtn) {
      downloadVideoBtn.href = data.video_url;
      downloadVideoBtn.download = `summary_video_${Date.now()}.mp4`;
    }
    videoPlayerWrap.style.display = "block";
    state.videoGenerated = true;
    toast("🎥 Video animation ready!");
  } catch (err) {
    clearInterval(msgInterval);
    toast(`❌ ${err.message}`, "error");
    generateVideoBtn.style.display = "inline-flex";
  } finally {
    videoLoading.style.display = "none";
  }
});

// ─── AI Chat ─────────────────────────────────────────
sendChatBtn.addEventListener("click", sendChat);
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendChat(); }
});
clearChatBtn.addEventListener("click", () => {
  chatMessages.innerHTML = "";
  state.chatHistory = [];
  addChatBubble("ai", "Chat cleared! Ask me anything about your document.");
});

async function sendChat() {
  const q = chatInput.value.trim();
  if (!q) return;
  if (!state.hasContent) { toast("Upload a PDF first!", "error"); return; }

  addChatBubble("user", escHtml(q));
  chatInput.value = "";

  // Typing indicator
  const typingId = addChatBubble("ai", "<em>Thinking…</em>", true);

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q, history: state.chatHistory }),
    });
    const data = await res.json();
    removeTyping(typingId);
    if (!res.ok) throw new Error(data.error || "Chat failed");

    const answer = data.answer || "I couldn't generate a response.";
    addChatBubble("ai", markdownToHtml(answer));

    // Update history (simplified — just track last 6 turns)
    state.chatHistory.push(
      { role: "user", parts: [q] },
      { role: "model", parts: [answer] }
    );
    if (state.chatHistory.length > 12) state.chatHistory = state.chatHistory.slice(-12);
  } catch (err) {
    removeTyping(typingId);
    addChatBubble("ai", `❌ Error: ${escHtml(err.message)}`);
  }
}

let typingCounter = 0;
function addChatBubble(role, html, isTyping = false) {
  const id = isTyping ? `typing-${++typingCounter}` : null;
  const div = document.createElement("div");
  div.className = `chat-msg ${role}${isTyping ? " typing-indicator" : ""}`;
  if (id) div.id = id;
  const now = new Date();
  div.innerHTML = `
    <div class="bubble">${html}</div>
    <span class="msg-time">${now.getHours()}:${String(now.getMinutes()).padStart(2, "0")}</span>`;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return id;
}

function removeTyping(id) {
  const el = $(`#${id}`);
  if (el) el.remove();
}

// ─── Sources List ─────────────────────────────────────
function updateSourcesList(filename) {
  sourcesList.innerHTML = `
    <div class="source-item source-active">
      <span class="material-symbols-outlined" style="color:var(--accent-pink)">picture_as_pdf</span>
      <span class="source-name" title="${escHtml(filename)}">${escHtml(filename)}</span>
    </div>`;
  aiBadge.textContent = "✨ Ready";
  aiBadge.className = "ai-badge ready";
}

// ─── Utilities ───────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function markdownToHtml(text) {
  // Very simple markdown: bold, italic, inline code, line breaks
  return escHtml(text)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/\n/g, "<br/>");
}

function flashError(el, msg) {
  el.style.borderColor = "var(--accent-pink)";
  el.placeholder = msg;
  setTimeout(() => { el.style.borderColor = ""; el.placeholder = "AIza…"; }, 3000);
}

// Toast notifications
let toastTimeout;
function toast(msg, type = "success") {
  let toastEl = document.getElementById("toastEl");
  if (!toastEl) {
    toastEl = document.createElement("div");
    toastEl.id = "toastEl";
    Object.assign(toastEl.style, {
      position: "fixed", bottom: "24px", right: "24px", zIndex: "9999",
      padding: "12px 20px", borderRadius: "10px", fontSize: "13px",
      fontWeight: "600", backdropFilter: "blur(12px)",
      transition: "opacity 0.3s ease, transform 0.3s ease",
      transform: "translateY(10px)", opacity: "0",
      maxWidth: "320px", lineHeight: "1.5",
    });
    document.body.appendChild(toastEl);
  }
  clearTimeout(toastTimeout);
  toastEl.textContent = msg;
  if (type === "error") {
    Object.assign(toastEl.style, { background: "rgba(255,85,85,0.15)", border: "1px solid rgba(255,85,85,0.35)", color: "#ff8888" });
  } else {
    Object.assign(toastEl.style, { background: "rgba(80,250,123,0.12)", border: "1px solid rgba(80,250,123,0.3)", color: "#50fa7b" });
  }
  requestAnimationFrame(() => {
    toastEl.style.opacity = "1";
    toastEl.style.transform = "translateY(0)";
  });
  toastTimeout = setTimeout(() => {
    toastEl.style.opacity = "0";
    toastEl.style.transform = "translateY(10px)";
  }, 4000);
}
