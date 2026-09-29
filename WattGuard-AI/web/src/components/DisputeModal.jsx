import React, { useState } from 'react';
import { X, ShieldCheck, Download, Copy, Check, FileText, Scale } from 'lucide-react';

export default function DisputeModal({ dossier, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!dossier) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(dossier, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const dataStr =
      'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(dossier, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute(
      'download',
      `WattGuard_Dispute_Dossier_${dossier.consumer_id}_${new Date().toISOString().slice(0, 10)}.json`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Scale size={18} style={{ color: 'var(--cyan-telemetry)' }} />
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
                Legal Dispute Resolution Audit Dossier
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
                Certified Evidentiary Pack for Revenue Recovery Tribunal // Consumer: {dossier.consumer_id}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {/* SHA-256 Hash Seal Banner */}
          <div
            style={{
              background: 'rgba(6, 182, 212, 0.08)',
              border: '1px solid rgba(6, 182, 212, 0.4)',
              borderRadius: 4,
              padding: '12px 14px',
              marginBottom: 16,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <ShieldCheck size={16} style={{ color: 'var(--cyan-telemetry)' }} />
              <span
                style={{
                  fontSize: '0.6875rem',
                  fontWeight: 700,
                  color: 'var(--cyan-telemetry)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}
              >
                Cryptographic Audit Certification Seal
              </span>
            </div>
            <div
              className="font-mono"
              style={{
                fontSize: '0.75rem',
                color: 'var(--text-bright)',
                wordBreak: 'break-all',
                background: 'rgba(7, 11, 18, 0.7)',
                padding: '6px 10px',
                borderRadius: 3,
                border: '1px solid var(--border-subtle)',
              }}
            >
              SHA-256: {dossier.legal_certification_hash}
            </div>
          </div>

          {/* Statutory Violation Summary */}
          <div className="grid-2" style={{ marginBottom: 16 }}>
            <div
              style={{
                background: 'var(--bg-card)',
                padding: '12px 14px',
                border: '1px solid var(--border-subtle)',
                borderRadius: 4,
              }}
            >
              <div className="form-label">Statutory Violation Framework</div>
              <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--red-critical)', marginBottom: 2 }}>
                {dossier.statutory_violation_code || 'ELECTRICITY_ACT_SECTION_135'}
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
                {dossier.statutory_description ||
                  'Unauthorized abstraction and consumption of electrical energy with artificial means or bypassing.'}
              </div>
            </div>

            <div
              style={{
                background: 'var(--bg-card)',
                padding: '12px 14px',
                border: '1px solid var(--border-subtle)',
                borderRadius: 4,
              }}
            >
              <div className="form-label">Assessed Legal Net Claim Amount</div>
              <div className="font-mono" style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FCD34D' }}>
                ${(dossier.net_claim_amount ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
                95% CI Bounds: ${(dossier.claim_lower_bound_95 ?? 0).toFixed(2)} — ${(dossier.claim_upper_bound_95 ?? 0).toFixed(2)}
              </div>
            </div>
          </div>

          {/* Consumer & Telemetry Audit Details */}
          <div
            style={{
              background: 'var(--bg-card)',
              padding: '14px',
              border: '1px solid var(--border-subtle)',
              borderRadius: 4,
              marginBottom: 16,
            }}
          >
            <div
              style={{
                fontSize: '0.6875rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                color: 'var(--text-muted)',
                marginBottom: 10,
                letterSpacing: '0.05em',
              }}
            >
              Consumer Telemetry Audit Summary
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: 12,
                fontSize: '0.75rem',
              }}
            >
              <div>
                <span style={{ color: 'var(--text-dim)', display: 'block', fontSize: '0.6875rem' }}>TARIFF CLASS</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>
                  {dossier.consumer_data?.tariff_class || 'N/A'}
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)', display: 'block', fontSize: '0.6875rem' }}>FEEDER / TX</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>
                  {dossier.consumer_data?.feeder_id || 'N/A'} / {dossier.consumer_data?.transformer_id || 'N/A'}
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)', display: 'block', fontSize: '0.6875rem' }}>HOURS AUDITED</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>
                  {dossier.telemetry_summary?.total_recorded_hours ?? 0} hrs
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)', display: 'block', fontSize: '0.6875rem' }}>TOTAL BILLED</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>
                  {dossier.telemetry_summary?.total_billed_kwh ?? 0} Units
                </span>
              </div>
            </div>
          </div>

          {/* Raw JSON View */}
          <div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: 6,
              }}
            >
              <span
                style={{
                  fontSize: '0.6875rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  color: 'var(--text-muted)',
                  letterSpacing: '0.05em',
                }}
              >
                Evidentiary Case Dossier JSON Payload
              </span>
            </div>
            <pre
              className="font-mono"
              style={{
                background: 'var(--bg-input)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 4,
                padding: '12px',
                fontSize: '0.6875rem',
                color: '#94A3B8',
                maxHeight: '220px',
                overflowY: 'auto',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
              }}
            >
              {JSON.stringify(dossier, null, 2)}
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button onClick={handleCopy} className="btn-industrial btn-secondary">
            {copied ? <Check size={14} style={{ color: 'var(--green-nominal)' }} /> : <Copy size={14} />}
            <span>{copied ? 'Copied to Clipboard' : 'Copy JSON'}</span>
          </button>
          <button onClick={handleDownload} className="btn-industrial btn-primary">
            <Download size={14} />
            <span>Download Certified Dossier (.json)</span>
          </button>
        </div>
      </div>
    </div>
  );
}
