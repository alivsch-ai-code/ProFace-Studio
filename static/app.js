const form = document.getElementById("gen-form");
const photos = document.getElementById("photos");
const statusEl = document.getElementById("status");
const previewsEl = document.getElementById("previews");
const finalEl = document.getElementById("final");
const modelsGrid = document.getElementById("models-grid");
const shopList = document.getElementById("shop-list");
const profileBox = document.getElementById("profile-box");
const navButtons = Array.from(document.querySelectorAll(".nav-btn"));
const viewIds = ["main", "models", "detail", "shop", "settings", "profile"];

function switchView(view) {
  viewIds.forEach((id) => {
    const el = document.getElementById(`view-${id}`);
    if (!el) return;
    if (id === view) el.classList.remove("hidden");
    else el.classList.add("hidden");
  });
}

function setStatus(msg) {
  statusEl.textContent = msg;
}

function renderImages(container, urls) {
  container.innerHTML = "";
  urls.forEach((url) => {
    const img = document.createElement("img");
    img.src = url;
    img.loading = "lazy";
    img.alt = "ProFace result";
    container.appendChild(img);
  });
}

async function loadModels() {
  const res = await fetch("/api/models?path=styles");
  const json = await res.json();
  const items = json.models || [];
  modelsGrid.innerHTML = "";
  items.forEach((m) => {
    const card = document.createElement("button");
    card.className = "btn-secondary";
    card.textContent = `${m.name} - ${m.cost_credits} XTR`;
    card.addEventListener("click", () => {
      const style = document.getElementById("style");
      if (style) style.value = m.key;
      switchView("detail");
      setStatus(`Model gewählt: ${m.name}`);
    });
    modelsGrid.appendChild(card);
  });
}

async function loadShop() {
  const res = await fetch("/api/shop_packages");
  const json = await res.json();
  const pkgs = json.packages || [];
  shopList.innerHTML = "";
  pkgs.forEach((p) => {
    const div = document.createElement("div");
    div.className = "shop-item";
    div.textContent = `${p.credits} Credits - ${p.price_xtr} XTR`;
    shopList.appendChild(div);
  });
}

async function loadProfile() {
  const res = await fetch("/api/user");
  const json = await res.json();
  profileBox.textContent = JSON.stringify(json, null, 2);
}

navButtons.forEach((btn) => {
  btn.addEventListener("click", async () => {
    const view = btn.dataset.view || "main";
    switchView(view);
    if (view === "models") await loadModels();
    if (view === "shop") await loadShop();
    if (view === "profile") await loadProfile();
  });
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if ((photos.files || []).length !== 5) {
    setStatus("Bitte genau 5 Fotos wählen.");
    return;
  }
  const data = new FormData(form);
  setStatus("Generierung läuft...");
  previewsEl.innerHTML = "";
  finalEl.innerHTML = "";

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      body: data,
    });
    const json = await res.json();
    if (!res.ok || !json.ok) {
      setStatus(`Fehler: ${json.error || "unknown_error"}`);
      return;
    }
    setStatus(`Fertig. Style: ${json.style}`);
    renderImages(previewsEl, json.previews || []);
    renderImages(finalEl, json.final_url ? [json.final_url] : []);
  } catch (err) {
    setStatus(`Netzwerkfehler: ${String(err)}`);
  }
});

switchView("main");
