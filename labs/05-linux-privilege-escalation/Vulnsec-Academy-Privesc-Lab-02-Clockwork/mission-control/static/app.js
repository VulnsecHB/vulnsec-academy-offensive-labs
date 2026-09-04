"use strict";

const runtime = {
  lab: null,
  progress: {
    solved: [],
    hints: {},
    walkthroughRevealed: false,
    activeQuestion: 0,
  },
};

function byId(id) {
  return document.getElementById(id);
}

function storageKey() {
  return `atlas-privesc-lab02-${runtime.lab.session_id}`;
}

function loadProgress() {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey()) || "null");
    if (saved && Array.isArray(saved.solved) && saved.hints && typeof saved.hints === "object") {
      runtime.progress = {
        solved: saved.solved.filter((id) => runtime.lab.questions.some((question) => question.id === id)),
        hints: saved.hints,
        walkthroughRevealed: Boolean(saved.walkthroughRevealed),
        activeQuestion: Number.isInteger(saved.activeQuestion) ? saved.activeQuestion : 0,
      };
    }
  } catch (_error) {
    localStorage.removeItem(storageKey());
  }
}

function saveProgress() {
  localStorage.setItem(storageKey(), JSON.stringify(runtime.progress));
}

function isSolved(questionId) {
  return runtime.progress.solved.includes(questionId);
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
  const hintTotal = Object.values(runtime.progress.hints).reduce((sum, value) => sum + Number(value || 0), 0);

  byId("progress-percent").textContent = `${percent}%`;
  byId("progress-copy").textContent = `${count} / ${total} objectives cleared`;
  byId("progress-bar").style.width = `${percent}%`;
  byId("mini-progress").style.height = `${Math.max(percent, 4)}%`;
  byId("cleared-copy").textContent = `${count}/${total} CLEARED`;
  byId("hints-used").textContent = String(hintTotal).padStart(2, "0");
  byId("completion-hints").textContent = String(hintTotal).padStart(2, "0");
  byId("completion-objectives").textContent = isComplete()
    ? `${String(total).padStart(2, "0")} / ${String(total).padStart(2, "0")}`
    : "SOLUTION";
  byId("open-debrief").classList.toggle("is-hidden", !isComplete());

  const current = isComplete()
    ? "DEBRIEF"
    : runtime.lab.questions[Math.min(runtime.progress.activeQuestion, total - 1)].eyebrow.toUpperCase();
  byId("current-phase").textContent = current;
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function renderQuestions() {
  const stack = byId("question-stack");
  stack.replaceChildren();

  runtime.lab.questions.forEach((question, index) => {
    const previousSolved = index === 0 || isSolved(runtime.lab.questions[index - 1].id);
    const locked = !previousSolved;
    const solved = isSolved(question.id);
    const open = solved || runtime.progress.activeQuestion === index;
    const hintCount = Number(runtime.progress.hints[question.id] || 0);

    const card = element("article", `question-card${locked ? " locked" : ""}${solved ? " correct" : ""}${open ? " open" : ""}`);
    const header = element("button", "question-header");
    header.type = "button";
    header.setAttribute("aria-expanded", String(open));
    header.disabled = locked;
    header.append(element("span", "question-index", solved ? "✓" : String(index + 1).padStart(2, "0")));
    const title = element("span");
    title.append(element("small", "", question.eyebrow), element("b", "", question.prompt));
    header.append(title, element("i", "", locked ? "LOCKED" : solved ? "CLEARED" : open ? "ACTIVE" : "OPEN"));
    header.addEventListener("click", () => {
      runtime.progress.activeQuestion = index;
      saveProgress();
      renderQuestions();
      updateProgressUI();
    });
    card.append(header);

    if (open && !locked) {
      const body = element("div", "question-body");
      body.append(element("p", "", question.helper));
      const form = element("form");
      const input = element("input");
      input.placeholder = question.placeholder;
      input.setAttribute("aria-label", question.prompt);
      input.autocomplete = "off";
      input.spellcheck = false;
      input.disabled = solved;
      const submit = element("button", "", solved ? "Verified" : "Verify answer");
      submit.type = "submit";
      submit.disabled = solved;
      input.addEventListener("input", () => { submit.disabled = solved || !input.value.trim(); });
      if (!solved) submit.disabled = true;
      form.append(input, submit);

      const feedback = element("div", "answer-feedback is-hidden");
      const feedbackTitle = element("b");
      const feedbackMessage = element("span");
      feedback.append(feedbackTitle, feedbackMessage);

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        submit.disabled = true;
        submit.textContent = "Checking…";
        try {
          const response = await fetch("/api/check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question_id: question.id, answer: input.value }),
          });
          if (!response.ok) throw new Error("Mission Control rejected the request");
          const result = await response.json();
          feedback.classList.remove("is-hidden", "correct", "wrong");
          feedback.classList.add(result.correct ? "correct" : "wrong");
          feedbackTitle.textContent = result.correct ? "SIGNAL CONFIRMED" : "NO MATCH";
          feedbackMessage.textContent = result.message;
          if (result.correct) {
            if (!isSolved(question.id)) runtime.progress.solved.push(question.id);
            runtime.progress.activeQuestion = Math.min(index + 1, runtime.lab.questions.length - 1);
            saveProgress();
            window.setTimeout(() => {
              renderQuestions();
              updateProgressUI();
            }, 620);
          } else {
            submit.disabled = false;
            submit.textContent = "Verify answer";
          }
        } catch (_error) {
          feedback.classList.remove("is-hidden", "correct");
          feedback.classList.add("wrong");
          feedbackTitle.textContent = "CONNECTION ERROR";
          feedbackMessage.textContent = "Mission Control could not check this answer. Confirm the lab is running.";
          submit.disabled = false;
          submit.textContent = "Try again";
        }
      });

      body.append(form, feedback);

      if (!solved) {
        const hintZone = element("div", "hint-zone");
        question.hints.slice(0, hintCount).forEach((hint, hintIndex) => {
          const row = element("div", "hint");
          row.append(element("span", "", `H${hintIndex + 1}`), document.createTextNode(hint));
          hintZone.append(row);
        });
        const reveal = element("button", "", hintCount >= question.hints.length ? "All hints revealed" : `Reveal hint ${hintCount + 1} / ${question.hints.length}`);
        reveal.type = "button";
        reveal.disabled = hintCount >= question.hints.length;
        reveal.addEventListener("click", () => {
          runtime.progress.hints[question.id] = Math.min(hintCount + 1, question.hints.length);
          saveProgress();
          renderQuestions();
          updateProgressUI();
        });
        hintZone.append(reveal);
        body.append(hintZone);
      }
      card.append(body);
    }
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
  byId("open-debrief").addEventListener("click", () => setView("walkthrough"));
  byId("reveal-walkthrough").addEventListener("click", () => {
    const dialog = byId("walkthrough-confirm");
    if (typeof dialog.showModal === "function") {
      dialog.showModal();
    } else if (window.confirm("Reveal the full walkthrough? This will expose every command, answer, and flag.")) {
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
    runtime.progress = { solved: [], hints: {}, walkthroughRevealed: false, activeQuestion: 0 };
    renderQuestions();
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
    document.querySelectorAll("[data-target]").forEach((node) => { node.textContent = runtime.lab.target_ip; });
    document.querySelectorAll("[data-port]").forEach((node) => { node.textContent = runtime.lab.port; });
    const previewLink = byId("preview-target-link");
    if (previewLink && runtime.lab.preview) previewLink.classList.remove("is-hidden");
    byId("environment-status").textContent = "ONLINE";
    byId("intel-status").textContent = "ENVIRONMENT ONLINE";
    renderQuestions();
    updateProgressUI();
    renderWalkthrough();
  } catch (_error) {
    byId("environment-status").textContent = "OFFLINE";
    byId("intel-status").textContent = "ENVIRONMENT OFFLINE";
    byId("portal-error").classList.remove("is-hidden");
  }
}

initialize();
