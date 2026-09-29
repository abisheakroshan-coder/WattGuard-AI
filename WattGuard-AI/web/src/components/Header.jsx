import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Activity,
  Radio,
  Users,
  Search,
  ClipboardList,
  Wrench,
  BarChart3,
  Play,
  CheckCircle2,
  Cpu,
  RefreshCw,
} from 'lucide-react';
import { api } from '../services/api';

export default function Header({ activeTab, onTabChange, selectedConsumerId, onTriggerBatch }) {
  const [timeStr, setTimeStr] = useState('');
  const [health, setHealth] = useState(null);
  const [isScoring, setIsScoring] = useState(false);

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      setTimeStr(
        now.toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
      );
    };
    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchHealth = async () => {
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch (err) {
      console.error('Failed to fetch system health:', err);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRunBatch = async () => {
    setIsScoring(true);
    try {
      if (onTriggerBatch) {
        await onTriggerBatch();
      } else {
        await api.runBatchScoring({ limit: 50 });
      }
      await fetchHealth();
    } catch (err) {
      console.error('Batch scoring run failed:', err);
    } finally {
      setIsScoring(false);
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Control Centre', icon: Activity },
    { id: 'alerts', label: 'Live Alerts', icon: Radio },
    { id: 'consumers', label: 'Consumer Directory', icon: Users },
    {
      id: 'consumer-detail',
      label: selectedConsumerId ? `Telemetry: ${selectedConsumerId}` : 'Consumer Detail',
      icon: Search,
    },
    { id: 'queue', label: 'Inspection Queue', icon: ClipboardList },
    { id: 'field-ops', label: 'Field Audits', icon: Wrench },
    { id: 'analytics', label: 'Model Governance', icon: BarChart3 },
  ];

  return (
    <header
      style={{
        background: 'var(--bg-panel)',
        borderBottom: '1px solid var(--border-subtle)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      {/* Top SCADA Telemetry Ticker */}
      <div
        style={{
          padding: '6px 20px',
          background: 'rgba(7, 11, 18, 0.95)',
          borderBottom: '1px solid rgba(30, 41, 59, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.6875rem',
          letterSpacing: '0.04em',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span
              className={`led-indicator ${
                health?.status === 'HEALTHY' ? 'led-green' : health ? 'led-amber' : 'led-red'
              }`}
            ></span>
            <span style={{ fontWeight: 700, color: 'var(--text-muted)' }}>
              SYSTEM: {health?.status || 'CONNECTING...'}
            </span>
          </div>

          <span style={{ color: 'var(--border-strong)' }}>|</span>

          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Cpu size={12} style={{ color: 'var(--cyan-telemetry)' }} />
            <span style={{ color: 'var(--text-dim)' }}>
              CORE: <span className="font-mono" style={{ color: 'var(--text-main)' }}>RF + IF DUAL ENGINE</span>
            </span>
          </div>

          <span style={{ color: 'var(--border-strong)' }}>|</span>

          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ color: 'var(--text-dim)' }}>WEIGHTS:</span>
            <span className="font-mono" style={{ color: 'var(--cyan-telemetry)' }}>
              w1={health?.operational_weights?.w1_risk ?? 0.35} w2={health?.operational_weights?.w2_anomaly ?? 0.25} w3={health?.operational_weights?.w3_loss ?? 0.25} w4={health?.operational_weights?.w4_confidence ?? 0.15}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <span className="font-mono" style={{ color: 'var(--text-muted)' }}>
            {timeStr}
          </span>
          <span style={{ color: 'var(--border-strong)' }}>|</span>
          <span style={{ color: 'var(--text-dim)' }}>
            API: <span className="font-mono" style={{ color: 'var(--green-nominal)' }}>127.0.0.1:8001</span>
          </span>
        </div>
      </div>

      {/* Main Navigation & Action Bar */}
      <div
        style={{
          padding: '10px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 12,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              cursor: 'pointer',
            }}
            onClick={() => onTabChange('dashboard')}
          >
            <div
              style={{
                width: 28,
                height: 28,
                background: 'rgba(2, 132, 199, 0.2)',
                border: '1px solid var(--border-accent)',
                borderRadius: 4,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <ShieldAlert size={18} style={{ color: 'var(--cyan-telemetry)' }} />
            </div>
            <div>
              <div
                style={{
                  fontSize: '0.875rem',
                  fontWeight: 800,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  color: 'var(--text-bright)',
                }}
              >
                WattGuard <span style={{ color: 'var(--cyan-telemetry)' }}>AI</span>
              </div>
              <div
                style={{
                  fontSize: '0.625rem',
                  letterSpacing: '0.06em',
                  color: 'var(--text-dim)',
                  textTransform: 'uppercase',
                }}
              >
                Revenue Protection SCADA
              </div>
            </div>
          </div>

          <div
            style={{
              height: 24,
              width: 1,
              background: 'var(--border-subtle)',
              margin: '0 6px',
            }}
          />

          {/* Navigation Tabs */}
          <nav style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '7px 12px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em',
                    background: isActive ? 'rgba(2, 132, 199, 0.15)' : 'transparent',
                    border: `1px solid ${isActive ? 'var(--border-accent)' : 'transparent'}`,
                    borderRadius: 3,
                    color: isActive ? 'var(--cyan-telemetry)' : 'var(--text-muted)',
                    cursor: 'pointer',
                    transition: 'all 0.12s ease',
                  }}
                >
                  <Icon size={14} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Global Control Centre Action */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button
            onClick={handleRunBatch}
            disabled={isScoring}
            className="btn-industrial btn-primary"
            style={{
              boxShadow: '0 0 10px rgba(2, 132, 199, 0.3)',
            }}
          >
            {isScoring ? (
              <>
                <RefreshCw size={13} className="animate-spin" />
                <span>Running Batch Scoring...</span>
              </>
            ) : (
              <>
                <Play size={13} />
                <span>Run Batch Scoring</span>
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
