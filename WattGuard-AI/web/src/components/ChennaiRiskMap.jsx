import React, { useState, useMemo, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  MapPin, Shield, AlertTriangle, Eye, Search, Filter,
  Users, CheckCircle2, ChevronRight, X, Radio, User
} from 'lucide-react';
import {
  formatINR,
  formatActionLabel,
  formatRiskTierLabel,
  getConsumerUnitBreakdown,
  TAMIL_NADU_CONSUMER_DIRECTORY,
  SHOWCASE_SCENARIO,
  SYNTHETIC_DEMO_SCENARIOS,
  DEMO_CONSUMER_META,
  getConsumerMetadata
} from '../App';
import {
  CHENNAI_CENTER,
  CHENNAI_NEIGHBORHOOD_COORDS,
  getConsumerChennaiCoords,
  getMarkerCategory,
  getInspectionTeamEntities
} from '../services/chennaiLocations';

/**
 * Standard Chennai distribution areas for neutral filter selection.
 */
const CHENNAI_DISTRIBUTION_AREAS = [
  'T. Nagar',
  'Anna Nagar',
  'Nungambakkam',
  'Kodambakkam',
  'Adyar',
  'Velachery',
  'Guindy',
  'Mylapore',
  'Saidapet',
  'Perungudi',
  'Thoraipakkam',
  'Pallavaram',
  'Chromepet',
  'Tambaram'
];

/**
 * Imperative map controller to pan/zoom and handle container resize / tab activation.
 */
function MapViewHandler({ center, zoom }) {
  const map = useMap();
  const isFirstMount = useRef(true);

  // Invalidate map size on mount, container resize, and tab visibility change
  useEffect(() => {
    const container = map.getContainer();
    if (!container) return;

    map.invalidateSize();
    const rafId = requestAnimationFrame(() => {
      map.invalidateSize();
    });
    const timer1 = setTimeout(() => {
      map.invalidateSize();
    }, 100);
    const timer2 = setTimeout(() => {
      map.invalidateSize();
    }, 300);

    const handleResize = () => {
      map.invalidateSize();
    };
    window.addEventListener('resize', handleResize);

    let resizeObserver;
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => {
        map.invalidateSize();
      });
      resizeObserver.observe(container);
    }

    return () => {
      cancelAnimationFrame(rafId);
      clearTimeout(timer1);
      clearTimeout(timer2);
      window.removeEventListener('resize', handleResize);
      if (resizeObserver) resizeObserver.disconnect();
    };
  }, [map]);

  useEffect(() => {
    if (isFirstMount.current) {
      isFirstMount.current = false;
      return;
    }
    if (center && Array.isArray(center) && center.length === 2 && !isNaN(center[0]) && !isNaN(center[1])) {
      const current = map.getCenter();
      if (Math.abs(current.lat - center[0]) > 0.0001 || Math.abs(current.lng - center[1]) > 0.0001 || map.getZoom() !== zoom) {
        map.flyTo(center, zoom || 12, {
          duration: 0.6,
          easeLinearity: 0.25
        });
      }
    }
  }, [center, zoom, map]);

  return null;
}

/**
 * Creates clean HTML divIcon for consumer markers.
 */
function createConsumerDivIcon(category) {
  let mainColor = '#0284c7'; // Moderate
  let label = 'M';

  if (category === 'Critical / Inspect Now') {
    mainColor = '#dc2626'; // Critical
    label = '!';
  } else if (category === 'High Priority') {
    mainColor = '#d97706'; // High
    label = 'H';
  }

  const baseSize = 26;
  const borderWidth = 2;

  const html = `
    <div style="position: relative; width: ${baseSize}px; height: ${baseSize}px; display: flex; align-items: center; justify-content: center; cursor: pointer;">
      <div style="
        width: ${baseSize}px;
        height: ${baseSize}px;
        border-radius: 9999px;
        background: #111827;
        border: ${borderWidth}px solid ${mainColor};
        display: flex;
        align-items: center;
        justify-content: center;
        color: ${mainColor};
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 11px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.5);
      ">
        ${label}
      </div>
    </div>
  `;

  return L.divIcon({
    className: 'custom-div-icon',
    html,
    iconSize: [baseSize, baseSize],
    iconAnchor: [baseSize / 2, baseSize / 2],
    popupAnchor: [0, -baseSize / 2 - 4]
  });
}

