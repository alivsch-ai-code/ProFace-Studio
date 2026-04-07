import React, { useEffect, useState } from 'react';
import { generateWithFiles, loadModelDetail } from '../apiClient';

function renderImages(urls) {
  return (urls || []).map((u) => <img key={u} src={u} alt="result" className="result-img" />);
}

export default function ModelDetailView({ modelKey, t, onBackToModels }) {
  const [style, setStyle] = useState(modelKey || 'linkedin');
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState('Bereit');
  const [previews, setPreviews] = useState([]);
  const [finalUrl, setFinalUrl] = useState('');
  const [model, setModel] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      try {
        const data = await loadModelDetail(modelKey || 'linkedin');
        if (!cancelled && data?.ok) setModel(data);
      } catch {}
    }
    run();
    return () => {
      cancelled = true;
    };
  }, [modelKey]);

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
      <div className="back-btn" onClick={() => onBackToModels && onBackToModels()} role="button" tabIndex={0}>
        ← {t ? t('webapp_back', 'Zurück') : 'Zurück'}
      </div>
      <div className="header"><h1>🤖 {model?.name || 'Model Detail'}</h1></div>
      <div className="detail-desc">{model?.description || 'ProFace pipeline with 5 user photos.'}</div>
      <form className="gen-options" onSubmit={submit}>
        <label>{t ? t('webapp_prompt', 'Style') : 'Style'}</label>
        <select value={style} onChange={(e) => setStyle(e.target.value)}>
          <option value="linkedin">LinkedIn</option>
          <option value="creative">Creative</option>
        </select>
        <label>{t ? t('webapp_reference_images', 'Fotos') : 'Fotos'} (genau 5)</label>
        <input type="file" multiple accept="image/*" onChange={(e) => setFiles(Array.from(e.target.files || []))} />
        <button type="submit" className="btn-start">🚀 {t ? t('webapp_start', 'Start') : 'Start'} (49 ⭐)</button>
      </form>
      <div className="section"><pre>{status}</pre></div>
      <div className="section webapp-result-media-grid">{renderImages(previews)}</div>
      <div className="section webapp-result-media-grid">{finalUrl ? <img src={finalUrl} alt="final" className="webapp-result-media" /> : null}</div>
    </div>
  );
}
