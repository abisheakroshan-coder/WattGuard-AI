import React from 'react';

export default function MetricCard({
  title,
  value,
  unit = '',
  status = 'nominal', // 'nominal', 'critical', 'caution', 'cyan', 'muted'
  subtext,
  icon: Icon,
  trend,
  className = '',
}) {
  const getStatusBorder = () => {
    switch (status) {
      case 'critical':
        return 'border-l-4 border-l-red-500';
      case 'caution':
        return 'border-l-4 border-l-amber-500';
      case 'cyan':
        return 'border-l-4 border-l-cyan-500';
      case 'nominal':
        return 'border-l-4 border-l-emerald-500';
      default:
        return 'border-l-4 border-l-slate-600';
    }
  };

  const getLedClass = () => {
    switch (status) {
      case 'critical':
        return 'led-red';
      case 'caution':
        return 'led-amber';
      case 'cyan':
        return 'led-cyan';
      default:
        return 'led-green';
    }
  };

  const getValueColor = () => {
    switch (status) {
      case 'critical':
        return 'text-red-400';
      case 'caution':
        return 'text-amber-400';
      case 'cyan':
        return 'text-cyan-400';
      default:
        return 'text-slate-100';
    }
  };

  return (
    <div
      className={`control-card ${className}`}
      style={{
        padding: '14px 16px',
        borderLeft: `3px solid ${
          status === 'critical'
            ? 'var(--red-critical)'
            : status === 'caution'
            ? 'var(--amber-caution)'
            : status === 'cyan'
            ? 'var(--cyan-telemetry)'
            : 'var(--green-nominal)'
        }`,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className={`led-indicator ${getLedClass()}`}></span>
          <span
            style={{
              fontSize: '0.6875rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              color: 'var(--text-muted)',
            }}
          >
            {title}
          </span>
        </div>
        {Icon && <Icon size={16} style={{ color: 'var(--text-dim)' }} />}
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 4 }}>
        <span
          className="font-mono"
          style={{
            fontSize: '1.625rem',
            fontWeight: 800,
            color:
              status === 'critical'
                ? '#FCA5A5'
                : status === 'caution'
                ? '#FCD34D'
                : status === 'cyan'
                ? '#67E8F9'
                : '#F8FAFC',
          }}
        >
          {value}
        </span>
        {unit && (
          <span className="font-mono" style={{ fontSize: '0.8125rem', color: 'var(--text-dim)', fontWeight: 600 }}>
            {unit}
          </span>
        )}
      </div>

      {(subtext || trend) && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.6875rem' }}>
          <span style={{ color: 'var(--text-dim)' }}>{subtext}</span>
          {trend && (
            <span
              className="font-mono"
              style={{
                color: trend.isPositive ? 'var(--green-nominal)' : 'var(--red-critical)',
                fontWeight: 600,
              }}
            >
              {trend.text}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
