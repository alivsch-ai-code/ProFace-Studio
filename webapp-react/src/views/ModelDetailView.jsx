import { useState } from 'react';
import { generateWithFiles } from '../apiClient';

function renderImages(urls) {
  return (urls || []).map((u) => <img key={u} src={u} alt="result" className="result-img" />);
}

export default function ModelDetailView({ modelKey, onBack }) {
  const [style, setStyle] = useState(modelKey || 'linkedin');
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState('Bereit');
  const [previews, setPreviews] = useState([]);
  const [finalUrl, setFinalUrl] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    if ((files || []).length !== 5) {
      setStatus('Bitte genau 5 Fotos hochladen.');
      return;
    }
    setStatus('Generierung laeuft...');
    const res = await generateWithFiles(style, files);
    if (!res.ok || !res.data?.ok) {
      setStatus('Fehler: ' + (res.data?.error || 'unknown'));
      return;
    }
    setStatus('Fertig');
    setPreviews(res.data.previews || []);
    setFinalUrl(res.data.final_url || '');
  };

  return (
    <div>
      <div className="back-btn" onClick={onBack}>← Zurueck</div>
      <div className="header"><h1>Model Detail</h1></div>
      <form className="section" onSubmit={submit}>
        <label>Style</label>
        <select value={style} onChange={(e) => setStyle(e.target.value)}>
          <option value="linkedin">LinkedIn</option>
          <option value="creative">Creative</option>
        </select>
        <label>Fotos (genau 5)</label>
        <input type="file" multiple accept="image/*" onChange={(e) => setFiles(Array.from(e.target.files || []))} />
        <button type="submit" className="btn-primary">Generieren</button>
      </form>
      <div className="section"><pre>{status}</pre></div>
      <div className="section grid">{renderImages(previews)}</div>
      <div className="section grid">{finalUrl ? <img src={finalUrl} alt="final" className="result-img" /> : null}</div>
    </div>
  );
}
