import React, { useEffect, useMemo, useState } from 'react';
import { initTelegram, getTelegramWebApp } from './telegram';
import { loadLegal, loadModels, loadModelDetail, loadShopPackages, loadStrings, loadUserInfo, loadVersion, sendWebappAction } from './apiClient';
import MainView from './views/MainView.jsx';
import ModelsView from './views/ModelsView.jsx';
import SettingsView from './views/SettingsView.jsx';
import ShopView from './views/ShopView.jsx';
import ProfileView from './views/ProfileView.jsx';
import ModelDetailView from './views/ModelDetailView.jsx';
import LegalDocsView from './views/LegalDocsView.jsx';

function showToastError(msg) {
  const el = document.createElement('div');
  el.style.cssText = 'position:fixed;bottom:20px;left:16px;right:16px;padding:12px;background:#c33;color:#fff;border-radius:8px;text-align:center;z-index:9999;';
  el.textContent = '⚠️ ' + (msg || 'Fehler');
  document.body.appendChild(el);
  setTimeout(() => {
    try {
      el.remove();
    } catch {}
  }, 3500);
}

export default function AppShell() {
  const apiBase = useMemo(() => window.location.origin, []);
  const [user, setUser] = useState({ user_id: null, username: 'User', credits: 0, lang: 'de', auto_opt: true, daily_msg: false, bot_username: '' });
  const [strings, setStrings] = useState({});
  const [view, setView] = useState('main');
  const [currentPath, setCurrentPath] = useState('root');
  const [modelKey, setModelKey] = useState('');
  const [azamatVersion, setAzamatVersion] = useState('0.1.0');
  const [modelsData, setModelsData] = useState({ title: '', folders: [], models: [], favorites_models: [] });
  const [loading, setLoading] = useState(false);
  const [legalCache, setLegalCache] = useState(null);
  const [legalDoc, setLegalDoc] = useState(null);

  const t = (key, fallback) => strings?.[key] || fallback || key;

  async function openLegal(doc) {
    try {
      setLoading(true);
      let bundle = legalCache;
      if (!bundle || bundle.lang !== (user.lang || 'de')) {
        const data = await loadLegal(user.lang || 'de');
        bundle = { lang: user.lang || 'de', privacy: data.privacy, impressum: data.impressum, labels: data.labels || {} };
        setLegalCache(bundle);
      }
      setLegalDoc(doc);
      setView('legal');
    } catch {
      showToastError('Rechtstexte konnten nicht geladen werden');
    } finally {
      setLoading(false);
    }
  }

  async function fetchModelsForPath(path) {
    setLoading(true);
    try {
      const data = await loadModels(path || 'root', user.lang);
      setModelsData({
        title: data?.title || path || '',
        folders: data?.folders || [],
        models: data?.models || [],
        favorites_models: data?.favorites_models || [],
      });
      setCurrentPath(path || 'root');
      setView('models');
    } catch {
      showToastError('Laden fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    initTelegram();
    const params = new URLSearchParams(window.location.search);
    const pathParam = params.get('path');
    const modelParam = params.get('model');
    if (modelParam) {
      setModelKey(modelParam);
      setView('detail');
    } else if (pathParam && pathParam !== 'root') {
      setCurrentPath(pathParam);
      setView('models');
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function boot() {
      try {
        const tg = getTelegramWebApp();
        if (!tg?.initData) return;
        const userInfo = await loadUserInfo();
        if (cancelled) return;
        setUser((u) => ({ ...u, ...userInfo }));
        const st = await loadStrings(userInfo.lang || 'de');
        if (!cancelled) setStrings(st || {});
      } catch {}
      try {
        const v = await loadVersion();
        if (!cancelled && v?.version) setAzamatVersion(String(v.version));
      } catch {}
    }
    boot();
    return () => {
      cancelled = true;
    };
  }, []);

  const freeLabel = t('webapp_free', 'FREE');

  return (
    <div className="app">
      <div className="top-bar" style={{ display: 'flex' }}>
        <span className="user" style={{ opacity: 0.92 }}>
          {(t('webapp_user', 'User') || 'User') + ': ' + (user.username || 'User')}
        </span>
        <div className="top-actions">
          <button type="button" className="top-icon-btn top-icon-shop" onClick={() => setView('shop')} title={t('webapp_credits_buy', 'Credits kaufen')} aria-label={t('webapp_credits_buy', 'Credits kaufen')}>
            <span aria-hidden="true">💎</span>
            <b>{user.credits || 0}</b>
          </button>
          <button type="button" className="top-icon-btn top-icon-settings" onClick={() => setView('settings')} title={t('webapp_settings', 'Einstellungen')} aria-label={t('webapp_settings', 'Einstellungen')}>
            <span aria-hidden="true">⚙️</span>
          </button>
          <button type="button" className="top-icon-btn top-icon-profile" onClick={() => setView('profile')} title={t('menu_profile', 'Profil')} aria-label={t('menu_profile', 'Profil')}>
            <span aria-hidden="true">👤</span>
          </button>
        </div>
      </div>

      {view === 'main' ? <MainView t={t} azamatVersion={azamatVersion} onNavigateModels={(path) => fetchModelsForPath(path)} onOpenShop={() => setView('shop')} onOpenSettings={() => setView('settings')} onOpenProfile={() => setView('profile')} /> : null}

      {view === 'models' ? (
        <ModelsView
          title={modelsData.title}
          folders={modelsData.folders}
          models={modelsData.models}
          favoritesModels={modelsData.favorites_models || []}
          t={t}
          freeLabel={freeLabel}
          loading={loading}
          currentPath={currentPath}
          onBack={() => setView('main')}
          onSelectFolder={(fp) => fetchModelsForPath(fp)}
          onSelectModel={(key) => {
            setModelKey(key);
            setView('detail');
          }}
        />
      ) : null}

      {view === 'settings' ? (
        <SettingsView
          lang={user.lang}
          auto_opt={user.auto_opt}
          daily_msg={user.daily_msg}
          t={t}
          onBack={() => setView('main')}
          onSetLang={async (lang) => {
            await sendWebappAction('set_lang_' + lang);
            setUser((u) => ({ ...u, lang }));
          }}
          onToggleOpt={async () => {
            await sendWebappAction('toggle_opt');
            setUser((u) => ({ ...u, auto_opt: !u.auto_opt }));
          }}
          onToggleDaily={async () => {
            await sendWebappAction('toggle_daily');
            setUser((u) => ({ ...u, daily_msg: !u.daily_msg }));
          }}
          onOpenPrivacy={() => openLegal('privacy')}
          onOpenImpressum={() => openLegal('impressum')}
        />
      ) : null}

      {view === 'legal' && legalCache && legalDoc ? <LegalDocsView doc={legalDoc} labels={legalCache.labels} privacyText={legalCache.privacy} impressumText={legalCache.impressum} onBack={() => setView('settings')} /> : null}

      {view === 'shop' ? <ShopView t={t} userCredits={user.credits} onBack={() => setView('main')} onBuy={(credits, price) => sendWebappAction('buy_credits_' + credits + '_' + price)} /> : null}
      {view === 'profile' ? <ProfileView t={t} user={user} onBack={() => setView('main')} /> : null}
      {view === 'detail' ? <ModelDetailView modelKey={modelKey} t={t} user={user} onUpdateCredits={(credits) => setUser((u) => ({ ...u, credits }))} onBackToModels={() => setView('models')} /> : null}

      {loading && view !== 'detail' ? <div className="loading">Laden...</div> : null}
      <div style={{ display: 'none' }}>{apiBase}</div>
    </div>
  );
}
