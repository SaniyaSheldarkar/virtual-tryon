/**
 * ImageUploadZone
 * ---------------
 * A styled file-input that shows a preview once an image is chosen.
 * Props:
 *   label      – e.g. "Person" or "Clothing"
 *   preview    – data URL of the chosen image (or null)
 *   onChange   – called with the File object when user picks a file
 */
import React, { useRef } from 'react'

export default function ImageUploadZone({ label, preview, onChange }) {
  const inputRef = useRef(null)

  function handleChange(e) {
    const file = e.target.files[0]
    if (file) onChange(file)
  }

  return (
    <div className={`upload-zone ${preview ? 'has-image' : ''}`}>
      {/* invisible file input overlaid on the whole card */}
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleChange}
      />

      {preview ? (
        <div className="upload-preview">
          <img src={preview} alt={`${label} preview`} />
          <div className="change-badge">click to change</div>
        </div>
      ) : (
        <div className="upload-placeholder">
          <div className="icon">▲</div>
          <div className="label">{label}</div>
          <div className="hint">Click to upload<br />JPEG · PNG · WEBP</div>
        </div>
      )}

      <div className="zone-label">
        <div className="dot" />
        <span>{label} Image</span>
      </div>
    </div>
  )
}
