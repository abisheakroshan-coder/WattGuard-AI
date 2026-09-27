---
name: Enterprise Industrial Utility Cockpit
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e18'
  surface-container-low: '#171b26'
  surface-container: '#1c1f2a'
  surface-container-high: '#262a35'
  surface-container-highest: '#313540'
  on-surface: '#dfe2f1'
  on-surface-variant: '#c2c6d6'
  inverse-surface: '#dfe2f1'
  inverse-on-surface: '#2c303b'
  outline: '#8c909f'
  outline-variant: '#424754'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e6a'
  primary-container: '#4d8eff'
  on-primary-container: '#00285d'
  inverse-primary: '#005ac2'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#ca8100'
  on-tertiary-container: '#3e2400'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0f131d'
  on-background: '#dfe2f1'
  surface-variant: '#313540'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  metric-lg:
    fontFamily: JetBrains Mono
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.03em
  metric-md:
    fontFamily: JetBrains Mono
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  metric-sm:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.05em
spacing:
  gutter: 0.75rem
  margin: 1rem
  space-xs: 0.125rem
  space-sm: 0.25rem
  space-md: 0.5rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style

This design system is engineered for high-stakes enterprise industrial utility cockpits. It targets operations engineers, grid controllers, and industrial supervisors who require instantaneous situational awareness and zero ambiguity. The emotional response is one of absolute control, precision, precision-engineered reliability, and calm authority under pressure.

We employ a High-Contrast Technical style that merges deep, light-absorbing dark surfaces with hyper-vibrant status metrics. Information density is optimized for multi-monitor command centers, ensuring critical anomalies cut through visual fatigue immediately.

## Colors

The color architecture is built around an obsidian foundation, utilizing precise tonal variations to segment complex telemetry dashboards without relying on heavy lines.

- **Background:** `#0B0F19` (Deep Slate Base)
- **Surfaces:** `#111827` (Elevated Card Surface)
- **Borders / Dividers:** `#1F2937` (Subtle Structural Frame)
- **Electric Blue (`#3B82F6`):** Primary interactive states, active pathways, and systemic telemetry.
- **Low Risk (`#10B981`):** Nominal operations, secure valves, stable output.
- **Medium Risk (`#F59E0B`):** Warning thresholds, approaching nominal limits.
- **High Risk (`#F97316`):** Severe variance, mandatory operator acknowledgement.
- **Critical Risk (`#EF4444`):** Emergency override, system failure, immediate shutdown protocols.

## Typography

The typography system strictly separates conversational UI text from machine metrics. **Inter** handles all interface labels, system navigation, and operational logs with clinical neutrality. **JetBrains Mono** is reserved exclusively for numerical data, timestamps, telemetry streams, and gauge readouts to guarantee tabular alignment across high-frequency updates. 

Font sizes are tightly clamped to maximize screen real estate. Large scales (>32px) use mobile-adjusted equivalents when scaling down to portable diagnostic tablets.

## Layout & Spacing

A high-density **fluid grid** system is utilized to accommodate expansive SCADA schemas and multi-pane telemetry monitors. 

- **Grid Architecture:** 24-column fluid grid allowing ultra-precise widget allocation for complex piping and electrical schematics.
- **Gutters & Margins:** Tight 12px (`0.75rem`) gutters maintain structural separation without wasting canvas space. Outer margins lock at 16px (`1rem`).
- **Responsive Behavior:** 
  - **Desktop (1440px+):** Full 24-column multi-pane cockpit view with persistent side telemetry.
  - **Tablet (768px - 1439px):** Collapsible panel layout, maintaining fixed metric rows.
  - **Mobile (<768px):** Single-column stacked telemetry feeds with priority-sorted risk indicators.

## Elevation & Depth

Depth is conveyed through a **low-contrast outline and tonal layering** system. Drop shadows are entirely omitted to prevent visual noise in high-density environments. 

Hierarchy is established strictly through surface luminance stepping (moving from `#0B0F19` base up to `#111827` cards) bound by crisp, 1px structural borders (`#1F2937`). Active or alarmed states breach this neutral boundary using high-intensity neon glows derived from the risk-level palette (e.g., a 1px border shift to `#EF4444` with a subtle corresponding ambient box-shadow blur for critical alerts).

## Shapes

The design system employs **Sharp (`0`)** corner geometry. 

All UI elements, cards, inputs, and modal containers feature strictly 0px border radii. This industrial precision aesthetic reinforces structural rigidity, eliminates wasted pixel footprints, and aligns seamlessly with technical schematics, CAD readouts, and engineering blueprints.

## Components

- **Buttons:** Sharp-edged structural blocks with high-contrast text. Primary actions use Electric Blue (`#3B82F6`); destructive or emergency overrides use Critical Red (`#EF4444`). Hover states invert or brighten luminance by 15% instantly without transition lag.
- **Chips & Badges:** Monospaced uppercase text enclosed in a 1px solid border matching the respective risk level color (e.g., Low Risk uses `#10B981` border with a 10% opacity background tint).
- **Lists & Tables:** Dense data tables featuring alternating row shading, sticky headers, and JetBrains Mono numerical alignment. Row heights are constrained to 28px for maximum telemetry visibility.
- **Checkboxes & Radio Buttons:** Hard-angled square and diamond geometries. Unchecked states feature `#1F2937` borders; active states fill completely with Electric Blue or the designated risk accent.
- **Input Fields:** Flush rectangular inputs with `#111827` backgrounds and `#1F2937` borders, shifting to `#3B82F6` upon focus. Placeholder text uses muted slate for clear legibility.
- **Cards:** Bordered structural containers (`#111827` fill, `#1F2937` border) housing isolated telemetry widgets, control valves, or system logs.
- **Specialized Components:** 
  - *Telemetry Gauges:* Circular and linear progress meters utilizing the full risk-spectrum gradient.
  - *Emergency Kill Switches:* Oversized, high-visibility tactile action blocks requiring a dual-step confirmation pattern.
  - *Live Feed Tickers:* Monospaced scrolling event logs with timestamp prefixes.