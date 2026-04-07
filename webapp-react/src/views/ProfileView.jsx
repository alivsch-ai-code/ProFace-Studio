import React from 'react';

export default function ProfileView({ t, user, onBack }) {
  const bot = user?.bot_username || 'proface_bot';
  const refLink = 'https://t.me/' + bot + '?start=' + (user?.user_id || '');
  return (
    <div>
      <div className="back-btn" onClick={onBack} role="button" tabIndex={0}>
        ← {t ? t('webapp_back', 'Zurück') : 'Zurück'}
      </div>
      <div className="header"><h1>👤 Profil</h1></div>
      <div className="section">
        <div className="gen-options">
          <p style={{ lineHeight: 1.6, color: 'var(--tg-theme-text-color)' }}>
            <b>{t ? t('webapp_user', 'User') : 'User'}:</b> {user?.username || 'User'}
          </p>
          <p style={{ lineHeight: 1.6, color: 'var(--tg-theme-text-color)' }}>
            <b>{t ? t('webapp_credits_remaining', 'Credits') : 'Credits'}:</b> {user?.credits || 0} ⭐
          </p>
          <p style={{ lineHeight: 1.6, color: 'var(--tg-theme-text-color)' }}>
            <b>Invite:</b> <span style={{ wordBreak: 'break-all', color: 'var(--accent)' }}>{refLink}</span>
          </p>
        </div>
      </div>
    </div>
  );
}
