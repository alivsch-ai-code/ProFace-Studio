const form = document.getElementById("gen-form");
const photos = document.getElementById("photos");
const statusEl = document.getElementById("status");
const previewsEl = document.getElementById("previews");
const finalEl = document.getElementById("final");

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
