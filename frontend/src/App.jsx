import { useCallback, useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function boxColor(i) {
  return `hsl(${(i * 53) % 360} 78% 42%)`
}

export default function App() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState('')
  const [imgNatural, setImgNatural] = useState({ w: 0, h: 0 })
  const [conf, setConf] = useState(0.25)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)

  const onFile = useCallback((e) => {
    const f = e.target.files?.[0]
    setError('')
    setData(null)
    setImgNatural({ w: 0, h: 0 })
    if (!f) {
      setFile(null)
      setPreview('')
      return
    }
    setFile(f)
    setPreview(URL.createObjectURL(f))
  }, [])

  const onImgLoad = (e) => {
    const el = e.target
    setImgNatural({ w: el.naturalWidth, h: el.naturalHeight })
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Choose an image first.')
      return
    }
    setLoading(true)
    setError('')
    setData(null)
    const body = new FormData()
    body.append('file', file)
    try {
      const res = await fetch(
        `${API_BASE}/predict?conf=${encodeURIComponent(conf)}`,
        { method: 'POST', body },
      )
      const json = await res.json().catch(() => ({}))
      if (!res.ok) {
        const d = json.detail
        const msg =
          typeof d === 'string'
            ? d
            : Array.isArray(d)
              ? d.map((e) => e.msg ?? JSON.stringify(e)).join('; ')
              : d
                ? JSON.stringify(d)
                : res.statusText
        setError(msg || 'Request failed')
        return
      }
      setData(json)
    } catch (err) {
      setError(err.message || 'Network error — is the API running?')
    } finally {
      setLoading(false)
    }
  }

  const showBoxes =
    preview &&
    imgNatural.w > 0 &&
    data?.detections?.length > 0

  return (
    <div className="app">
      <header className="header">
        <h1>Kitchen ingredients</h1>
        <p className="sub">
          Upload a photo — boxes, labels, and kcal per 100 g
        </p>
      </header>

      <form className="panel" onSubmit={onSubmit}>
        <label className="file-label">
          <span>Image</span>
          <input type="file" accept="image/*" onChange={onFile} />
        </label>

        <label className="conf">
          <span>Confidence threshold</span>
          <input
            type="number"
            min={0}
            max={1}
            step={0.05}
            value={conf}
            onChange={(e) => setConf(Number(e.target.value))}
          />
        </label>

        <button type="submit" disabled={loading || !file}>
          {loading ? 'Running…' : 'Detect'}
        </button>
      </form>

      {preview && (
        <figure className="preview">
          <div className="annotated">
            <img
              src={preview}
              alt="Preview"
              onLoad={onImgLoad}
            />
            {showBoxes && (
              <div className="box-layer" aria-hidden="true">
                {data.detections.map((d, i) => {
                  const { x1, y1, x2, y2 } = d.bbox
                  const nw = imgNatural.w
                  const nh = imgNatural.h
                  return (
                    <div
                      key={i}
                      className="det-box"
                      style={{
                        left: `${(x1 / nw) * 100}%`,
                        top: `${(y1 / nh) * 100}%`,
                        width: `${((x2 - x1) / nw) * 100}%`,
                        height: `${((y2 - y1) / nh) * 100}%`,
                        borderColor: boxColor(i),
                      }}
                    >
                      <span className="det-tag" style={{ background: boxColor(i) }}>
                        <span className="det-label">{d.label}</span>
                        {d.calories_kcal_per_100g != null && (
                          <>
                            {' · '}
                            <span className="det-kcal">
                              {d.calories_kcal_per_100g} kcal/100g
                            </span>
                          </>
                        )}
                        {' · '}
                        <em>{(d.confidence * 100).toFixed(0)}%</em>
                      </span>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </figure>
      )}

      {error && <div className="error">{error}</div>}

      {data?.detections?.length > 0 && (
        <section className="results">
          <h2>Detections ({data.detections.length})</h2>
          <ul>
            {data.detections.map((d, i) => (
              <li key={i} className="card">
                <strong>{d.label}</strong>
                <span className="conf-val">
                  {(d.confidence * 100).toFixed(1)}% conf
                </span>
                {d.calories_kcal_per_100g != null && (
                  <span className="kcal">
                    {d.calories_kcal_per_100g} kcal / 100 g
                  </span>
                )}
                <code className="bbox">
                  box {Math.round(d.bbox.x1)},{Math.round(d.bbox.y1)} →{' '}
                  {Math.round(d.bbox.x2)},{Math.round(d.bbox.y2)}
                </code>
              </li>
            ))}
          </ul>
        </section>
      )}

      {data && data.detections?.length === 0 && !error && (
        <p className="empty">No objects detected (try lowering confidence).</p>
      )}

      <footer className="foot">
        API: <code>{API_BASE}</code> · Start with{' '}
        <code>python serve.py</code>
      </footer>
    </div>
  )
}
