/**
 * ResultPanel
 * -----------
 * Displays the generated try-on image with a download button.
 * Props:
 *   base64  – base64-encoded image string
 *   mime    – MIME type string (default "image/jpeg")
 *   mode    – "mock" | "gemini" (shown as a badge)
 */
import React from 'react'

export default function ResultPanel({ base64, mime = 'image/jpeg', mode }) {
  const src = `data:${mime};base64,${base64}`

  function handleDownload() {
    const a = document.createElement('a')
    a.href = src
    a.download = 'virtual-tryon-result.jpg'
    a.click()
  }

  return (
    <div className="result-block">
      <div className="divider"><span>Result</span></div>
      <div className="result-card">
        <img src={src} alt="Virtual try-on result" />
        <div className="result-footer">
          <span>
            {mode === 'mock' ? '⚡ Mock render' : '✦ AI generated'} · ready to save
          </span>
          <button className="btn-download" onClick={handleDownload}>
            Download
          </button>
        </div>
      </div>
    </div>
  )
}