/**
 * Creates clean HTML divIcon for inspection teams.
 */
function createTeamDivIcon(status, isHighlighted = false) {
  const mainColor = '#7c3aed'; // Purple
  const baseSize = isHighlighted ? 32 : 24;

  const html = `
    <div style="position: relative; width: ${baseSize}px; height: ${baseSize}px; display: flex; align-items: center; justify-content: center; cursor: pointer;">
      ${isHighlighted ? `<div style="position: absolute; inset: -3px; border-radius: 6px; border: 2px solid ${mainColor}; opacity: 0.8;"></div>` : ''}
      <div style="
        width: ${baseSize}px;
        height: ${baseSize}px;
        border-radius: 6px;
        background: #1e1b4b;
        border: 2px solid ${mainColor};
        display: flex;
        align-items: center;
        justify-content: center;
        color: #e9d5ff;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4);
      ">
        T
      </div>
    </div>
  `;

  return L.divIcon({
    className: 'custom-team-icon',
    html,
    iconSize: [baseSize, baseSize],
    iconAnchor: [baseSize / 2, baseSize / 2],
    popupAnchor: [0, -baseSize / 2 - 4]
  });
}

const consumerIconCache = {};
function getConsumerIcon(category) {
  if (!consumerIconCache[category]) {
    consumerIconCache[category] = createConsumerDivIcon(category);
  }
  return consumerIconCache[category];
}

