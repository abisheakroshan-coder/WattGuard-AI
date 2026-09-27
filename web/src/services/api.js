/**
 * WattGuard AI - API Service Layer
 * Connects directly to FastAPI backend on http://127.0.0.1:8001 (or via Vite proxy).
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

async function fetchJSON(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  const defaultHeaders = options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' };
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errData = await response.json();
      errorDetail = errData.detail || errorDetail;
    } catch {
      // Keep generic error
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // System
  getHealth: () => fetchJSON('/api/v1/system/health'),
  triggerIngest: (maxConsumers = 16, readings = 720) =>
    fetchJSON(`/api/v1/system/ingest/dataset?max_consumers=${maxConsumers}&readings_per_consumer=${readings}`, {
      method: 'POST',
    }),

  // Detection & Baselining
  evaluateConsumer: (consumerId, params = {}) =>
    fetchJSON(`/api/v1/detection/evaluate/consumer/${consumerId}`, {
      method: 'POST',
      body: JSON.stringify(params),
    }),
  getConsumerBaseline: (consumerId) =>
    fetchJSON(`/api/v1/detection/baseline/${consumerId}`),
  getConsumerChangepoints: (consumerId) =>
    fetchJSON(`/api/v1/detection/changepoints/${consumerId}`),
  runBatchScoring: (params = {}) =>
    fetchJSON('/api/v1/detection/batch-run', {
      method: 'POST',
      body: JSON.stringify(params),
    }),

  // Alerts & Explainability
  getAlerts: (params = {}) => {
    const query = new URLSearchParams();
    if (params.risk_level) query.append('risk_level', params.risk_level);
    if (params.tariff_class) query.append('tariff_class', params.tariff_class);
    if (params.feeder_id) query.append('feeder_id', params.feeder_id);
    if (params.status) query.append('status', params.status);
    if (params.page) query.append('page', params.page);
    if (params.page_size) query.append('page_size', params.page_size);
    const qs = query.toString();
    return fetchJSON(`/api/v1/alerts/${qs ? `?${qs}` : ''}`);
  },
  getAlertEvidence: (alertId) =>
    fetchJSON(`/api/v1/alerts/${alertId}/evidence`),

  // Prioritization & Capacity Control
  getManifest: (limit = 20, tariffClass = null, feederId = null) => {
    const query = new URLSearchParams({ limit: String(limit) });
    if (tariffClass) query.append('tariff_class', tariffClass);
    if (feederId) query.append('feeder_id', feederId);
    return fetchJSON(`/api/v1/prioritization/manifest?${query.toString()}`);
  },
  adjustWeights: (weights) =>
    fetchJSON('/api/v1/prioritization/adjust-weights', {
      method: 'POST',
      body: JSON.stringify(weights),
    }),

  // Geospatial & Fleet Logistics
  getHotspots: (epsKm = 2.5, minSamples = 2) =>
    fetchJSON(`/api/v1/geospatial/hotspots?eps_km=${epsKm}&min_samples=${minSamples}`),
  optimizeRoute: (startLat, startLon, alertIds) =>
    fetchJSON('/api/v1/geospatial/route-optimize', {
      method: 'POST',
      body: JSON.stringify({
        inspector_start_latitude: startLat,
        inspector_start_longitude: startLon,
        alert_ids: alertIds,
      }),
    }),
  getFeederVulnerability: () =>
    fetchJSON('/api/v1/geospatial/feeder-vulnerability'),

  // Field Operations & Dispute Dossiers
  submitInspection: (data) =>
    fetchJSON('/api/v1/field/inspections/submit', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  uploadEvidence: (inspectionId, formData) =>
    fetchJSON(`/api/v1/field/inspections/${inspectionId}/evidence-upload`, {
      method: 'POST',
      body: formData,
    }),
  getDisputeDossier: (consumerId) =>
    fetchJSON(`/api/v1/field/dispute-dossier/${consumerId}`),

  // Model Governance & Active Learning
  triggerRetrain: () =>
    fetchJSON('/api/v1/governance/model/retrain', {
      method: 'POST',
    }),
  getModelMetrics: () =>
    fetchJSON('/api/v1/governance/model/metrics'),
  submitWhistleblowerTip: (tip) =>
    fetchJSON('/api/v1/governance/whistleblower-tip', {
      method: 'POST',
      body: JSON.stringify(tip),
    }),
};
