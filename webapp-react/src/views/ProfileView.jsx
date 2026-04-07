export default function ProfileView({ user, onBack }) {
  return (
    <div>
      <div className="back-btn" onClick={onBack}>← Zurueck</div>
      <div className="header"><h1>Profil</h1></div>
      <div className="section">
        <p>User: {user?.username || 'user'}</p>
        <p>Credits: {user?.credits || 0}</p>
      </div>
    </div>
  );
}
