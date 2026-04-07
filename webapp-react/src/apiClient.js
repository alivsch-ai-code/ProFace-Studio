import { getInitData, getTelegramWebApp } from './telegram';

export function getApiBase() {
  return window.location.origin;
}

export async function postJSON(path, body) {
  return fetch(getApiBase() + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body ?? {}),
  });
}

export async function getJSON(path) {
  return fetch(getApiBase() + path);
}

export async function loadUserInfo() {
  const res = await postJSON('/api/user_info', { init_data: getInitData() || '' });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || !data?.ok) throw new Error(data?.error || 'user_info_failed');
  return data;
}

export async function loadStrings(lang) {
  const res = await getJSON('/api/strings?lang=' + encodeURIComponent(lang || 'de'));
  return res.json();
}

export async function loadVersion() {
  const res = await getJSON('/api/version');
  return res.json();
}

export async function loadLegal(lang) {
  const res = await getJSON('/api/legal?lang=' + encodeURIComponent(lang || 'de'));
  const data = await res.json().catch(() => ({}));
  if (!res.ok || !data?.ok) throw new Error(data?.error || 'legal_failed');
  return data;
}

export async function loadModels(path, lang) {
  const qs = new URLSearchParams();
  if (path) qs.set('path', path);
  if (lang) qs.set('lang', lang);
  const res = await getJSON('/api/models?' + qs.toString());
  return res.json();
}

export async function loadModelDetail(key) {
  const res = await getJSON('/api/model_detail?key=' + encodeURIComponent(key));
  const data = await res.json().catch(() => ({}));
  if (!res.ok) return { ok: false, error: data?.error || 'model_detail_failed', status: res.status };
  return data;
}

export async function loadShopPackages() {
  const res = await getJSON('/api/shop_packages');
  return res.json();
}

export async function sendWebappAction(action, payload = {}) {
  const tg = getTelegramWebApp();
  const res = await postJSON('/api/action', { action, ...payload, init_data: getInitData() || '' });
  const data = await res.json().catch(() => ({}));
  if (data?.ok && tg?.close && !String(action).startsWith('set_lang_')) {
    // keep same UX semantics as AZAMAT for most actions
    // but don't force close on settings toggles
  }
  return data;
}

export async function generateWithFiles(style, files) {
  const fd = new FormData();
  fd.append('style', style);
  for (const f of files || []) fd.append('photos', f);
  const res = await fetch(getApiBase() + '/api/generate', { method: 'POST', body: fd });
  return { ok: res.ok, data: await res.json().catch(() => ({})) };
}
