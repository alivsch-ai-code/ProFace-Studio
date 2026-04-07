export function getApiBase() {
  return window.location.origin;
}

async function getJSON(path) {
  const res = await fetch(getApiBase() + path);
  return res.json();
}

export async function loadUserInfo() {
  return getJSON('/api/user');
}
export async function loadStrings(lang) {
  return getJSON('/api/strings?lang=' + encodeURIComponent(lang || 'de'));
}
export async function loadVersion() {
  return getJSON('/api/version');
}
export async function loadModels(path) {
  return getJSON('/api/models?path=' + encodeURIComponent(path || 'root'));
}
export async function loadModelDetail(key) {
  return getJSON('/api/model_detail?key=' + encodeURIComponent(key));
}
export async function loadShopPackages() {
  return getJSON('/api/shop_packages');
}

export async function sendWebappAction(action, payload = {}) {
  const res = await fetch(getApiBase() + '/api/action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, ...payload }),
  });
  return res.json();
}

export async function generateWithFiles(style, files) {
  const fd = new FormData();
  fd.append('style', style);
  for (const f of files || []) fd.append('photos', f);
  const res = await fetch(getApiBase() + '/api/generate', { method: 'POST', body: fd });
  return { ok: res.ok, data: await res.json() };
}