export default function ChennaiRiskMap({
  anomalies = [],
  selectedAnomaly = null,
  unitRate = 8.0,
  onSelectConsumer,
  queueData = []
}) {
  const [filterType, setFilterType] = useState('ALL'); // 'ALL' | 'CRITICAL' | 'HIGH' | 'TEAMS'
  const [selectedArea, setSelectedArea] = useState('ALL_AREAS');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedConsumerId, setSelectedConsumerId] = useState(selectedAnomaly?.consumer_id || null);
  const [mapCenter, setMapCenter] = useState(CHENNAI_CENTER);
  const [mapZoom, setMapZoom] = useState(12);

  const markerRefs = useRef({});

  // 1. Prepare comprehensive enriched consumers with Chennai coordinates across all WattGuard sources
  const mappedConsumers = useMemo(() => {
    const consumerMap = new Map();

    // A. Priority 1: Active detected anomalies & imported consumers
    (anomalies || []).forEach((item) => {
      if (!item || !item.consumer_id) return;
      const coords = getConsumerChennaiCoords(item);
      const category = getMarkerCategory(item);
      const revLoss = (item.estimated_unbilled_kwh || 0) * unitRate;
      consumerMap.set(item.consumer_id, {
        ...item,
        computedCoords: coords,
        markerCategory: category,
        computedRevLoss: revLoss
      });
    });

    // B. Priority 2: Core Tamil Nadu Consumer Directory
    Object.entries(TAMIL_NADU_CONSUMER_DIRECTORY || {}).forEach(([cid, meta]) => {
      if (!consumerMap.has(cid)) {
        const fallbackRisk = 0.68;
        const tempObj = {
          alert_id: `DIR-${cid}`,
          consumer_id: cid,
          consumer_name: meta.name,
          area: meta.area,
          street: meta.street,
          tariff_class: meta.category?.includes('Residential') ? 'RESIDENTIAL' : 'COMMERCIAL',
          risk_score: fallbackRisk,
          composite_priority: fallbackRisk * 100,
          risk_tier: fallbackRisk >= 0.85 ? 'CRITICAL' : (fallbackRisk >= 0.70 ? 'HIGH' : 'MEDIUM'),
          estimated_unbilled_kwh: 1450,
          status: 'ACTIVE',
          recommended_action: 'SCHEDULED_INSPECTION',
          tamper_type: 'Telemetry Deviation',
          explanations: ['Historical load factor inconsistency monitored by distribution grid.']
        };
        const coords = getConsumerChennaiCoords(tempObj);
        const category = getMarkerCategory(tempObj);
        consumerMap.set(cid, {
          ...tempObj,
          computedCoords: coords,
          markerCategory: category,
          computedRevLoss: 1450 * unitRate
        });
      } else {
        const existing = consumerMap.get(cid);
        if (!existing.consumer_name && meta.name) existing.consumer_name = meta.name;
        if (!existing.area && meta.area) existing.area = meta.area;
        if (!existing.street && meta.street) existing.street = meta.street;
      }
    });

    // C. Priority 3: Synthetic Demo Scenarios (Showcase + 20 cases)
    const allScenarios = [SHOWCASE_SCENARIO, ...(SYNTHETIC_DEMO_SCENARIOS || [])];
    allScenarios.forEach((sc) => {
      if (!sc) return;
      const meta = (DEMO_CONSUMER_META && DEMO_CONSUMER_META[sc.id]) || {
        name: sc.consumer_label || `Demo Account #${sc.scenario_number}`,
        id: `WG-C${(sc.scenario_number || 0).toString().padStart(3, '0')}`,
        area: 'Chennai Circle',
        theft_type: sc.theft_type || sc.title,
        risk_score_display: `${Math.round((sc.risk_score || 0.8) * 100)}/100`
      };
      const cid = meta.id;
      if (!consumerMap.has(cid)) {
        const unbilled = sc.estimated_unbilled_kwh || 0;
        const loss = sc.potential_revenue_loss || (unbilled * unitRate);
        const risk = sc.risk_score || 0.8;
        const tier = sc.risk_level === 'Critical' ? 'CRITICAL' : (sc.risk_level === 'High' ? 'HIGH' : 'MEDIUM');
        const street = meta.street || (getConsumerMetadata ? getConsumerMetadata(cid).street : 'Main Road');
        const tempObj = {
          alert_id: `DEMO-${cid}`,
          consumer_id: cid,
          consumer_name: meta.name,
          area: meta.area,
          street: street,
          tariff_class: sc.tariff_class || 'COMMERCIAL',
          risk_score: risk,
          composite_priority: risk * 100,
          risk_tier: tier,
          estimated_unbilled_kwh: unbilled,
          status: 'ACTIVE',
          recommended_action: sc.recommended_action || (tier === 'CRITICAL' ? 'IMMEDIATE_RAID' : 'SCHEDULED_INSPECTION'),
          tamper_type: sc.theft_type || sc.title,
          explanations: [sc.why_flagged || sc.what_happened || 'Investigative scenario flagged by multi-engine ensemble.'],
          energy_curve: sc.curve_data ? sc.curve_data.map(d => ({ hour: d.t, baseline: d.exp, metered: d.act })) : []
        };
        const coords = getConsumerChennaiCoords(tempObj);
        const category = getMarkerCategory(tempObj);
        consumerMap.set(cid, {
          ...tempObj,
          computedCoords: coords,
          markerCategory: category,
          computedRevLoss: loss
        });
      }
    });

    // D. Priority 4: Platform Consumer Pool (ensuring all standard consumers are accounted for)
    const extraConsumers = ['CONS_RES_006', 'CONS_RES_007', 'CONS_RES_008', 'CONS_COM_008', 'CONS_COM_010', 'CONS_COM_014', 'CONS_RES_012', 'CONS_COM_016'];
    extraConsumers.forEach((cid) => {
      if (!consumerMap.has(cid)) {
        const meta = getConsumerMetadata ? getConsumerMetadata(cid) : { name: cid, street: 'Main Road', area: 'Chennai' };
        const fallbackRisk = 0.58;
        const tempObj = {
          alert_id: `POOL-${cid}`,
          consumer_id: cid,
          consumer_name: meta.name,
          area: meta.area,
          street: meta.street,
          tariff_class: cid.startsWith('CONS_RES') ? 'RESIDENTIAL' : 'COMMERCIAL',
          risk_score: fallbackRisk,
          composite_priority: fallbackRisk * 100,
          risk_tier: 'MEDIUM',
          estimated_unbilled_kwh: 850,
          status: 'ACTIVE',
          recommended_action: 'METER_CALIBRATION_TEST',
          tamper_type: 'Load Variance',
          explanations: ['Substation secondary feeder audit anomaly.']
        };
        const coords = getConsumerChennaiCoords(tempObj);
        const category = getMarkerCategory(tempObj);
        consumerMap.set(cid, {
          ...tempObj,
          computedCoords: coords,
          markerCategory: category,
          computedRevLoss: 850 * unitRate
        });
      }
    });

    return Array.from(consumerMap.values());
  }, [anomalies, unitRate]);

  // 2. Prepare Inspection Teams
  const inspectionTeams = useMemo(() => {
    return getInspectionTeamEntities(queueData, anomalies);
  }, [queueData, anomalies]);

  // Unique areas list for area filter (ensuring standard Chennai areas are always included)
  const uniqueAreas = useMemo(() => {
    const list = [...CHENNAI_DISTRIBUTION_AREAS];
    const clean = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
    mappedConsumers.forEach(c => {
      if (c.area && !list.some(a => clean(a) === clean(c.area))) {
        list.push(c.area.trim());
      }
    });
    return list;
  }, [mappedConsumers]);

  // Filtered consumers based on active filter pills & search
  const visibleConsumers = useMemo(() => {
    if (filterType === 'TEAMS') return [];
    const clean = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');

    return mappedConsumers.filter((c) => {
      if (filterType === 'CRITICAL' && c.markerCategory !== 'Critical / Inspect Now') {
        return false;
      }
      if (filterType === 'HIGH' && c.markerCategory !== 'High Priority' && c.markerCategory !== 'Critical / Inspect Now') {
        return false;
      }

      if (selectedArea !== 'ALL_AREAS') {
        if (clean(c.area) !== clean(selectedArea)) {
          return false;
        }
      }

      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const name = (c.consumer_name || '').toLowerCase();
        const cid = (c.consumer_id || '').toLowerCase();
        const area = (c.area || '').toLowerCase();
        const street = (c.street || '').toLowerCase();
        if (!name.includes(q) && !cid.includes(q) && !area.includes(q) && !street.includes(q)) {
          return false;
        }
      }

      return true;
    });
  }, [mappedConsumers, filterType, selectedArea, searchQuery]);

  // Filtered teams based on active filter
  const visibleTeams = useMemo(() => {
    if (filterType === 'CRITICAL' || filterType === 'HIGH') return [];
    return inspectionTeams;
  }, [inspectionTeams, filterType]);

  const handleSelectFromList = (consumer) => {
    setSelectedConsumerId(consumer.consumer_id);
    setMapCenter(consumer.computedCoords);
    setMapZoom(15);
    setTimeout(() => {
      const marker = markerRefs.current[consumer.consumer_id];
      if (marker && marker.openPopup) {
        marker.openPopup();
      }
    }, 450);
  };

  // Synchronize CSS highlighted class on marker DOM elements to avoid unbinding popups
  useEffect(() => {
    Object.values(markerRefs.current).forEach((m) => {
      const el = m?.getElement?.();
      if (el) {
        el.classList.remove('marker-highlighted');
      }
    });

    if (selectedConsumerId && markerRefs.current[selectedConsumerId]) {
      const m = markerRefs.current[selectedConsumerId];
      const el = m?.getElement?.();
      if (el) {
        el.classList.add('marker-highlighted');
      }
    }
  }, [selectedConsumerId]);

  useEffect(() => {
    if (selectedAnomaly && selectedAnomaly.consumer_id) {
      const match = mappedConsumers.find(c => c.consumer_id === selectedAnomaly.consumer_id);
      if (match) {
        handleSelectFromList(match);
      }
    }
  }, [selectedAnomaly]);

  const criticalCount = useMemo(() => mappedConsumers.filter(c => c.markerCategory === 'Critical / Inspect Now').length, [mappedConsumers]);
  const highRiskCount = useMemo(() => mappedConsumers.filter(c => c.markerCategory === 'High Priority' || c.markerCategory === 'Critical / Inspect Now').length, [mappedConsumers]);

  return (
    <div className="space-y-4">
      {/* Clean Header & Risk Filter Bar */}
      <div className="p-3.5 rounded-lg bg-[#111827] border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <MapPin className="w-5 h-5 text-sky-400 shrink-0" />
          <div>
            <h2 className="text-base font-semibold text-slate-100 font-sans leading-none">
              Chennai Risk Map
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Geographic overview of monitored meters and field teams
            </p>
          </div>
        </div>

        {/* Clean Risk Filters */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <button
            onClick={() => setFilterType('ALL')}
            className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
              filterType === 'ALL'
                ? 'bg-sky-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            All ({mappedConsumers.length})
          </button>

          <button
            onClick={() => setFilterType('CRITICAL')}
            className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
              filterType === 'CRITICAL'
                ? 'bg-red-600 text-white'
                : 'bg-slate-800 text-red-300 hover:bg-red-950/40'
            }`}
          >
            Critical ({criticalCount})
          </button>

          <button
            onClick={() => setFilterType('HIGH')}
            className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
              filterType === 'HIGH'
                ? 'bg-amber-600 text-white'
                : 'bg-slate-800 text-amber-300 hover:bg-amber-950/40'
            }`}
          >
            High Risk ({highRiskCount})
          </button>

          <button
            onClick={() => setFilterType('TEAMS')}
            className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
              filterType === 'TEAMS'
                ? 'bg-purple-600 text-white'
                : 'bg-slate-800 text-purple-300 hover:bg-purple-950/40'
            }`}
          >
            Teams ({inspectionTeams.length})
          </button>
        </div>
      </div>

      {/* Main Map Workspace: Sidebar + Map */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        {/* Left Side: Clean Consumer List Sidebar */}
        <div className="lg:col-span-4 rounded-lg bg-[#111827] border border-slate-800 overflow-hidden flex flex-col h-[620px]">
          {/* Filter Bar */}
          <div className="p-2.5 border-b border-slate-800 bg-slate-900 space-y-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search consumer, ID, or area..."
                className="w-full pl-8 pr-7 py-1.5 rounded-md bg-slate-950 border border-slate-700 text-xs text-slate-100 placeholder-slate-400 focus:outline-none focus:border-sky-500 transition-colors"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
              <div className="flex flex-wrap items-center gap-2">
                <div className="flex items-center gap-1.5">
                  <Filter className="w-3 h-3 text-slate-400" />
                  <span>Area:</span>
                  <select
                    value={selectedArea}
                    onChange={(e) => {
                      const newArea = e.target.value;
                      setSelectedArea(newArea);
                      if (newArea === 'ALL_AREAS') {
                        setMapCenter(CHENNAI_CENTER);
                        setMapZoom(12);
                      } else {
                        const areaCoords = CHENNAI_NEIGHBORHOOD_COORDS[newArea]?.base;
                        if (areaCoords) {
                          setMapCenter(areaCoords);
                          setMapZoom(14);
                        }
                      }
                    }}
                    className="bg-slate-950 border border-slate-700 rounded px-1.5 py-0.5 text-slate-200 focus:outline-none focus:border-sky-500 text-xs"
                  >
                    <option value="ALL_AREAS">All Chennai Areas</option>
                    {uniqueAreas.map(a => (
                      <option key={a} value={a}>{a}</option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center gap-1.5">
                  <User className="w-3 h-3 text-slate-400" />
                  <span>Consumer:</span>
                  <select
                    value={selectedConsumerId || ''}
                    onChange={(e) => {
                      const cid = e.target.value;
                      if (!cid) {
                        setSelectedConsumerId(null);
                        if (selectedArea !== 'ALL_AREAS' && CHENNAI_NEIGHBORHOOD_COORDS[selectedArea]?.base) {
                          setMapCenter(CHENNAI_NEIGHBORHOOD_COORDS[selectedArea].base);
                          setMapZoom(14);
                        } else {
                          setMapCenter(CHENNAI_CENTER);
                          setMapZoom(12);
                        }
                      } else {
                        const match = mappedConsumers.find(c => c.consumer_id === cid);
                        if (match) {
                          handleSelectFromList(match);
                        }
                      }
                    }}
                    className="bg-slate-950 border border-slate-700 rounded px-1.5 py-0.5 text-slate-200 focus:outline-none focus:border-sky-500 text-xs max-w-[130px] truncate"
                  >
                    <option value="">Select Consumer</option>
                    {visibleConsumers.map(c => (
                      <option key={c.consumer_id} value={c.consumer_id}>
                        {c.consumer_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <span>
                Showing: <strong className="text-slate-200">{filterType === 'TEAMS' ? visibleTeams.length : visibleConsumers.length}</strong>
              </span>
            </div>
          </div>

          {/* Consumer Rows */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-800/80 p-2 space-y-1">
            {filterType === 'TEAMS' ? (
              visibleTeams.map((team, idx) => (
                <div
                  key={idx}
                  onClick={() => {
                    setMapCenter(team.coords);
                    setMapZoom(15);
                  }}
                  className="p-2.5 rounded-md border border-slate-800 bg-slate-900/60 hover:bg-slate-800/60 cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-purple-300 font-sans">{team.teamName}</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-purple-950 text-purple-200 border border-purple-800/40">
                      {team.status}
                    </span>
                  </div>
                  <div className="text-xs text-slate-300 mt-0.5 truncate">
                    {team.currentAreaStreet}
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    Target: <span className="text-slate-200">{team.assignedConsumer}</span>
                  </div>
                </div>
              ))
            ) : visibleConsumers.length === 0 ? (
              <div className="text-center py-16 text-slate-400 text-xs">
                No consumers match the filter criteria.
              </div>
            ) : (
              visibleConsumers.map((c) => {
                const isSelected = selectedConsumerId === c.consumer_id;
                const isCritical = c.markerCategory === 'Critical / Inspect Now';
                const isHigh = c.markerCategory === 'High Priority';

                return (
                  <div
                    key={c.consumer_id}
                    onClick={() => handleSelectFromList(c)}
                    className={`p-2.5 rounded-md border transition-colors cursor-pointer flex flex-col gap-1.5 ${
                      isSelected
                        ? 'bg-slate-800 border-sky-500'
                        : isCritical
                        ? 'bg-slate-900/70 border-red-900/30 hover:border-red-700/50'
                        : isHigh
                        ? 'bg-slate-900/70 border-amber-900/30 hover:border-amber-700/50'
                        : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="min-w-0">
                        <div className="text-xs font-semibold text-slate-100 truncate flex items-center gap-1.5 font-sans">
                          <span
                            className={`w-2 h-2 rounded-full shrink-0 ${
                              isCritical ? 'bg-red-500' : isHigh ? 'bg-amber-500' : 'bg-sky-500'
                            }`}
                          />
                          {c.consumer_name}
                        </div>
                        <div className="text-[11px] text-slate-400 truncate mt-0.5">
                          {c.area} &middot; <span className="font-mono text-slate-400">{c.consumer_id}</span>
                        </div>
                      </div>

                      <div className="text-right shrink-0">
                        <span className={`text-xs font-semibold block ${isCritical ? 'text-red-400' : 'text-amber-400'}`}>
                          {(c.risk_score * 100).toFixed(0)}%
                        </span>
                        <span className="text-[10px] text-slate-400 block">
                          {formatINR(c.computedRevLoss)}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Side: Leaflet Interactive Map View */}
        <div className="lg:col-span-8 rounded-lg bg-[#111827] border border-slate-800 overflow-hidden relative h-[620px] flex flex-col">
          <div className="w-full flex-1 h-[620px] min-h-[620px] relative z-0">
            <MapContainer
              center={CHENNAI_CENTER}
              zoom={mapZoom}
              scrollWheelZoom={true}
              style={{ width: '100%', height: '100%', minHeight: '620px', background: '#0b0f19' }}
            >
              <MapViewHandler
                center={mapCenter}
                zoom={mapZoom}
              />

              {/* Free OpenStreetMap Basemap */}
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                maxZoom={19}
              />

              {/* Render Consumer Markers */}
              {visibleConsumers.map((consumer) => {
                const icon = getConsumerIcon(consumer.markerCategory);
                const units = getConsumerUnitBreakdown(consumer);

                return (
                  <Marker
                    key={consumer.consumer_id}
                    position={consumer.computedCoords}
                    icon={icon}
                    ref={(el) => {
                      if (el) markerRefs.current[consumer.consumer_id] = el;
                    }}
                    eventHandlers={{
                      click: (e) => {
                        if (e.originalEvent) {
                          e.originalEvent.stopPropagation();
                        }
                        setSelectedConsumerId(consumer.consumer_id);
                        if (e.target && !e.target.isPopupOpen()) {
                          e.target.openPopup();
                        }
                      },
                      popupclose: () => {
                        setSelectedConsumerId((curr) => (curr === consumer.consumer_id ? null : curr));
                      }
                    }}
                  >
                    {/* Clean Comprehensive Popup on Click */}
                    <Popup className="wattguard-hud-popup" autoPan={true} autoPanPadding={[40, 40]}>
                      <div className="p-3.5 rounded-lg bg-[#111827] border border-slate-700 text-slate-200 font-sans shadow-xl min-w-[260px] max-w-[300px]">
                        <div className="flex items-start justify-between gap-2 border-b border-slate-800 pb-2 mb-2">
                          <div>
                            <div className="text-xs font-semibold text-slate-100">
                              {consumer.consumer_name}
                            </div>
                            <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                              {consumer.consumer_id}
                            </div>
                          </div>
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-medium border ${
                              consumer.markerCategory === 'Critical / Inspect Now'
                                ? 'bg-red-950 text-red-300 border-red-800'
                                : consumer.markerCategory === 'High Priority'
                                ? 'bg-amber-950 text-amber-300 border-amber-800'
                                : 'bg-sky-950 text-sky-300 border-sky-800'
                            }`}
                          >
                            {formatRiskTierLabel(consumer.risk_tier)}
                          </span>
                        </div>

                        <div className="text-xs text-slate-300 mb-2 truncate">
                          {consumer.street}, <strong className="text-slate-100">{consumer.area}</strong>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-xs mb-2">
                          <div className="p-1.5 rounded bg-slate-900 border border-slate-800">
                            <div className="text-slate-400 text-[10px]">Risk Score</div>
                            <div className={`text-sm font-semibold mt-0.5 ${consumer.markerCategory === 'Critical / Inspect Now' ? 'text-red-400' : 'text-amber-400'}`}>
                              {(consumer.risk_score * 100).toFixed(0)}%
                            </div>
                          </div>

                          <div className="p-1.5 rounded bg-slate-900 border border-slate-800">
                            <div className="text-slate-400 text-[10px]">Potential Loss</div>
                            <div className="text-xs font-semibold text-amber-300 mt-0.5">
                              {formatINR(consumer.computedRevLoss)}
                            </div>
                          </div>
                        </div>

                        {/* Electricity Units Accounting Breakdown */}
                        <div className="p-2 rounded bg-slate-900/90 border border-slate-800 space-y-1 mb-2.5 text-[11px]">
                          <div className="flex items-center justify-between text-slate-300">
                            <span>Consumed Units:</span>
                            <strong className="font-mono text-slate-100">{units.consumed.toLocaleString('en-IN')} Units</strong>
                          </div>
                          <div className="flex items-center justify-between text-slate-300">
                            <span>Billed Units:</span>
                            <strong className="font-mono text-slate-100">{units.billed.toLocaleString('en-IN')} Units</strong>
                          </div>
                          <div className="flex items-center justify-between text-red-400 pt-1 border-t border-slate-800 font-medium">
                            <span>Estimated Theft / Unbilled:</span>
                            <strong className="font-mono text-red-300">{units.unbilled.toLocaleString('en-IN')} Units</strong>
                          </div>
                        </div>

                        <div className="text-[11px] mb-2.5 bg-slate-950 p-1.5 rounded border border-slate-800">
                          <span className="text-slate-400">Action:</span>{' '}
                          <strong className="text-slate-200">
                            {formatActionLabel(consumer.recommended_action)}
                          </strong>
                        </div>

                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectConsumer(consumer);
                          }}
                          className="w-full py-1.5 rounded-md font-medium text-xs bg-sky-600 hover:bg-sky-700 text-white transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Consumer</span>
                        </button>
                      </div>
                    </Popup>
                  </Marker>
                );
              })}

              {/* Render Inspection Team Markers */}
              {visibleTeams.map((team, idx) => {
                const icon = createTeamDivIcon(team.status, false);

                return (
                  <Marker
                    key={idx}
                    position={team.coords}
                    icon={icon}
                    eventHandlers={{
                      click: (e) => {
                        e.target.openPopup();
                      }
                    }}
                  >
                    <Popup className="wattguard-hud-popup">
                      <div className="p-3 rounded-lg bg-[#111827] border border-purple-800/40 text-slate-200 font-sans shadow-xl min-w-[220px]">
                        <div className="flex items-center justify-between border-b border-purple-800/30 pb-1.5 mb-2">
                          <span className="text-xs font-semibold text-purple-300">
                            {team.teamName}
                          </span>
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-purple-950 text-purple-300 border border-purple-800/40">
                            {team.status}
                          </span>
                        </div>
                        <div className="space-y-1 text-xs">
                          <div>
                            <span className="text-slate-400">Location:</span> {team.currentAreaStreet}
                          </div>
                          <div>
                            <span className="text-slate-400">Target:</span> {team.assignedConsumer}
                          </div>
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                );
              })}
            </MapContainer>
          </div>

          {/* Discreet Bottom-Right Legend */}
          <div className="absolute bottom-2.5 right-2.5 z-[1000] px-2.5 py-1.5 rounded-md bg-[#111827]/90 border border-slate-700/80 backdrop-blur-sm flex items-center gap-3 text-[11px] font-sans pointer-events-none">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-red-600 inline-block" /> Critical
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" /> High
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-sky-600 inline-block" /> Moderate
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded bg-purple-600 inline-block" /> Squad
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
