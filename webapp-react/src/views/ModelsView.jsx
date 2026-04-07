export default function ModelsView({ models, onBack, onSelectModel }) {
  return (
    <div>
      <div className="back-btn" onClick={onBack}>← Zurueck</div>
      <div className="header"><h1>Models</h1></div>
      {(models || []).map((m) => (
        <div className="model-card" key={m.key} onClick={() => onSelectModel(m.key)}>
          <span>{m.name}</span>
          <b>{m.cost_credits} XTR</b>
        </div>
      ))}
    </div>
  );
}
