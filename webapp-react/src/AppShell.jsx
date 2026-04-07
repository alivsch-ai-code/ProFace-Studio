import { useEffect, useState } from 'react';
import { initTelegram } from './telegram';
import { loadModels, loadShopPackages, loadUserInfo, loadVersion } from './apiClient';
import MainView from './views/MainView.jsx';
import ModelsView from './views/ModelsView.jsx';
import ModelDetailView from './views/ModelDetailView.jsx';
import ShopView from './views/ShopView.jsx';
import SettingsView from './views/SettingsView.jsx';
import ProfileView from './views/ProfileView.jsx';

export default function AppShell() {
  const [view, setView] = useState('main');
  const [models, setModels] = useState([]);
  const [modelKey, setModelKey] = useState('linkedin');
  const [packages, setPackages] = useState([]);
  const [user, setUser] = useState({ username: 'User', credits: 0 });
  const [version, setVersion] = useState('0.1.0');

  useEffect(() => {
    initTelegram();
    loadUserInfo().then(setUser).catch(() => {});
    loadVersion().then((v) => setVersion(String(v.version || '0.1.0'))).catch(() => {});
  }, []);

  async function openModels(path) {
    const data = await loadModels(path);
    setModels(data.models || []);
    setView('models');
  }

  async function openShop() {
    const data = await loadShopPackages();
    setPackages(data.packages || []);
    setView('shop');
  }

  return (
    <div className="app">
      <div className="top-bar">
        <span className="user">User: {user.username}</span>
        <div className="top-actions">
          <button className="top-icon-btn" onClick={openShop}>💎 <b>{user.credits}</b></button>
          <button className="top-icon-btn" onClick={() => setView('settings')}>⚙️</button>
          <button className="top-icon-btn" onClick={() => setView('profile')}>👤</button>
        </div>
      </div>
      <div className="azamat-version-badge">PROFACE v{version}</div>

      {view === 'main' && <MainView onNavigateModels={openModels} />}
      {view === 'models' && <ModelsView models={models} onBack={() => setView('main')} onSelectModel={(k) => { setModelKey(k); setView('detail'); }} />}
      {view === 'detail' && <ModelDetailView modelKey={modelKey} onBack={() => setView('models')} />}
      {view === 'shop' && <ShopView packages={packages} onBack={() => setView('main')} />}
      {view === 'settings' && <SettingsView onBack={() => setView('main')} />}
      {view === 'profile' && <ProfileView user={user} onBack={() => setView('main')} />}
    </div>
  );
}
