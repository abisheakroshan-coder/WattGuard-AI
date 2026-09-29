import React, { useState, useEffect } from 'react';
import {
  Radio,
  Filter,
  Search,
  RefreshCw,
  ExternalLink,
  ShieldAlert,
  AlertTriangle,
  Zap,
} from 'lucide-react';
import { api } from '../services/api';

export default function Alerts({ onSelectConsumer }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);

  // Filters
  const [riskTier, setRiskTier] = useState('');
  const [tariffClass, setTariffClass] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const params = { page_size: 100 };
      if (riskTier) params.risk_level = riskTier;
      if (tariffClass) params.tariff_class = tariffClass;

      const data = await api.getAlerts(params);
      setAlerts(data.alerts || []);
      setTotalCount(data.total || 0);
    } catch (err) {
      console.error('Failed to query alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [riskTier, tariffClass]);

  // Filter alerts by search query
  const filteredAlerts = alerts.filter((a) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      a.consumer_id?.toLowerCase().includes(q) ||
      a.alert_id?.toLowerCase().includes(q) ||
      a.feeder_id?.toLowerCase().includes(q) ||
      a.transformer_id?.toLowerCase().includes(q)
    );
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Filters & Command Bar */}
      <div
        className="control-panel"
        style={{
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 12,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Radio size={15} style={{ color: 'var(--red-critical)' }} />
            <span
              style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                color: 'var(--text-bright)',
              }}
            >
              Live Telemetry Incident Stream
            </span>
          </div>

          <div style={{ height: 18, width: 1, background: 'var(--border-subtle)' }} />

          {/* Search Input */}
          <div style={{ position: 'relative', width: 220 }}>
            <Search
              size={13}
              style={{
                position: 'absolute',
                left: 8,
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-dim)',
              }}
            />
            <input
              type="text"
              placeholder="Search ID, Feeder, Tx..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="scada-input"
              style={{ paddingLeft: 26, fontSize: '0.75rem' }}
            />
          </div>

          {/* Risk Tier Filter */}
          <select
            value={riskTier}
            onChange={(e) => setRiskTier(e.target.value)}
            className="scada-select"
            style={{ width: 150, fontSize: '0.75rem' }}
          >
            <option value="">ALL RISK TIERS</option>
            <option value="CRITICAL">CRITICAL ONLY</option>
            <option value="HIGH">HIGH ONLY</option>
            <option value="MEDIUM">MEDIUM ONLY</option>
            <option value="LOW">LOW ONLY</option>
          </select>

          {/* Tariff Class Filter */}
          <select
            value={tariffClass}
            onChange={(e) => setTariffClass(e.target.value)}
            className="scada-select"
            style={{ width: 160, fontSize: '0.75rem' }}
          >
            <option value="">ALL TARIFF CLASSES</option>
            <option value="COMMERCIAL">COMMERCIAL</option>
            <option value="RESIDENTIAL">RESIDENTIAL</option>
            <option value="INDUSTRIAL">INDUSTRIAL</option>
            <option value="AGRICULTURAL">AGRICULTURAL</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
            MATCHING: <span className="font-mono" style={{ color: 'var(--cyan-telemetry)' }}>{filteredAlerts.length}</span> / {totalCount}
          </span>
          <button onClick={fetchAlerts} className="btn-industrial btn-secondary btn-sm">
            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
            <span>Sync</span>
          </button>
        </div>
      </div>

      {/* High-Density Table */}
      <div className="control-panel">
        <div className="table-wrapper" style={{ border: 'none', borderRadius: 0 }}>
          <table className="scada-table">
            <thead>
              <tr>
                <th>Priority</th>
                <th>Alert / Consumer ID</th>
                <th>Tariff</th>
                <th>Grid Node (Feeder / Tx)</th>
                <th>Supervised Risk</th>
                <th>Anomaly Score</th>
                <th>Est. Unbilled</th>
                <th>Revenue Loss</th>
                <th>Tamper Flag</th>
                <th>Directive</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan={11} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-dim)' }}>
                    {loading ? 'Querying alerts from FastAPI...' : 'No alerts match the selected criteria.'}
                  </td>
                </tr>
              ) : (
                filteredAlerts.map((alert) => {
                  const isCrit = alert.risk_tier === 'CRITICAL';
                  const isHigh = alert.risk_tier === 'HIGH';
                  const tierBadge = isCrit
                    ? 'badge-critical'
                    : isHigh
                    ? 'badge-high'
                    : alert.risk_tier === 'MEDIUM'
                    ? 'badge-medium'
                    : 'badge-low';

                  return (
                    <tr
                      key={alert.alert_id}
                      className="clickable-row"
                      onClick={() => onSelectConsumer(alert.consumer_id)}
                      title="Click row to open deep Consumer Telemetry view"
                    >
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <span
                            className={`led-indicator ${
                              isCrit ? 'led-red' : isHigh ? 'led-amber' : 'led-cyan'
                            }`}
                          />
                          <span
                            className="font-mono"
                            style={{
                              fontWeight: 800,
                              color: isCrit ? '#EF4444' : isHigh ? '#F59E0B' : 'var(--text-bright)',
                            }}
                          >
                            {alert.composite_priority?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                      </td>

                      <td>
                        <div
                          className="font-mono"
                          style={{
                            fontWeight: 700,
                            color: 'var(--cyan-telemetry)',
                            fontSize: '0.8125rem',
                          }}
                        >
                          {alert.consumer_id}
                        </div>
                        <div className="font-mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                          {alert.alert_id}
                        </div>
                      </td>

                      <td>
                        <span className="badge badge-purple">{alert.tariff_class}</span>
                      </td>

                      <td>
                        <div style={{ fontSize: '0.75rem', fontWeight: 600 }}>{alert.feeder_id}</div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>{alert.transformer_id}</div>
                      </td>

                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <div
                            style={{
                              width: 38,
                              height: 5,
                              background: 'rgba(30, 41, 59, 0.8)',
                              borderRadius: 2,
                              overflow: 'hidden',
                            }}
                          >
                            <div
                              style={{
                                width: `${Math.min(100, (alert.risk_score || 0) * 100)}%`,
                                height: '100%',
                                background:
                                  alert.risk_score > 0.7
                                    ? 'var(--red-critical)'
                                    : alert.risk_score > 0.4
                                    ? 'var(--amber-caution)'
                                    : 'var(--cyan-telemetry)',
                              }}
                            />
                          </div>
                          <span className="font-mono" style={{ fontSize: '0.75rem', fontWeight: 600 }}>
                            {Math.round((alert.risk_score || 0) * 100)}%
                          </span>
                        </div>
                      </td>

                      <td>
                        <span className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {(alert.anomaly_score || 0).toFixed(3)}
                        </span>
                      </td>

                      <td>
                        <span
                          className="font-mono"
                          style={{
                            fontWeight: 600,
                            color: alert.estimated_unbilled_kwh > 0 ? '#FCA5A5' : 'var(--text-main)',
                          }}
                        >
                          {(alert.estimated_unbilled_kwh || 0).toFixed(1)} Units
                        </span>
                      </td>

                      <td>
                        <div className="font-mono" style={{ fontWeight: 600, color: '#FCD34D' }}>
                          ${(alert.estimated_loss_currency || 0).toFixed(2)}
                        </div>
                        <div style={{ fontSize: '0.5625rem', color: 'var(--text-dim)' }}>
                          [${(alert.loss_lower_bound_95 || 0).toFixed(0)} - ${(alert.loss_upper_bound_95 || 0).toFixed(0)}]
                        </div>
                      </td>

                      <td>
                        <span
                          className="badge"
                          style={{
                            background:
                              alert.hardware_tamper_evidence !== 'NORMAL'
                                ? 'rgba(239, 68, 68, 0.2)'
                                : 'rgba(30, 41, 59, 0.5)',
                            color:
                              alert.hardware_tamper_evidence !== 'NORMAL'
                                ? '#FCA5A5'
                                : 'var(--text-dim)',
                            border:
                              alert.hardware_tamper_evidence !== 'NORMAL'
                                ? '1px solid rgba(239, 68, 68, 0.5)'
                                : '1px solid var(--border-subtle)',
                          }}
                        >
                          {alert.hardware_tamper_evidence}
                        </span>
                      </td>

                      <td>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          <span className={`badge ${tierBadge}`}>{alert.recommended_action}</span>
                          {alert.security_escort_required && (
                            <span className="badge badge-critical" style={{ fontSize: '0.5625rem' }}>
                              ESCORT REQ
                            </span>
                          )}
                        </div>
                      </td>

                      <td>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectConsumer(alert.consumer_id);
                          }}
                          className="btn-industrial btn-primary btn-sm"
                          style={{ padding: '3px 8px' }}
                        >
                          <ExternalLink size={11} />
                          <span>Inspect</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
