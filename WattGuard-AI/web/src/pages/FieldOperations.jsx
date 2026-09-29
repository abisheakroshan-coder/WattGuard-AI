import React, { useState } from 'react';
import {
  Wrench,
  Camera,
  CheckCircle2,
  Upload,
  AlertCircle,
  FileText,
  Shield,
  MapPin,
} from 'lucide-react';
import { api } from '../services/api';

const DEFAULT_CONSUMERS = [
  'CONS_COM_001',
  'CONS_COM_002',
  'CONS_COM_003',
  'CONS_COM_004',
  'CONS_COM_005',
  'CONS_COM_006',
  'CONS_COM_007',
  'CONS_COM_008',
  'CONS_COM_009',
  'CONS_COM_010',
  'CONS_COM_014',
  'CONS_RES_006',
  'CONS_RES_007',
  'CONS_RES_008',
  'CONS_RES_011',
  'CONS_RES_012',
];

const AUDIT_STATUSES = [
  { value: 'CONFIRMED_THEFT_BYPASS', label: 'CONFIRMED THEFT BYPASS (Physical Wire Tap / Shunt)' },
  { value: 'METER_FAULT', label: 'METER FAULT (Hardware Failure / Drift)' },
  { value: 'GENUINE_USAGE_CHANGE', label: 'GENUINE USAGE CHANGE (Commercial Operations Reduced)' },
  { value: 'PREMISES_VACANT', label: 'PREMISES VACANT (Tenancy Vacated)' },
  { value: 'REINSPECTION_REQUIRED', label: 'REINSPECTION REQUIRED (Access Denied / Obstruction)' },
];

