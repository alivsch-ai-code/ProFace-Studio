export function getTelegramWebApp() {
  try {
    return window.Telegram?.WebApp || null;
  } catch {
    return null;
  }
}

export function initTelegram() {
  const tg = getTelegramWebApp();
  if (!tg) return;
  tg.ready();
  tg.expand();
}
