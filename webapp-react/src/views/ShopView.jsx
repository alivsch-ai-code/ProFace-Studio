export default function ShopView({ packages, onBack }) {
  return (
    <div>
      <div className="back-btn" onClick={onBack}>← Zurueck</div>
      <div className="header"><h1>Shop</h1></div>
      <div className="section">
        {(packages || []).map((p, i) => (
          <div key={i} className="model-card">{p.credits} Credits - {p.price_xtr} XTR</div>
        ))}
      </div>
    </div>
  );
}
