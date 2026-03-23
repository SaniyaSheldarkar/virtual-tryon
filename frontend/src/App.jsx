/**
 * App — Virtual Try-On Studio
 * ============================
 * Orchestrates image uploads, calls the FastAPI backend,
 * and renders the resulting try-on image.
 */
import React, { useState, useCallback } from 'react'
import ImageUploadZone from './components/ImageUploadZone'
import ResultPanel from './components/ResultPanel'

const API_URL = 'http://localhost:8000'

export default function App() {
  // ── State ──────────────────────────────────────────────────────
  const [personFile,   setPersonFile]   = useState(null)
  const [clothFile,    setClothFile]    = useState(null)
  const [personPreview, setPersonPreview] = useState(null)
  const [clothPreview,  setClothPreview]  = useState(null)
  const [result,   setResult]   = useState(null)   // { base64, mime, mode }
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState('')

  // ── Handlers ───────────────────────────────────────────────────
  function pickFile(file, setFile, setPreview) {
    setFile(file)
    setPreview(URL.createObjectURL(file))
    setResult(null)
    setError('')
  }

  const handlePersonChange = useCallback((file) =>
    pickFile(file, setPersonFile, setPersonPreview), [])

  const handleClothChange = useCallback((file) =>
    pickFile(file, setClothFile, setClothPreview), [])

  async function handleTryOn() {
    // Validate both images are selected
    if (!personFile || !clothFile) {
      setError('Please upload both a person image and a clothing image before continuing.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      // Build multipart/form-data payload
      const form = new FormData()
      form.append('person_image', personFile)
      form.append('cloth_image',  clothFile)

      const res = await fetch(`${API_URL}/tryon`, {
        method: 'POST',
        body: form,
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `Server error: ${res.status}`)
      }

      const data = await res.json()
      setResult({ base64: data.result_image, mime: data.mime, mode: data.mode })
    } catch (err) {
      setError(err.message || 'Something went wrong. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  // ── Render ─────────────────────────────────────────────────────
  return (
    <div className="app-shell">
      {/* ── Header ── */}
      <header className="site-header">
        <h1>Virtual <em>Try-On</em> Studio</h1>
        <p>Upload · Generate · Visualise</p>
      </header>

      {/* ── Main ── */}
      <main className="main-content">

        {/* Upload panels */}
        <div className="upload-grid">
          <ImageUploadZone
            label="Person"
            preview={personPreview}
            onChange={handlePersonChange}
          />
          <ImageUploadZone
            label="Clothing"
            preview={clothPreview}
            onChange={handleClothChange}
          />
        </div>

        {/* Error message */}
        {error && <div className="error-msg">⚠ {error}</div>}

        {/* CTA */}
        <div className="cta-row">
          <button
            className="btn-tryon"
            onClick={handleTryOn}
            disabled={loading}
          >
            {loading ? 'Processing…' : 'Try On'}
          </button>
        </div>

        {/* Loading indicator */}
        {loading && (
          <div className="loading-block">
            <div className="spinner" />
            <p>Generating your look…</p>
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <ResultPanel
            base64={result.base64}
            mime={result.mime}
            mode={result.mode}
          />
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="site-footer">
        Virtual Try-On Studio &nbsp;·&nbsp; Powered by FastAPI &amp; React
      </footer>
    </div>
  )
}