export default function FieldOperations({ initialConsumerId }) {
  const [consumerId, setConsumerId] = useState(initialConsumerId || 'CONS_COM_001');
  const [inspectorId, setInspectorId] = useState('INSP-ALPHA-42');
  const [auditStatus, setAuditStatus] = useState('CONFIRMED_THEFT_BYPASS');
  const [meterSerial, setMeterSerial] = useState('SM-99482-TX');
  const [sealNumber, setSealNumber] = useState('SEAL-A8472');
  const [observedLoad, setObservedLoad] = useState('18.5');
  const [notes, setNotes] = useState('Physical secondary shunt wire discovered bypassing phase CT in terminal box.');
  const [submitting, setSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState(null);
  const [submitError, setSubmitError] = useState('');

  // Evidence upload
  const [inspectionIdForUpload, setInspectionIdForUpload] = useState('');
  const [photoType, setPhotoType] = useState('BYPASS_TAP_PANEL');
  const [latitude, setLatitude] = useState(28.625);
  const [longitude, setLongitude] = useState(77.224);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState('');

  const handleSubmitAudit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError('');
    setSubmitResult(null);

    try {
      const payload = {
        consumer_id: consumerId,
        inspector_id: inspectorId,
        audit_status: auditStatus,
        meter_serial: meterSerial,
        seal_number: sealNumber,
        observed_load: parseFloat(observedLoad) || 0.0,
        inspector_notes: notes,
      };

      const res = await api.submitInspection(payload);
      setSubmitResult(res);
      setInspectionIdForUpload(res.inspection_id);
    } catch (err) {
      setSubmitError(err.message || 'Failed to submit inspection.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUploadPhoto = async (e) => {
    e.preventDefault();
    if (!inspectionIdForUpload) {
      setUploadError('Please provide an Inspection ID.');
      return;
    }
    if (!selectedFile) {
      setUploadError('Please select a photo file (JPEG/PNG).');
      return;
    }

    setUploading(true);
    setUploadError('');
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('photo_type', photoType);
      if (latitude) formData.append('latitude', latitude);
      if (longitude) formData.append('longitude', longitude);

      const res = await api.uploadEvidence(inspectionIdForUpload, formData);
      setUploadResult(res);
    } catch (err) {
      setUploadError(err.message || 'Failed to upload evidence photo.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Page Header Banner */}
      <div
        className="control-panel"
        style={{
          padding: '12px 18px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Wrench size={18} style={{ color: 'var(--cyan-telemetry)' }} />
          <div>
            <div
              style={{
                fontSize: '0.8125rem',
                fontWeight: 800,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                color: 'var(--text-bright)',
              }}
            >
              Field Inspection Audit Recording & Evidentiary Ingestion
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
              Standardized ground-truth audit logging feeding closed-loop active learning retrainers
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 16 }}>
        {/* Form 1: Inspection Audit Outcome Submission */}
        <div className="control-panel">
          <div className="panel-header">
            <div className="panel-title">
              <FileText size={14} style={{ color: 'var(--cyan-telemetry)' }} />
              <span>Submit Structured Inspection Result</span>
            </div>
          </div>

          <form onSubmit={handleSubmitAudit} style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div className="grid-2" style={{ gap: 12 }}>
              <div>
                <label className="form-label">Consumer Meter ID</label>
                <select
                  value={consumerId}
                  onChange={(e) => setConsumerId(e.target.value)}
                  className="scada-select font-mono"
                  style={{ fontWeight: 600 }}
                >
                  {DEFAULT_CONSUMERS.map((cid) => (
                    <option key={cid} value={cid}>
                      {cid}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="form-label">Inspector Crew ID</label>
                <input
                  type="text"
                  value={inspectorId}
                  onChange={(e) => setInspectorId(e.target.value)}
                  className="scada-input font-mono"
                  required
                />
              </div>
            </div>

            <div>
              <label className="form-label">Standardized Audit Status Outcome</label>
              <select
                value={auditStatus}
                onChange={(e) => setAuditStatus(e.target.value)}
                className="scada-select"
                style={{ fontWeight: 600, color: auditStatus === 'CONFIRMED_THEFT_BYPASS' ? '#FCA5A5' : 'var(--text-bright)' }}
              >
                {AUDIT_STATUSES.map((st) => (
                  <option key={st.value} value={st.value}>
                    {st.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid-3" style={{ gap: 12 }}>
              <div>
                <label className="form-label">Meter Serial Verified</label>
                <input
                  type="text"
                  value={meterSerial}
                  onChange={(e) => setMeterSerial(e.target.value)}
                  className="scada-input font-mono"
                />
              </div>

              <div>
                <label className="form-label">Tamper Seal Number</label>
                <input
                  type="text"
                  value={sealNumber}
                  onChange={(e) => setSealNumber(e.target.value)}
                  className="scada-input font-mono"
                />
              </div>

              <div>
                <label className="form-label">Observed Load (kW)</label>
                <input
                  type="number"
                  step="0.1"
                  value={observedLoad}
                  onChange={(e) => setObservedLoad(e.target.value)}
                  className="scada-input font-mono"
                />
              </div>
            </div>

            <div>
              <label className="form-label">Inspector Technical Notes & Findings</label>
              <textarea
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="scada-textarea"
                placeholder="Detail physical bypass type, CT shunt wire, magnetic interference, or premise status..."
              />
            </div>

            {submitError && (
              <div
                style={{
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid var(--red-critical)',
                  borderRadius: 4,
                  padding: '8px 12px',
                  fontSize: '0.75rem',
                  color: '#FCA5A5',
                }}
              >
                {submitError}
              </div>
            )}

            {submitResult && (
              <div
                style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  border: '1px solid var(--green-nominal)',
                  borderRadius: 4,
                  padding: '10px 14px',
                  fontSize: '0.75rem',
                  color: '#6EE7B7',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                }}
              >
                <CheckCircle2 size={16} />
                <div>
                  <strong>Inspection successfully committed!</strong> ID:{' '}
                  <span className="font-mono" style={{ textDecoration: 'underline' }}>
                    {submitResult.inspection_id}
                  </span>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="btn-industrial btn-primary"
              style={{ alignSelf: 'flex-start', marginTop: 4 }}
            >
              {submitting ? 'Submitting to Database...' : 'Submit Field Inspection Record'}
            </button>
          </form>
        </div>

        {/* Form 2: Geo-Tagged Evidence Photo Ingestion */}
        <div className="control-panel">
          <div className="panel-header">
            <div className="panel-title">
              <Camera size={14} style={{ color: 'var(--amber-caution)' }} />
              <span>Geo-Tagged Site Evidence Photo Upload</span>
            </div>
          </div>

          <form onSubmit={handleUploadPhoto} style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div>
              <label className="form-label">Target Inspection ID</label>
              <input
                type="text"
                placeholder="INS-XXXXXXXX"
                value={inspectionIdForUpload}
                onChange={(e) => setInspectionIdForUpload(e.target.value)}
                className="scada-input font-mono"
                required
              />
              <span style={{ fontSize: '0.625rem', color: 'var(--text-dim)', marginTop: 3, display: 'block' }}>
                Auto-populated upon audit submission above, or enter manually.
              </span>
            </div>

            <div>
              <label className="form-label">Photo Classification Category</label>
              <select
                value={photoType}
                onChange={(e) => setPhotoType(e.target.value)}
                className="scada-select font-mono"
              >
                <option value="BYPASS_TAP_PANEL">BYPASS TAP PANEL (Wire Shunt / Direct Tap)</option>
                <option value="METER_SEAL_CLOSEUP">METER SEAL CLOSEUP (Cut / Broken Seal)</option>
                <option value="TERMINAL_BOX">TERMINAL BOX (Reversed CT / Neutral Cut)</option>
                <option value="SITE_OVERVIEW">SITE OVERVIEW (Premises / Commercial Setup)</option>
              </select>
            </div>

            <div className="grid-2" style={{ gap: 12 }}>
              <div>
                <label className="form-label">GPS Latitude</label>
                <input
                  type="number"
                  step="0.0001"
                  value={latitude}
                  onChange={(e) => setLatitude(parseFloat(e.target.value))}
                  className="scada-input font-mono"
                />
              </div>
              <div>
                <label className="form-label">GPS Longitude</label>
                <input
                  type="number"
                  step="0.0001"
                  value={longitude}
                  onChange={(e) => setLongitude(parseFloat(e.target.value))}
                  className="scada-input font-mono"
                />
              </div>
            </div>

            <div>
              <label className="form-label">Select Evidence Image File</label>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={(e) => setSelectedFile(e.target.files[0])}
                className="scada-input"
                style={{ paddingTop: 5 }}
              />
            </div>

            {uploadError && (
              <div
                style={{
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid var(--red-critical)',
                  borderRadius: 4,
                  padding: '8px 12px',
                  fontSize: '0.75rem',
                  color: '#FCA5A5',
                }}
              >
                {uploadError}
              </div>
            )}

            {uploadResult && (
              <div
                style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  border: '1px solid var(--green-nominal)',
                  borderRadius: 4,
                  padding: '10px 14px',
                  fontSize: '0.75rem',
                  color: '#6EE7B7',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                }}
              >
                <CheckCircle2 size={16} />
                <div>
                  <strong>Photo securely stored!</strong> File ID:{' '}
                  <span className="font-mono">{uploadResult.file_id}</span> ({uploadResult.file_size_bytes} bytes)
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={uploading}
              className="btn-industrial btn-secondary"
              style={{ alignSelf: 'flex-start', borderColor: 'var(--border-accent)', color: 'var(--cyan-telemetry)', marginTop: 4 }}
            >
              <Upload size={13} />
              <span>{uploading ? 'Uploading to Storage...' : 'Upload & Link Evidence Image'}</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
