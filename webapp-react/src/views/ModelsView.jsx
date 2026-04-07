import React from 'react';

export default function ModelsView({ title, folders, models, favoritesModels, freeLabel, loading, onBack, onSelectFolder, onSelectModel, t }) {
  const regularModels = models || [];
  const favorites = favoritesModels || [];
  const activateOnKey = (e, fn) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fn && fn();
    }
  };
  return (
    <div>
      <div className="back-btn" onClick={onBack} onKeyDown={(e) => activateOnKey(e, onBack)} role="button" tabIndex={0}>
        ← <span>{t ? t('webapp_back', 'Zurück') : 'Zurück'}</span>
      </div>
      <div className="header">
        <h1>{title || 'Modelle'}</h1>
      </div>

      {loading ? <div className="loading">Laden...</div> : null}

      {(folders || []).length ? (
        <div className="folder-grid">
          {(folders || []).map((f) => {
            const fp = f.path || f.slug;
            const label = String(f.title || f.slug || fp || '').replace(/_/g, ' ');
            return (
              <div key={'folder-' + fp} className="folder-tile" onClick={() => onSelectFolder(fp)} onKeyDown={(e) => activateOnKey(e, () => onSelectFolder(fp))} role="button" tabIndex={0}>
                <div className="folder-logo-fallback">📁</div>
                <div className="folder-title">{label}</div>
              </div>
            );
          })}
        </div>
      ) : null}

      {(favorites || []).map((m) => (
        <div key={'fav-' + m.key} className="model-card" onClick={() => onSelectModel(m.key)} onKeyDown={(e) => activateOnKey(e, () => onSelectModel(m.key))} role="button" tabIndex={0}>
          <div className="model-left">
            <div className="model-logo-fallback">⭐</div>
            <span className="model-name">{m.name}</span>
          </div>
          <span className="model-cost">{(m.cost_credits ?? 0) <= 0 ? (freeLabel || 'FREE') : `${m.cost_credits} ⭐`}</span>
        </div>
      ))}

      {regularModels.map((m) => (
        <div key={m.key} className="model-card" onClick={() => onSelectModel(m.key)} onKeyDown={(e) => activateOnKey(e, () => onSelectModel(m.key))} role="button" tabIndex={0}>
          <div className="model-left">
            <div className="model-logo-fallback">✨</div>
            <span className="model-name">{m.name}</span>
          </div>
          <span className="model-cost">{(m.cost_credits ?? 0) <= 0 ? (freeLabel || 'FREE') : `${m.cost_credits} ⭐`}</span>
        </div>
      ))}
    </div>
  );
}
