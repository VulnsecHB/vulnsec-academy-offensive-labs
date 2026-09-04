"use strict";

const runtime = {
  lab: null,
  progress: {
    solved: [],
    walkthroughRevealed: false,
  },
};

function byId(id) {
  return document.getElementById(id);
}

function storageKey() {
  return `atlas-${runtime.lab.lab_id}-${runtime.lab.session_id}`;
}

function loadProgress() {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey()) || "null");
    if (saved && Array.isArray(saved.solved)) {
      runtime.progress = {
        solved: saved.solved.filter((id) => runtime.lab.questions.some((item) => item.id === id)),
        walkthroughRevealed: Boolean(saved.walkthroughRevealed),
      };
    }
  } catch (_error) {
    localStorage.removeItem(storageKey());
  }
}

function saveProgress() {
  localStorage.setItem(storageKey(), JSON.stringify(runtime.progress));
}

function isSolved(id) {
  return runtime.progress.solved.includes(id);
}

function solvedCount() {
  return runtime.progress.solved.length;
}

function isComplete() {
  return solvedCount() === runtime.lab.questions.length;
}

function setView(name) {
  document.querySelectorAll("[data-view]").forEach((view) => {
    view.classList.toggle("is-hidden", view.dataset.view !== name);
  });
  document.querySelectorAll(".rail [data-view-target]").forEach((button) => {
    button.classList.toggle("active", button.dataset.viewTarget === name);
  });
  if (name === "walkthrough") renderWalkthrough();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function updateProgressUI() {
  const count = solvedCount();
  const total = runtime.lab.questions.length;
  const percent = Math.round((count / total) * 100);
  byId("progress-percent").textContent = `${percent}%`;
  byId("progress-copy").textContent = `${count} / ${total} flags accepted`;
  byId("progress-bar").style.width = `${percent}%`;
  if (byId("mini-progress")) byId("mini-progress").style.height = `${Math.max(percent, 4)}%`;
  if (byId("cleared-copy")) byId("cleared-copy").textContent = `${count}/${total} FLAGS`;
  if (byId("hints-used")) byId("hints-used").textContent = "00";
  if (byId("completion-hints")) byId("completion-hints").textContent = "00";
  if (byId("completion-objectives")) byId("completion-objectives").textContent = isComplete() ? "02 / 02" : "SOLUTION";
  if (byId("open-debrief")) byId("open-debrief").classList.toggle("is-hidden", !isComplete());
  if (byId("current-phase")) {
    byId("current-phase").textContent = isComplete()
      ? "DEBRIEF"
      : isSolved("user")
        ? "02 / ROOT FLAG"
        : "01 / USER FLAG";
  }
  if (byId("intel-user")) byId("intel-user").textContent = isSolved("user") ? "ACCEPTED" : "PENDING";
  if (byId("intel-root")) byId("intel-root").textContent = isSolved("root") ? "ACCEPTED" : "PENDING";
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function renderFlags() {
  const stack = byId("question-stack");
  stack.replaceChildren();
  runtime.lab.questions.forEach((flag, index) => {
    const solved = isSolved(flag.id);
    const card = element("article", `question-card${solved ? " correct" : ""} open`);
    const header = element("button", "question-header");
    header.type = "button";
    header.setAttribute("aria-expanded", "true");
    header.append(element("span", "question-index", solved ? "✓" : String(index + 1).padStart(2, "0")));
    const title = element("span");
    title.append(element("small", "", flag.eyebrow), element("b", "", flag.prompt));
    header.append(title, element("i", "", solved ? "ACCEPTED" : "OPEN"));
    const body = element("div", "question-body");
    body.append(element("p", "", flag.helper));
    const feedback = element("p", `feedback${solved ? " ok" : ""}`, solved ? flag.success : "");
    if (!solved) {
      const form = element("form", "answer-form");
      const input = element("input");
      input.type = "text";
      input.autocomplete = "off";
      input.spellcheck = false;
      input.placeholder = flag.placeholder;
      const submit = element("button", "primary-button compact", "Submit flag");
      submit.type = "submit";
      form.append(input, submit);
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const response = await fetch("/api/check", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question_id: flag.id, answer: input.value }),
        });
        const result = await response.json();
        if (result.correct) {
          if (!isSolved(flag.id)) runtime.progress.solved.push(flag.id);
          saveProgress();
          renderFlags();
          updateProgressUI();
        } else {
          feedback.className = "feedback bad";
          feedback.textContent = result.message || flag.error;
        }
      });
      body.append(form);
    }
    body.append(feedback);
    card.append(header, body);
    stack.append(card);
  });
}

function renderWalkthrough() {
  const unlocked = isComplete() || runtime.progress.walkthroughRevealed;
  byId("walkthrough-lock").classList.toggle("is-hidden", unlocked);
  byId("walkthrough-content").classList.toggle("is-hidden", !unlocked);
  if (unlocked) {
    const badge = byId("walkthrough-badge");
    badge.textContent = isComplete() ? "MISSION COMPLETE" : "SOLUTION REVEALED";
    badge.className = isComplete() ? "success-badge" : "warning-badge";
  }
}

function revealWalkthrough() {
  runtime.progress.walkthroughRevealed = true;
  saveProgress();
  renderWalkthrough();
}

function bindControls() {
  document.querySelectorAll("[data-view-target]").forEach((button) => {
    button.addEventListener("click", () => setView(button.dataset.viewTarget));
  });
  const openDebrief = byId("open-debrief");
  if (openDebrief) openDebrief.addEventListener("click", () => setView("walkthrough"));
  byId("reveal-walkthrough").addEventListener("click", () => {
    const dialog = byId("walkthrough-confirm");
    if (typeof dialog.showModal === "function") {
      dialog.showModal();
    } else if (window.confirm("Reveal the full walkthrough? This will expose every command and both flags.")) {
      revealWalkthrough();
    }
  });
  byId("cancel-walkthrough-reveal").addEventListener("click", () => byId("walkthrough-confirm").close());
  byId("confirm-walkthrough-reveal").addEventListener("click", () => {
    byId("walkthrough-confirm").close();
    revealWalkthrough();
  });
  byId("walkthrough-confirm").addEventListener("click", (event) => {
    if (event.target === event.currentTarget) event.currentTarget.close();
  });
  byId("repeat-mission").addEventListener("click", () => {
    localStorage.removeItem(storageKey());
    runtime.progress = { solved: [], walkthroughRevealed: false };
    renderFlags();
    updateProgressUI();
    setView("mission");
  });
}

async function initialize() {
  bindControls();
  try {
    const response = await fetch("/api/state", { cache: "no-store" });
    if (!response.ok) throw new Error("State unavailable");
    runtime.lab = await response.json();
    loadProgress();
    document.querySelectorAll("[data-target]").forEach((node) => {
      node.textContent = runtime.lab.target_ip;
    });
    document.querySelectorAll("[data-port]").forEach((node) => {
      node.textContent = runtime.lab.port;
    });
    const previewLink = byId("preview-target-link");
    if (previewLink && runtime.lab.preview) previewLink.classList.remove("is-hidden");
    byId("environment-status").textContent = "ONLINE";
    if (byId("intel-status")) byId("intel-status").textContent = "ENVIRONMENT ONLINE";
    renderFlags();
    updateProgressUI();
    renderWalkthrough();
  } catch (_error) {
    byId("environment-status").textContent = "OFFLINE";
    if (byId("intel-status")) byId("intel-status").textContent = "ENVIRONMENT OFFLINE";
    byId("portal-error").classList.remove("is-hidden");
  }
}

initialize();
