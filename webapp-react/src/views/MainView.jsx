import React from 'react';

function Card({ icon, label, desc, tone = 'default', onClick }) {
  const onKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick && onClick();
    }
  };
  return (
    <div className={`card card-tone-${tone}`} onClick={onClick} onKeyDown={onKeyDown} role="button" tabIndex={0}>
      <div className="card-animated-bg" aria-hidden="true" />
      <div className="card-icon">{icon}</div>
      <div className="card-label">{label}</div>
      <div className="card-desc">{desc}</div>
    </div>
  );
}

function HeroVisual() {
  return (
    <div className="hero-visual" aria-hidden="true">
      <div className="hero-orb hero-orb-a" />
      <div className="hero-orb hero-orb-b" />
      <div className="hero-ring hero-ring-a" />
      <div className="hero-ring hero-ring-b" />
      <div className="hero-grid-glow" />
    </div>
  );
}

export default function MainView({ t, azamatVersion, onNavigateModels }) {
  return (
    <div>
      <div className="header">
        <HeroVisual />
        <h1>
          🤖 <span>{t('webapp_title', 'ProFace AI Hub')}</span>
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '8px' }}>
          {t('webapp_choose_category', 'Wähle eine Kategorie')}
        </p>
        <div className="hero-chip-row">
          <span className="hero-chip">⚡ Fast Pipeline</span>
          <span className="hero-chip">🧠 ProFace Portraits</span>
          <span className="hero-chip">🛡️ Safe by Design</span>
        </div>
        <div className="azamat-version-badge">PROFACE v{azamatVersion || '0.1.0'}</div>
      </div>

      <div className="section">
        <div className="section-title">{t('webapp_categories', 'Kategorien')}</div>
        <div className="grid">
          <Card icon="🧑‍💼" tone="image" label={t('menu_image', 'Business Portraits')} desc={t('webapp_desc_image', 'LinkedIn & Creative Studio')} onClick={() => onNavigateModels('styles')} />
          <Card icon="✨" tone="tools" label={t('menu_tools', 'ProFace Workflow')} desc={t('webapp_desc_tools', 'Upload 5 Fotos → Preview → Final')} onClick={() => onNavigateModels('styles')} />
        </div>
      </div>
    </div>
  );
}
