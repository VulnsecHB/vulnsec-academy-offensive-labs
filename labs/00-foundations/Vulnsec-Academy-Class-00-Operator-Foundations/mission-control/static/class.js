"use strict";

function byId(id) {
  return document.getElementById(id);
}

function setView(name) {
  document.querySelectorAll("[data-view]").forEach((view) => {
    view.classList.toggle("is-hidden", view.dataset.view !== name);
  });
  document.querySelectorAll(".rail [data-view-target]").forEach((button) => {
    button.classList.toggle("active", button.dataset.viewTarget === name);
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function bindControls() {
  document.querySelectorAll("[data-view-target]").forEach((button) => {
    button.addEventListener("click", () => setView(button.dataset.viewTarget));
  });
  document.querySelectorAll("[data-jump]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.getAttribute("data-jump");
      setView("toolkit");
      window.setTimeout(() => {
        const node = document.getElementById(id);
        if (node) node.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 60);
    });
  });
}

async function boot() {
  bindControls();
  try {
    const response = await fetch("/api/state");
    if (!response.ok) throw new Error("offline");
    byId("environment-status").textContent = "CLASS LIVE";
    byId("portal-error").classList.add("is-hidden");
  } catch (_error) {
    byId("environment-status").textContent = "OFFLINE";
    byId("portal-error").classList.remove("is-hidden");
  }
}

boot();
