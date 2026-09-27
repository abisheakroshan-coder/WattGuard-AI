import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  Zap,
  DollarSign,
  MapPin,
  Flame,
  ShieldCheck,
  ChevronRight,
  TrendingDown,
  RefreshCw,
  Server,
  Layers,
} from 'lucide-react';
import MetricCard from '../components/MetricCard';
import { api } from '../services/api';

export default function Dashboard({ onSelectConsumer, onNavigate }) {
  const [loading, setLoading] = useState(true);
  const [alertsData, setAlertsData] = useState({ alerts: [], total: 0 });
  const [feeders, setFeeders] = useState([]);
  const [hotspots, setHotspots] = useState({ hotspots: [], total_hotspots_detected: 0 });
  const [manifest, setManifest] = useState(null);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [alertsRes, feederRes, hotspotRes, manifestRes] = await Promise.allSettled([
        api.getAlerts({ page_size: 25 }),
        api.getFeederVulnerability(),
        api.getHotspots(3.0, 2),
        api.getManifest(25),
      ]);

      if (alertsRes.status === 'fulfilled') setAlertsData(alertsRes.value);
      if (feederRes.status === 'fulfilled') setFeeders(feederRes.value.feeders || []);
      if (hotspotRes.status === 'fulfilled') setHotspots(hotspotRes.value);
      if (manifestRes.status === 'fulfilled') setManifest(manifestRes.value);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const criticalCount = alertsData.alerts.filter((a) => a.risk_tier === 'CRITICAL').length;
  const highCount = alertsData.alerts.filter((a) => a.risk_tier === 'HIGH').length;
  const totalUnbilled = alertsData.alerts.reduce((acc, a) => acc + (a.estimated_unbilled_kwh || 0), 0);
  const totalLoss = alertsData.alerts.reduce((acc, a) => acc + (a.estimated_loss_currency || 0), 0);
  const priorityRaids = manifest?.high_priority_raids_count ?? 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
      {/* Top SCADA Metrics Grid */}
      <div className="grid-4">
        <MetricCard
          title="Active Live Alerts"
          value={alertsData.total}
          unit="METERS"
          status={criticalCount > 0 ? 'critical' : alertsData.total > 0 ? 'caution' : 'nominal'}
          subtext={`${criticalCount} Critical, ${highCount} High Tier`}
          icon={AlertTriangle}
        />
        <MetricCard
          title="Est. Unbilled Energy"
          value={totalUnbilled.toLocaleString(undefined, { maximumFractionDigits: 1 })}
          unit="kWh"
          status={totalUnbilled > 500 ? 'critical' : 'cyan'}
          subtext="Unaccounted baseline delta"
          icon={Zap}
        />
        <MetricCard
          title="Revenue Exposure"
          value={`$${totalLoss.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          unit="USD"
          status={totalLoss > 1000 ? 'critical' : 'caution'}
          subtext="Immediate financial recovery target"
          icon={DollarSign}
        />
        <MetricCard
          title="Priority Raids Queued"
          value={priorityRaids}
          unit="UNITS"
          status={priorityRaids > 0 ? 'critical' : 'nominal'}
          subtext={`${manifest?.security_escorts_required_count ?? 0} with Security Escort`}
          icon={Flame}
        />
      </div>

      {/* Main Grid: Live Incidents & Feeder Vulnerability */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 18 }}>
        {/* Left Column: Live High-Risk Incidents Table */}
        <div className="control-panel">
          <div className="panel-header">
            <div className="panel-title">
              <Activity size={14} style={{ color: 'var(--cyan-telemetry)' }} />
              <span>Live High-Priority Theft Alerts ({alertsData.alerts.length})</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <button
                onClick={loadDashboardData}
                className="btn-industrial btn-secondary btn-sm"
                title="Refresh Feed"
              >
                <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                <span>Sync</span>
              </button>
              <button
                onClick={() => onNavigate('alerts')}
                className="btn-industrial btn-secondary btn-sm"
              >
                <span>View All ({alertsData.total})</span>
                <ChevronRight size={12} />
              </button>
            </div>
          </div>

          <div className="table-wrapper" style={{ border: 'none', borderRadius: 0, maxHeight: 420 }}>
            <table className="scada-table">
              <thead>
                <tr>
                  <th>Priority</th>
                  <th>Consumer ID</th>
                  <th>Feeder / Transformer</th>
                  <th>Tariff</th>
                  <th>Risk %</th>
                  <th>Anomaly</th>
                  <th>Unbilled kWh</th>
                  <th>Action Directive</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {alertsData.alerts.length === 0 ? (
                  <tr>
                    <td colSpan={9} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-dim)' }}>
                      {loading ? 'Polling active telemetry alerts from FastAPI...' : 'No active alerts detected.'}
                    </td>
                  </tr>
                ) : (
                  alertsData.alerts.map((alert) => {
                    const tierClass =
                      alert.risk_tier === 'CRITICAL'
                        ? 'badge-critical'
                        : alert.risk_tier === 'HIGH'
                        ? 'badge-high'
                        : alert.risk_tier === 'MEDIUM'
                        ? 'badge-medium'
                        : 'badge-low';

                    return (
                      <tr
                        key={alert.alert_id}
                        className="clickable-row"
                        onClick={() => onSelectConsumer(alert.consumer_id)}
                        title="Click to view full consumer telemetry & explainability"
                      >
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <span
                              className={`led-indicator ${
                                alert.risk_tier === 'CRITICAL'
                                  ? 'led-red'
                                  : alert.risk_tier === 'HIGH'
                                  ? 'led-amber'
                                  : 'led-cyan'
                              }`}
                            />
                            <span className="font-mono" style={{ fontWeight: 700, fontSize: '0.8125rem' }}>
                              {alert.composite_priority?.toFixed(1) || '0.0'}
                            </span>
                          </div>
                        </td>
                        <td>
                          <div className="font-mono" style={{ fontWeight: 700, color: 'var(--cyan-telemetry)' }}>
                            {alert.consumer_id}
                          </div>
                          <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                            {alert.alert_id}
                          </div>
                        </td>
                        <td>
                          <div style={{ fontSize: '0.75rem', fontWeight: 600 }}>
                            {alert.feeder_id}
                          </div>
                          <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                            {alert.transformer_id}
                          </div>
                        </td>
                        <td>
                          <span className="badge badge-purple">{alert.tariff_class}</span>
                        </td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <div
                              style={{
                                width: 44,
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
                            <span className="font-mono" style={{ fontSize: '0.75rem' }}>
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
                              color: alert.estimated_unbilled_kwh > 0 ? '#FCA5A5' : 'var(--text-main)',
                              fontWeight: 600,
                            }}
                          >
                            {(alert.estimated_unbilled_kwh || 0).toFixed(1)}
                          </span>
                        </td>
                        <td>
                          <span className={`badge ${tierClass}`}>{alert.recommended_action}</span>
                        </td>
                        <td>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onSelectConsumer(alert.consumer_id);
                            }}
                            className="btn-industrial btn-secondary btn-sm"
                            style={{ padding: '3px 8px' }}
                          >
                            Inspect
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

        {/* Right Column: Feeder Vulnerability Rankings */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          <div className="control-panel">
            <div className="panel-header">
              <div className="panel-title">
                <Layers size={14} style={{ color: 'var(--amber-caution)' }} />
                <span>Feeder Vulnerability Rankings</span>
              </div>
            </div>
            <div style={{ padding: 14 }}>
              {feeders.length === 0 ? (
                <div style={{ color: 'var(--text-dim)', fontSize: '0.75rem', textAlign: 'center', padding: '20px' }}>
                  Loading feeder telemetry...
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {feeders.map((f, idx) => (
                    <div
                      key={f.feeder_id || idx}
                      style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 4,
                        padding: '10px 12px',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          marginBottom: 6,
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span
                            className="font-mono"
                            style={{
                              fontSize: '0.75rem',
                              fontWeight: 800,
                              color: idx === 0 ? '#EF4444' : idx === 1 ? '#F59E0B' : 'var(--text-muted)',
                            }}
                          >
                            #{idx + 1}
                          </span>
                          <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--text-bright)' }}>
                            {f.feeder_id}
                          </span>
                        </div>
                        <span
                          className="badge"
                          style={{
                            background: f.composite_vulnerability_index > 50 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                            color: f.composite_vulnerability_index > 50 ? '#FCA5A5' : '#93C5FD',
                          }}
                        >
                          INDEX: {(f.composite_vulnerability_index || 0).toFixed(1)}
                        </span>
                      </div>

                      {/* Mini Bar */}
                      <div
                        style={{
                          width: '100%',
                          height: 5,
                          background: 'rgba(30, 41, 59, 0.8)',
                          borderRadius: 2,
                          overflow: 'hidden',
                          marginBottom: 6,
                        }}
                      >
                        <div
                          style={{
                            width: `${Math.min(100, f.composite_vulnerability_index || 0)}%`,
                            height: '100%',
                            background:
                              f.composite_vulnerability_index > 60
                                ? 'var(--red-critical)'
                                : f.composite_vulnerability_index > 30
                                ? 'var(--amber-caution)'
                                : 'var(--cyan-telemetry)',
                          }}
                        />
                      </div>

                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          fontSize: '0.6875rem',
                          color: 'var(--text-dim)',
                        }}
                      >
                        <span>Active Alerts: {f.active_alerts_count ?? 0}</span>
                        <span>Unbilled: {f.estimated_unbilled_kwh?.toFixed(1) ?? '0.0'} kWh</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Geographic Hotspots Mini Summary */}
          <div className="control-panel">
            <div className="panel-header">
              <div className="panel-title">
                <MapPin size={14} style={{ color: 'var(--cyan-telemetry)' }} />
                <span>Active Theft Hotspots ({hotspots.total_hotspots_detected})</span>
              </div>
            </div>
            <div style={{ padding: 14 }}>
              {hotspots.hotspots.length === 0 ? (
                <div style={{ color: 'var(--text-dim)', fontSize: '0.75rem', textAlign: 'center', padding: '16px' }}>
                  No geographic clusters detected. Meters are geographically dispersed.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {hotspots.hotspots.map((hs, idx) => (
                    <div
                      key={hs.cluster_id || idx}
                      style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 3,
                        padding: '8px 10px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div>
                        <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-bright)' }}>
                          {hs.cluster_id} // Feeder: {hs.dominant_feeder}
                        </div>
                        <div className="font-mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                          Centroid: {hs.centroid_latitude?.toFixed(4)}, {hs.centroid_longitude?.toFixed(4)}
                        </div>
                      </div>
                      <span className="badge badge-critical">{hs.alert_count} METERS</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
