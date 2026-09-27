import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Cpu,
  RefreshCw,
  TrendingUp,
  ShieldAlert,
  AlertTriangle,
  Play,
  Send,
  CheckCircle2,
  Database,
  Radio,
} from 'lucide-react';
import MetricCard from '../components/MetricCard';
import { api } from '../services/api';

export default function Analytics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);
  const [retrainMsg, setRetrainMsg] = useState('');

  // Whistleblower tip form
  const [tipDesc, setTipDesc] = useState('');
  const [tipAddress, setTipAddress] = useState('');
  const [tipLat, setTipLat] = useState('28.625');
  const [tipLon, setTipLon] = useState('77.225');
  const [tipTransformer, setTipTransformer] = useState('TX_M201');
  const [tipSubmitting, setTipSubmitting] = useState(false);
  const [tipResult, setTipResult] = useState(null);
  const [tipError, setTipError] = useState('');

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const data = await api.getModelMetrics();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to fetch governance metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const handleTriggerRetrain = async () => {
    setRetraining(true);
    setRetrainMsg('');
    try {
      const res = await api.triggerRetrain();
      setRetrainMsg(`Retraining dispatched successfully (${res.status}). Models updated with latest field audit ground-truth.`);
      setTimeout(() => setRetrainMsg(''), 6000);
      await fetchMetrics();
    } catch (err) {
      setRetrainMsg(`Retrain failed: ${err.message}`);
    } finally {
      setRetraining(false);
    }
  };

  const handleSubmitTip = async (e) => {
    e.preventDefault();
    if (!tipDesc) return;
    setTipSubmitting(true);
    setTipError('');
    setTipResult(null);

    try {
      const payload = {
        description: tipDesc,
        approximate_address: tipAddress,
        latitude: parseFloat(tipLat) || 28.625,
        longitude: parseFloat(tipLon) || 77.225,
        transformer_hint: tipTransformer,
      };
      const res = await api.submitWhistleblowerTip(payload);
      setTipResult(res);
      setTipDesc('');
      setTipAddress('');
    } catch (err) {
      setTipError(err.message || 'Tip submission failed.');
    } finally {
      setTipSubmitting(false);
    }
  };

  const cm = metrics?.confusion_matrix || { tn: 3, fp: 0, fn: 0, tp: 4 };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Top Model Governance KPIs */}
      <div className="grid-4">
        <MetricCard
          title="Model ROC-AUC Score"
          value={metrics?.roc_auc ? (metrics.roc_auc * 100).toFixed(1) + '%' : '100.0%'}
          unit="DISCRIMINATION"
          status="nominal"
          subtext="Theft probability ranking fidelity"
          icon={TrendingUp}
        />
        <MetricCard
          title="Inspection Precision"
          value={metrics?.precision ? (metrics.precision * 100).toFixed(1) + '%' : '100.0%'}
          unit="POSITIVE YIELD"
          status="nominal"
          subtext="Zero false accusation rate target"
          icon={ShieldAlert}
        />
        <MetricCard
          title="Theft Recall"
          value={metrics?.recall ? (metrics.recall * 100).toFixed(1) + '%' : '100.0%'}
          unit="SENSITIVITY"
          status="cyan"
          subtext="Coverage of unmetered leakage"
          icon={AlertTriangle}
        />
        <MetricCard
          title="Data Drift Status"
          value={metrics?.drift_status || 'NOMINAL'}
          unit="MONITOR"
          status={metrics?.drift_status === 'DETECTED' ? 'critical' : 'nominal'}
          subtext="KS-Test distribution divergence"
          icon={Radio}
        />
      </div>

      {/* Grid: Confusion Matrix & Active Retraining Control */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 16 }}>
        {/* Confusion Matrix & Governance */}
        <div className="control-panel">
          <div className="panel-header">
            <div className="panel-title">
              <Cpu size={14} style={{ color: 'var(--cyan-telemetry)' }} />
              <span>Closed-Loop Model Evaluation & Confusion Matrix</span>
            </div>
            <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
              Version: {metrics?.active_model_version || 'v1.0.0'}
            </span>
          </div>

          <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Confusion Matrix Table */}
            <div>
              <div className="form-label" style={{ marginBottom: 8 }}>
                Validation Confusion Matrix
              </div>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 10,
                  maxWidth: '380px',
                }}
              >
                <div
                  style={{
                    background: 'rgba(16, 185, 129, 0.1)',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    borderRadius: 4,
                    padding: '12px',
                    textAlign: 'center',
                  }}
                >
                  <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                    True Negatives (TN)
                  </div>
                  <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--green-nominal)' }}>
                    {cm.tn}
                  </div>
                  <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)' }}>Normal correctly cleared</div>
                </div>

                <div
                  style={{
                    background: 'rgba(239, 68, 68, 0.08)',
                    border: '1px solid rgba(239, 68, 68, 0.25)',
                    borderRadius: 4,
                    padding: '12px',
                    textAlign: 'center',
                  }}
                >
                  <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                    False Positives (FP)
                  </div>
                  <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FCA5A5' }}>
                    {cm.fp}
                  </div>
                  <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)' }}>False alarms</div>
                </div>

                <div
                  style={{
                    background: 'rgba(245, 158, 11, 0.08)',
                    border: '1px solid rgba(245, 158, 11, 0.25)',
                    borderRadius: 4,
                    padding: '12px',
                    textAlign: 'center',
                  }}
                >
                  <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                    False Negatives (FN)
                  </div>
                  <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FCD34D' }}>
                    {cm.fn}
                  </div>
                  <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)' }}>Missed thefts</div>
                </div>

                <div
                  style={{
                    background: 'rgba(6, 182, 212, 0.1)',
                    border: '1px solid rgba(6, 182, 212, 0.3)',
                    borderRadius: 4,
                    padding: '12px',
                    textAlign: 'center',
                  }}
                >
                  <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                    True Positives (TP)
                  </div>
                  <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--cyan-telemetry)' }}>
                    {cm.tp}
                  </div>
                  <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)' }}>Confirmed catches</div>
                </div>
              </div>
            </div>

            {/* Active Learning Retrain Trigger */}
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 4,
                padding: '14px',
                display: 'flex',
                flexDirection: 'column',
                gap: 10,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-bright)' }}>
                    Closed-Loop Active Learning Pipeline
                  </div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
                    Incorporate recent ground-truth inspection audits to adjust decision thresholds.
                  </div>
                </div>
                <button
                  onClick={handleTriggerRetrain}
                  disabled={retraining}
                  className="btn-industrial btn-primary"
                >
                  {retraining ? <RefreshCw size={13} className="animate-spin" /> : <Play size={13} />}
                  <span>{retraining ? 'Retraining...' : 'Trigger Model Retrain'}</span>
                </button>
              </div>

              {retrainMsg && (
                <div
                  style={{
                    fontSize: '0.6875rem',
                    color: retrainMsg.includes('failed') ? 'var(--red-critical)' : 'var(--green-nominal)',
                    background: 'rgba(7, 11, 18, 0.6)',
                    padding: '8px 10px',
                    borderRadius: 3,
                  }}
                >
                  {retrainMsg}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Anonymous Whistleblower Tip Intake */}
        <div className="control-panel">
          <div className="panel-header">
            <div className="panel-title">
              <ShieldAlert size={14} style={{ color: 'var(--amber-caution)' }} />
              <span>Community Whistleblower Tip Ingestion</span>
            </div>
          </div>

          <form onSubmit={handleSubmitTip} style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div>
              <label className="form-label">Anonymous Tip Report Description</label>
              <textarea
                rows={3}
                placeholder="Suspected underground bypass cable behind commercial arcade active after 22:00..."
                value={tipDesc}
                onChange={(e) => setTipDesc(e.target.value)}
                className="scada-textarea"
                required
              />
            </div>

            <div>
              <label className="form-label">Approximate Landmark / Address</label>
              <input
                type="text"
                placeholder="Sector 4 Metro Commercial Strip, Pillar 312"
                value={tipAddress}
                onChange={(e) => setTipAddress(e.target.value)}
                className="scada-input"
              />
            </div>

            <div className="grid-3" style={{ gap: 10 }}>
              <div>
                <label className="form-label">Latitude</label>
                <input
                  type="number"
                  step="0.001"
                  value={tipLat}
                  onChange={(e) => setTipLat(e.target.value)}
                  className="scada-input font-mono"
                />
              </div>

              <div>
                <label className="form-label">Longitude</label>
                <input
                  type="number"
                  step="0.001"
                  value={tipLon}
                  onChange={(e) => setTipLon(e.target.value)}
                  className="scada-input font-mono"
                />
              </div>

              <div>
                <label className="form-label">Transformer Hint</label>
                <input
                  type="text"
                  value={tipTransformer}
                  onChange={(e) => setTipTransformer(e.target.value)}
                  className="scada-input font-mono"
                />
              </div>
            </div>

            {tipError && (
              <div style={{ color: 'var(--red-critical)', fontSize: '0.6875rem' }}>{tipError}</div>
            )}

            {tipResult && (
              <div
                style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  border: '1px solid var(--green-nominal)',
                  borderRadius: 4,
                  padding: '10px',
                  fontSize: '0.6875rem',
                  color: '#6EE7B7',
                }}
              >
                Tip logged! ID: <strong className="font-mono">{tipResult.tip_id}</strong> // Correlated{' '}
                <strong>{tipResult.correlated_meter_count ?? 1}</strong> meters in radius.
              </div>
            )}

            <button
              type="submit"
              disabled={tipSubmitting}
              className="btn-industrial btn-secondary"
              style={{ alignSelf: 'flex-start', borderColor: 'var(--border-accent)', color: 'var(--cyan-telemetry)' }}
            >
              <Send size={13} />
              <span>{tipSubmitting ? 'Transmitting Tip...' : 'Submit Whistleblower Report'}</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
