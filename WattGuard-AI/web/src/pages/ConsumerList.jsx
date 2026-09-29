import React, { useState, useEffect } from 'react';
import { Users, Search, RefreshCw, ExternalLink, Zap, MapPin } from 'lucide-react';
import { api } from '../services/api';

export default function ConsumerList({ onSelectConsumer }) {
  const [consumers, setConsumers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [tariffFilter, setTariffFilter] = useState('');
  const [feederFilter, setFeederFilter] = useState('');

  const loadConsumers = async () => {
    setLoading(true);
    try {
      // Manifest gives detailed consumer rows with priority and coordinates
      const manifest = await api.getManifest(100);
      setConsumers(manifest.items || []);
    } catch (err) {
      console.error('Failed to load consumers list:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConsumers();
  }, []);

  const filtered = consumers.filter((c) => {
    if (tariffFilter && c.tariff_class !== tariffFilter) return false;
    if (feederFilter && c.feeder_id !== feederFilter) return false;
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      c.consumer_id?.toLowerCase().includes(q) ||
      c.feeder_id?.toLowerCase().includes(q) ||
      c.transformer_id?.toLowerCase().includes(q)
    );
  });

  const uniqueFeeders = Array.from(new Set(consumers.map((c) => c.feeder_id).filter(Boolean)));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Controls Bar */}
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
            <Users size={15} style={{ color: 'var(--cyan-telemetry)' }} />
            <span
              style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                color: 'var(--text-bright)',
              }}
            >
              Consumer Registry & Meter Fleet Directory
            </span>
          </div>

          <div style={{ height: 18, width: 1, background: 'var(--border-subtle)' }} />

          {/* Search */}
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
              placeholder="Search Consumer ID, Feeder..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="scada-input"
              style={{ paddingLeft: 26, fontSize: '0.75rem' }}
            />
          </div>

          {/* Tariff Class */}
          <select
            value={tariffFilter}
            onChange={(e) => setTariffFilter(e.target.value)}
            className="scada-select"
            style={{ width: 150, fontSize: '0.75rem' }}
          >
            <option value="">ALL TARIFFS</option>
            <option value="COMMERCIAL">COMMERCIAL</option>
            <option value="RESIDENTIAL">RESIDENTIAL</option>
            <option value="INDUSTRIAL">INDUSTRIAL</option>
          </select>

          {/* Feeder Filter */}
          <select
            value={feederFilter}
            onChange={(e) => setFeederFilter(e.target.value)}
            className="scada-select"
            style={{ width: 160, fontSize: '0.75rem' }}
          >
            <option value="">ALL FEEDERS</option>
            {uniqueFeeders.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
            RECORDS: <span className="font-mono" style={{ color: 'var(--cyan-telemetry)' }}>{filtered.length}</span> / {consumers.length}
          </span>
          <button onClick={loadConsumers} className="btn-industrial btn-secondary btn-sm">
            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
            <span>Sync</span>
          </button>
        </div>
      </div>

      {/* High Density Consumer Fleet Table */}
      <div className="control-panel">
        <div className="table-wrapper" style={{ border: 'none', borderRadius: 0 }}>
          <table className="scada-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Consumer ID</th>
                <th>Tariff Class</th>
                <th>Feeder ID</th>
                <th>Transformer ID</th>
                <th>Coordinates (Lat, Lon)</th>
                <th>Composite Priority</th>
                <th>Risk Tier</th>
                <th>Unbilled Loss</th>
                <th>Tamper Flag</th>
                <th>Action Directive</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={12} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-dim)' }}>
                    {loading ? 'Retrieving consumer meters from FastAPI backend...' : 'No consumers match query.'}
                  </td>
                </tr>
              ) : (
                filtered.map((c) => {
                  const isCrit = c.risk_tier === 'CRITICAL';
                  const isHigh = c.risk_tier === 'HIGH';
                  const tierBadge = isCrit
                    ? 'badge-critical'
                    : isHigh
                    ? 'badge-high'
                    : c.risk_tier === 'MEDIUM'
                    ? 'badge-medium'
                    : 'badge-low';

                  return (
                    <tr
                      key={c.consumer_id}
                      className="clickable-row"
                      onClick={() => onSelectConsumer(c.consumer_id)}
                      title="Click to view full consumer telemetry & explainability"
                    >
                      <td>
                        <span className="font-mono" style={{ color: 'var(--text-dim)', fontWeight: 700 }}>
                          #{c.rank}
                        </span>
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
                          {c.consumer_id}
                        </div>
                      </td>

                      <td>
                        <span className="badge badge-purple">{c.tariff_class}</span>
                      </td>

                      <td>
                        <span className="font-mono" style={{ fontWeight: 600 }}>
                          {c.feeder_id}
                        </span>
                      </td>

                      <td>
                        <span className="font-mono" style={{ color: 'var(--text-muted)' }}>
                          {c.transformer_id}
                        </span>
                      </td>

                      <td>
                        <div className="font-mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
                          {c.latitude?.toFixed(4)}, {c.longitude?.toFixed(4)}
                        </div>
                      </td>

                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <span
                            className={`led-indicator ${
                              isCrit ? 'led-red' : isHigh ? 'led-amber' : 'led-cyan'
                            }`}
                          />
                          <span className="font-mono" style={{ fontWeight: 700 }}>
                            {c.composite_priority?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                      </td>

                      <td>
                        <span className={`badge ${tierBadge}`}>{c.risk_tier}</span>
                      </td>

                      <td>
                        <div className="font-mono" style={{ fontWeight: 600, color: '#FCD34D' }}>
                          ${(c.estimated_loss_currency || 0).toFixed(2)}
                        </div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                          {(c.estimated_unbilled_kwh || 0).toFixed(1)} Units
                        </div>
                      </td>

                      <td>
                        <span
                          className="badge"
                          style={{
                            background:
                              c.tamper_flags !== 'NORMAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(30, 41, 59, 0.5)',
                            color: c.tamper_flags !== 'NORMAL' ? '#FCA5A5' : 'var(--text-dim)',
                          }}
                        >
                          {c.tamper_flags}
                        </span>
                      </td>

                      <td>
                        <span className="badge badge-cyan">{c.recommended_action}</span>
                      </td>

                      <td>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectConsumer(c.consumer_id);
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
