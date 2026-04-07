export default function SettingsView({ onBack }) {
  return (
    <div>
      <div className="back-btn" onClick={onBack}>← Zurueck</div>
      <div className="header"><h1>Einstellungen</h1></div>
      <div className="section">Sprache, Prompt-Magic, Daily-News Optionen.</div>
    </div>
  );
}
