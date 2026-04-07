import React, { useEffect, useState } from 'react';
import { loadShopPackages } from '../apiClient';

export default function ShopView({ t, userCredits, onBack, onBuy }) {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      try {
        setLoading(true);
        const data = await loadShopPackages();
        if (cancelled) return;
        setPackages(data?.packages || []);
      } catch {
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    run();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div>
      <div className="back-btn" onClick={onBack} role="button" tabIndex={0}>
        ← {t ? t('webapp_back', 'Zurück') : 'Zurück'}
      </div>
      <div className="header">
        <h1>{t ? t('webapp_shop_title', '💳 Buy Credits') : '💳 Buy Credits'}</h1>
        <p style={{ marginTop: 10, color: 'var(--tg-theme-text-color)', opacity: 0.9 }}>
          {(t ? t('webapp_credits_remaining', 'Credits') : 'Credits')}: {userCredits || 0} ⭐
        </p>
      </div>
      <div className="section">
        {loading ? (
          <div className="loading">Laden...</div>
        ) : (
          <div>
            {(packages || []).map((p, i) => (
              <div key={i} className="model-card" style={{ cursor: 'pointer' }} onClick={() => onBuy && onBuy(p.credits, p.price_xtr || p.price)}>
                <div className="model-left">
                  <div className="model-logo-fallback" style={{ fontSize: 18 }}>💎</div>
                  <span className="model-name">{p.desc || `${p.credits} Credits`}</span>
                </div>
                <span className="model-cost">{p.price_xtr || p.price} ⭐</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
