export default function MainView({ onNavigateModels }) {
  return (
    <div>
      <div className="header">
        <h1>ProFace AI Hub</h1>
        <p>Waehle eine Kategorie</p>
      </div>
      <div className="grid">
        <button className="card" onClick={() => onNavigateModels('styles')}>Styles</button>
        <button className="card" onClick={() => onNavigateModels('styles')}>Business Portrait</button>
      </div>
    </div>
  );
}
