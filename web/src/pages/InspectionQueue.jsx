import React, { useState, useEffect } from 'react';
import {
  ClipboardList,
  Sliders,
  Navigation,
  DollarSign,
  Zap,
  TrendingUp,
  ShieldAlert,
  MapPin,
  RefreshCw,
  ExternalLink,
  Check,
  AlertOctagon,
} from 'lucide-react';
import MetricCard from '../components/MetricCard';
import { api } from '../services/api';

export default function InspectionQueue({ onSelectConsumer }) {
  const [manifest, setManifest] = useState(null);
  const [loading, setLoading] = useState(true);

  // Capacity Control Sliders
  const [limit, setLimit] = useState(20);
  const [weightRisk, setWeightRisk] = useState(0.35);
  const [weightAnomaly, setWeightAnomaly] = useState(0.25);
  const [weightLoss, setWeightLoss] = useState(0.25);
  const [weightConfidence, setWeightConfidence] = useState(0.15);
  const [weightSaving, setWeightSaving] = useState(false);
  const [weightMsg, setWeightMsg] = useState('');

  // Route Optimization (TSP)
  const [startLat, setStartLat] = useState(28.625);
  const [startLon, setStartLon] = useState(77.225);
  const [routeResult, setRouteResult] = useState(null);
  const [routeLoading, setRouteLoading] = useState(false);

  const fetchManifest = async () => {
    setLoading(true);
    try {
      const data = await api.getManifest(limit);
      setManifest(data);
    } catch (err) {
      console.error('Failed to fetch manifest:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchManifest();
  }, [limit]);

  const handleAdjustWeights = async () => {
    setWeightSaving(true);
    setWeightMsg('');
    try {
      const payload = {
        weight_risk: parseFloat(weightRisk),
        weight_anomaly: parseFloat(weightAnomaly),
        weight_loss: parseFloat(weightLoss),
        weight_confidence: parseFloat(weightConfidence),
      };
      await api.adjustWeights(payload);
      setWeightMsg('Weights applied & normalized successfully!');
      setTimeout(() => setWeightMsg(''), 4000);
      await fetchManifest();
    } catch (err) {
      setWeightMsg(`Error: ${err.message}`);
    } finally {
      setWeightSaving(false);
    }
  };

  const handleSolveRoute = async () => {
    if (!manifest?.items || manifest.items.length < 2) return;
    setRouteLoading(true);
    try {
      const alertIds = manifest.items.slice(0, 8).map((it) => it.alert_id).filter(Boolean);
      const res = await api.optimizeRoute(startLat, startLon, alertIds);
      setRouteResult(res);
    } catch (err) {
      console.error('Failed to optimize route:', err);
    } finally {
      setRouteLoading(false);
    }
  };

  const weightsSum = (
    parseFloat(weightRisk) +
    parseFloat(weightAnomaly) +
    parseFloat(weightLoss) +
    parseFloat(weightConfidence)
  ).toFixed(2);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Top Economic Yield KPI Cards */}
      <div className="grid-4">
        <MetricCard
          title="Daily Dispatches"
          value={manifest?.total_dispatches ?? 0}
          unit="INSPECTIONS"
          status="cyan"
          subtext="Capacity-throttled queue"
          icon={ClipboardList}
        />
        <MetricCard
          title="Est. Unbilled Recovery"
          value={(manifest?.aggregate_unbilled_kwh ?? 0).toLocaleString()}
          unit="kWh"
          status="critical"
          subtext="Projected unmetered energy"
          icon={Zap}
        />
        <MetricCard
          title="Gross Revenue Loss"
          value={`$${(manifest?.aggregate_expected_revenue_recovery ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          unit="USD"
          status="caution"
          subtext={`Dispatch Cost: $${manifest?.total_estimated_dispatch_cost ?? 0}`}
          icon={DollarSign}
        />
        <MetricCard
          title="Net ROI Yield"
          value={`$${(manifest?.aggregate_net_yield ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          unit="NET"
          status="nominal"
          subtext="Net economic surplus post-dispatch"
          icon={TrendingUp}
        />
      </div>

      {/* Capacity Control & Route Optimization Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 16 }}>
        {/* Inspection Capacity Control Panel */}
        <div className="control-panel">
          <div className="panel-header">
            <div className="panel-title">
              <Sliders size={14} style={{ color: 'var(--cyan-telemetry)' }} />
              <span>Inspection Capacity & Priority Weight Tuning</span>
            </div>
            <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
              Normalized Sum: <strong style={{ color: weightsSum === '1.00' ? 'var(--green-nominal)' : 'var(--amber-caution)' }}>{weightsSum}</strong>
            </span>
          </div>

          <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 14 }}>
            {/* Weight Sliders */}
            <div className="grid-2" style={{ gap: 14 }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', marginBottom: 4 }}>
                  <span style={{ color: 'var(--text-muted)' }}>w1: THEFT RISK WEIGHT</span>
                  <span className="font-mono" style={{ fontWeight: 700, color: 'var(--cyan-telemetry)' }}>
                    {weightRisk}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.8"
                  step="0.05"
                  value={weightRisk}
                  onChange={(e) => setWeightRisk(e.target.value)}
                  className="scada-slider"
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', marginBottom: 4 }}>
                  <span style={{ color: 'var(--text-muted)' }}>w2: ANOMALY SCORE WEIGHT</span>
                  <span className="font-mono" style={{ fontWeight: 700, color: 'var(--cyan-telemetry)' }}>
                    {weightAnomaly}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.8"
                  step="0.05"
                  value={weightAnomaly}
                  onChange={(e) => setWeightAnomaly(e.target.value)}
                  className="scada-slider"
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', marginBottom: 4 }}>
                  <span style={{ color: 'var(--text-muted)' }}>w3: UNBILLED LOSS WEIGHT</span>
                  <span className="font-mono" style={{ fontWeight: 700, color: 'var(--cyan-telemetry)' }}>
                    {weightLoss}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.8"
                  step="0.05"
                  value={weightLoss}
                  onChange={(e) => setWeightLoss(e.target.value)}
                  className="scada-slider"
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', marginBottom: 4 }}>
                  <span style={{ color: 'var(--text-muted)' }}>w4: MODEL CONFIDENCE WEIGHT</span>
                  <span className="font-mono" style={{ fontWeight: 700, color: 'var(--cyan-telemetry)' }}>
                    {weightConfidence}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.8"
                  step="0.05"
                  value={weightConfidence}
                  onChange={(e) => setWeightConfidence(e.target.value)}
                  className="scada-slider"
                />
              </div>
            </div>

            {/* Capacity Limit Slider */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', marginBottom: 4 }}>
                <span style={{ color: 'var(--text-muted)' }}>INSPECTION CREW DAILY CAPACITY LIMIT</span>
                <span className="font-mono" style={{ fontWeight: 700, color: '#FCD34D' }}>
                  {limit} DISPATCHES / DAY
                </span>
              </div>
              <input
                type="range"
                min="5"
                max="50"
                step="5"
                value={limit}
                onChange={(e) => setLimit(parseInt(e.target.value))}
                className="scada-slider"
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 4 }}>
              <span style={{ fontSize: '0.6875rem', color: weightMsg.startsWith('Error') ? 'var(--red-critical)' : 'var(--green-nominal)' }}>
                {weightMsg}
              </span>
              <button
                onClick={handleAdjustWeights}
                disabled={weightSaving}
                className="btn-industrial btn-primary"
              >
                {weightSaving ? <RefreshCw size={13} className="animate-spin" /> : <Check size={13} />}
                <span>Apply Operational Weights</span>
              </button>
            </div>
          </div>
        </div>

        {/* TSP Fleet Route Optimization */}
        <div className="control-panel">
          <div className="panel-header">
            <div className="panel-title">
              <Navigation size={14} style={{ color: 'var(--amber-caution)' }} />
              <span>Inspector TSP Route Optimization (Fleet Logistics)</span>
            </div>
          </div>

          <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div className="grid-2" style={{ gap: 10 }}>
              <div>
                <label className="form-label">Depot Start Latitude</label>
                <input
                  type="number"
                  step="0.001"
                  value={startLat}
                  onChange={(e) => setStartLat(parseFloat(e.target.value))}
                  className="scada-input font-mono"
                />
              </div>
              <div>
                <label className="form-label">Depot Start Longitude</label>
                <input
                  type="number"
                  step="0.001"
                  value={startLon}
                  onChange={(e) => setStartLon(parseFloat(e.target.value))}
                  className="scada-input font-mono"
                />
              </div>
            </div>

            <button
              onClick={handleSolveRoute}
              disabled={routeLoading || !manifest?.items?.length}
              className="btn-industrial btn-secondary"
              style={{ width: '100%', borderColor: 'var(--border-accent)', color: 'var(--cyan-telemetry)' }}
            >
              {routeLoading ? <RefreshCw size={13} className="animate-spin" /> : <Navigation size={13} />}
              <span>Compute Vehicle Inspection Route (TSP)</span>
            </button>

            {routeResult && (
              <div
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 4,
                  padding: '12px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 8,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>STOPS: <strong style={{ color: 'var(--text-bright)' }}>{routeResult.total_stops}</strong></span>
                  <span style={{ color: 'var(--text-muted)' }}>DISTANCE: <strong className="font-mono" style={{ color: 'var(--cyan-telemetry)' }}>{routeResult.total_distance_km} km</strong></span>
                  <span style={{ color: 'var(--text-muted)' }}>EST. DURATION: <strong className="font-mono" style={{ color: '#FCD34D' }}>{routeResult.estimated_total_tour_minutes} mins</strong></span>
                </div>

                <div
                  className="font-mono"
                  style={{
                    fontSize: '0.6875rem',
                    color: 'var(--text-dim)',
                    background: 'rgba(7, 11, 18, 0.7)',
                    padding: '8px',
                    borderRadius: 3,
                    maxHeight: '80px',
                    overflowY: 'auto',
                  }}
                >
                  {routeResult.ordered_waypoints?.map((wp, i) => (
                    <div key={i}>
                      #{i}: {wp.name || wp.alert_id || 'Depot'} ({wp.latitude?.toFixed(4)}, {wp.longitude?.toFixed(4)})
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Prioritized Daily Manifest Table */}
      <div className="control-panel">
        <div className="panel-header">
          <div className="panel-title">
            <ClipboardList size={14} style={{ color: 'var(--cyan-telemetry)' }} />
            <span>Prioritized Inspection Dispatch Manifest ({manifest?.items?.length ?? 0} Nodes)</span>
          </div>
          <button onClick={fetchManifest} className="btn-industrial btn-secondary btn-sm">
            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
            <span>Sync Manifest</span>
          </button>
        </div>

        <div className="table-wrapper" style={{ border: 'none', borderRadius: 0 }}>
          <table className="scada-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Consumer ID</th>
                <th>Tariff</th>
                <th>Feeder / Tx</th>
                <th>GPS Location</th>
                <th>Priority Score</th>
                <th>Loss Bounds ($)</th>
                <th>Net Yield</th>
                <th>Tamper Flag</th>
                <th>Action Directive</th>
                <th>Escort Req.</th>
                <th>Primary Reason</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {!manifest?.items || manifest.items.length === 0 ? (
                <tr>
                  <td colSpan={13} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-dim)' }}>
                    {loading ? 'Retrieving prioritized manifest from FastAPI...' : 'No manifest items found.'}
                  </td>
                </tr>
              ) : (
                manifest.items.map((item) => {
                  const isCrit = item.risk_tier === 'CRITICAL';
                  const isHigh = item.risk_tier === 'HIGH';

                  return (
                    <tr
                      key={item.alert_id}
                      className="clickable-row"
                      onClick={() => onSelectConsumer(item.consumer_id)}
                      title="Click row to open Consumer Telemetry view"
                    >
                      <td>
                        <span className="font-mono" style={{ fontWeight: 800, color: 'var(--text-dim)' }}>
                          #{item.rank}
                        </span>
                      </td>

                      <td>
                        <div className="font-mono" style={{ fontWeight: 700, color: 'var(--cyan-telemetry)' }}>
                          {item.consumer_id}
                        </div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                          {item.alert_id}
                        </div>
                      </td>

                      <td>
                        <span className="badge badge-purple">{item.tariff_class}</span>
                      </td>

                      <td>
                        <div style={{ fontSize: '0.75rem', fontWeight: 600 }}>{item.feeder_id}</div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>{item.transformer_id}</div>
                      </td>

                      <td>
                        <div className="font-mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
                          {item.latitude?.toFixed(4)}, {item.longitude?.toFixed(4)}
                        </div>
                      </td>

                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <span
                            className={`led-indicator ${
                              isCrit ? 'led-red' : isHigh ? 'led-amber' : 'led-cyan'
                            }`}
                          />
                          <span className="font-mono" style={{ fontWeight: 800, color: isCrit ? '#EF4444' : isHigh ? '#F59E0B' : 'var(--text-bright)' }}>
                            {item.composite_priority?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                      </td>

                      <td>
                        <span className="font-mono" style={{ color: '#FCD34D', fontWeight: 600 }}>
                          ${(item.loss_upper_bound_95 || 0).toFixed(0)}
                        </span>
                      </td>

                      <td>
                        <span
                          className="font-mono"
                          style={{
                            fontWeight: 600,
                            color: item.net_roi_yield > 0 ? 'var(--green-nominal)' : 'var(--text-dim)',
                          }}
                        >
                          ${(item.net_roi_yield || 0).toFixed(0)}
                        </span>
                      </td>

                      <td>
                        <span
                          className="badge"
                          style={{
                            background: item.tamper_flags !== 'NORMAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(30, 41, 59, 0.5)',
                            color: item.tamper_flags !== 'NORMAL' ? '#FCA5A5' : 'var(--text-dim)',
                          }}
                        >
                          {item.tamper_flags}
                        </span>
                      </td>

                      <td>
                        <span className="badge badge-cyan">{item.recommended_action}</span>
                      </td>

                      <td>
                        {item.security_escort_required ? (
                          <span className="badge badge-critical">ESCORT MANDATED</span>
                        ) : (
                          <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Standard</span>
                        )}
                      </td>

                      <td>
                        <div
                          style={{
                            maxWidth: 220,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            fontSize: '0.6875rem',
                            color: 'var(--text-muted)',
                          }}
                          title={item.primary_reason}
                        >
                          {item.primary_reason}
                        </div>
                      </td>

                      <td>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectConsumer(item.consumer_id);
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
