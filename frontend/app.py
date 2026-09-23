
import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import re
import textwrap
from pathlib import Path
from datetime import datetime

# ============================================================
# WATTGUARD AI — CHENNAI DISTRIBUTION LOSS CONTROL CENTRE
# Full replacement frontend/app.py — Web deploy-ready V11
# ============================================================

st.set_page_config(
    page_title="WattGuard AI — Chennai Control Centre",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "data" / "wattguard_output.csv"
FULL_DATA_FILE = ROOT / "notebooks" / "full.csv"
EVALUATION_FILE = ROOT / "data" / "wattguard_evaluation.csv"
WEB_HISTORY_FILE = ROOT / "data" / "wattguard_web_history.csv.gz"

# ============================================================
# INDUSTRIAL CONTROL-ROOM THEME
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #0a1015;
    --bg2: #0d141a;
    --panel: #111920;
    --panel2: #0e161c;
    --line: #27343d;
    --line2: #1d2830;
    --text: #e6edf2;
    --muted: #8fa1ad;
    --faint: #60717c;
    --cyan: #35c1cf;
    --blue: #5c94cf;
    --green: #3fb58e;
    --amber: #e0a33a;
    --red: #e25a49;
    --mono: 'IBM Plex Mono', monospace;
    --ui: 'Inter', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--ui);
}

.stApp {
    color: var(--text);
    background:
        linear-gradient(rgba(39,52,61,.18) 1px, transparent 1px) 0 0/32px 32px,
        linear-gradient(90deg, rgba(39,52,61,.18) 1px, transparent 1px) 0 0/32px 32px,
        var(--bg);
}

.block-container {
    max-width: 1420px;
    padding-top: 0.9rem;
    padding-bottom: 3rem;
    padding-left: 1.6rem;
    padding-right: 1.6rem;
}

#MainMenu,
footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}

/* ---------- Header ---------- */

.ctrl-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    padding: 13px 15px;
    border: 1px solid var(--line);
    background: var(--panel2);
}

.ctrl-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.ctrl-logo {
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #31505f;
    background: #13212a;
    color: var(--cyan);
    font-family: var(--mono);
    font-size: 17px;
    font-weight: 600;
}

.ctrl-title {
    color: var(--text);
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.1px;
}

.ctrl-sub {
    margin-top: 3px;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 10.5px;
}

.online {
    color: var(--green);
    font-family: var(--mono);
    font-size: 10.5px;
    white-space: nowrap;
}

.online strong {
    color: var(--text);
    font-weight: 500;
}

.ticker {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    padding: 7px 13px;
    margin-bottom: 12px;
    border: 1px solid var(--line);
    border-top: 0;
    background: #0c1318;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 9.8px;
}

.ticker strong {
    color: var(--text);
    font-weight: 500;
}

.ops-label {
    margin: 8px 0 7px;
    color: var(--faint);
    font-family: var(--mono);
    font-size: 9.5px;
    letter-spacing: 1.25px;
    text-transform: uppercase;
}

/* ---------- KPI ---------- */

.kpi {
    position: relative;
    min-height: 90px;
    padding: 13px 14px;
    border: 1px solid var(--line);
    background: var(--panel);
}

.kpi::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 3px;
    background: var(--cyan);
}

.kpi.red::before {
    background: var(--red);
}

.kpi.amber::before {
    background: var(--amber);
}

.kpi.green::before {
    background: var(--green);
}

.kpi.blue::before {
    background: var(--blue);
}

.kpi .v {
    color: var(--text);
    font-family: var(--mono);
    font-size: 23px;
    font-weight: 600;
}

.kpi .l {
    margin-top: 4px;
    color: var(--muted);
    font-size: 10.5px;
    letter-spacing: 0.35px;
    text-transform: uppercase;
}

.kpi .s {
    margin-top: 5px;
    color: var(--faint);
    font-family: var(--mono);
    font-size: 9px;
}

/* ---------- Panels ---------- */

.panel {
    padding: 14px 15px;
    margin-bottom: 13px;
    border: 1px solid var(--line);
    background: var(--panel);
}

.panel-head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 10px;
    padding-bottom: 8px;
    margin-bottom: 10px;
    border-bottom: 1px solid var(--line2);
}

.panel-title {
    color: var(--text);
    font-size: 12.5px;
    font-weight: 600;
    letter-spacing: 0.2px;
}

.panel-meta {
    color: var(--faint);
    font-family: var(--mono);
    font-size: 8.9px;
}

/* ---------- Filter / context ---------- */

.context-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0,1fr));
    gap: 8px;
    margin-bottom: 10px;
}

.context-box {
    padding: 9px 10px;
    border: 1px solid var(--line);
    background: #0d151b;
}

.context-box .k {
    color: var(--faint);
    font-family: var(--mono);
    font-size: 8.5px;
    text-transform: uppercase;
}

.context-box .v {
    margin-top: 3px;
    color: var(--text);
    font-family: var(--mono);
    font-size: 11px;
}

/* ---------- Alarm ---------- */

.alarm {
    padding: 9px 10px;
    margin-bottom: 7px;
    border: 1px solid #302b2a;
    border-left: 3px solid var(--red);
    background: #171415;
}

.alarm.amber {
    border-color: #302d22;
    border-left-color: var(--amber);
    background: #191811;
}

.alarm.green {
    border-color: #21312b;
    border-left-color: var(--green);
    background: #111916;
}

.alarm-id {
    color: var(--text);
    font-family: var(--mono);
    font-size: 11.5px;
    font-weight: 600;
}

.alarm-meta {
    margin-top: 3px;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 9.3px;
}

.riskbar {
    height: 7px;
    margin-top: 7px;
    overflow: hidden;
    border: 1px solid #2b3943;
    background: #19242c;
}

.riskbar > div {
    height: 100%;
    background: var(--red);
}

.riskbar.amber > div {
    background: var(--amber);
}

.riskbar.green > div {
    background: var(--green);
}

/* ---------- Badges ---------- */

.badge {
    display: inline-block;
    padding: 3px 7px;
    border: 1px solid var(--line);
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: .25px;
}

.badge.red {
    color: var(--red);
    border-color: #5a2c28;
    background: #1d1312;
}

.badge.amber {
    color: var(--amber);
    border-color: #5b4722;
    background: #1b180f;
}

.badge.green {
    color: var(--green);
    border-color: #265146;
    background: #101a17;
}

.badge.blue {
    color: #7db1e5;
    border-color: #304f6a;
    background: #111923;
}

/* ---------- Consumer ---------- */

.consumer-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    padding: 14px 15px;
    border: 1px solid var(--line);
    background: var(--panel);
}

.consumer-id {
    color: var(--text);
    font-family: var(--mono);
    font-size: 18px;
    font-weight: 600;
}

.consumer-sub {
    margin-top: 4px;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 9.8px;
}

.big-score {
    color: var(--text);
    font-family: var(--mono);
    font-size: 29px;
    font-weight: 600;
    text-align: right;
}

.big-score small {
    color: var(--muted);
    font-size: 10px;
    font-weight: 400;
}

.reason {
    padding: 8px 0;
    border-bottom: 1px solid var(--line2);
    color: #cbd6dd;
    font-size: 11.5px;
}

.reason:last-child {
    border-bottom: 0;
}

.note {
    padding: 11px 12px;
    border: 1px solid var(--line);
    border-left: 3px solid var(--cyan);
    background: #0e171d;
    color: #ccd7de;
    font-size: 11.5px;
    line-height: 1.55;
}

.note strong {
    color: var(--text);
}

.money {
    color: var(--amber);
    font-family: var(--mono);
    font-size: 27px;
    font-weight: 600;
}

/* ---------- Feeder table cards ---------- */

.feeder-card {
    padding: 10px 11px;
    margin-bottom: 7px;
    border: 1px solid var(--line);
    background: #0e161c;
}

.feeder-name {
    color: var(--text);
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 600;
}

.feeder-meta {
    margin-top: 3px;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 9px;
}


/* ---------- Energy accounting ---------- */

.energy-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
    margin: 10px 0 14px;
}

.energy-box {
    position: relative;
    min-height: 92px;
    padding: 11px 12px;
    border: 1px solid var(--line);
    background:
        linear-gradient(180deg, rgba(53,193,207,.035), transparent 55%),
        #0d151a;
}

.energy-box::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 2px;
    background: var(--cyan);
    opacity: .75;
}

.energy-box.warn::after {
    background: var(--amber);
}

.energy-box.red::after {
    background: var(--red);
}

.energy-box.green::after {
    background: var(--green);
}

.energy-k {
    color: var(--faint);
    font-family: var(--mono);
    font-size: 8.4px;
    letter-spacing: .65px;
    text-transform: uppercase;
}

.energy-v {
    margin-top: 6px;
    color: var(--text);
    font-family: var(--mono);
    font-size: 20px;
    font-weight: 600;
}

.energy-s {
    margin-top: 5px;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 8.8px;
}

/* ---------- Substation mimic / single-line style ---------- */

.station-shell {
    border: 1px solid #30414c;
    background:
        radial-gradient(circle at 20% 15%, rgba(53,193,207,.04), transparent 24%),
        radial-gradient(circle at 80% 80%, rgba(92,148,207,.035), transparent 22%),
        #0b1217;
    padding: 14px;
    margin-top: 10px;
}

.station-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    padding: 11px 12px;
    border: 1px solid var(--line);
    background: #0f181e;
}

.station-name {
    color: var(--text);
    font-family: var(--mono);
    font-size: 15px;
    font-weight: 600;
}

.station-place {
    margin-top: 4px;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 9px;
}

.station-state {
    color: var(--green);
    font-family: var(--mono);
    font-size: 9px;
    text-align: right;
}

.mimic {
    position: relative;
    padding: 22px 10px 12px;
}

.supply-node {
    width: 230px;
    margin: 0 auto;
    padding: 10px 12px;
    border: 1px solid #3a5665;
    background: #101c23;
    text-align: center;
}

.supply-icon {
    color: var(--cyan);
    font-family: var(--mono);
    font-size: 20px;
    font-weight: 600;
}

.supply-title {
    margin-top: 3px;
    color: var(--text);
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 600;
}

.supply-sub {
    margin-top: 3px;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 8.4px;
}

.vline {
    width: 2px;
    height: 24px;
    margin: 0 auto;
    background: #4b7180;
}

.breaker {
    width: 150px;
    margin: 0 auto;
    padding: 6px 8px;
    border: 1px solid #32505e;
    background: #0f181e;
    color: var(--green);
    font-family: var(--mono);
    font-size: 8.8px;
    text-align: center;
}

.bus-wrap {
    position: relative;
    padding: 14px 18px 4px;
}

.bus-label {
    margin-bottom: 6px;
    color: var(--faint);
    font-family: var(--mono);
    font-size: 8px;
    text-align: center;
    letter-spacing: 1px;
}

.busbar {
    height: 5px;
    border-top: 1px solid #5a8796;
    border-bottom: 1px solid #28424e;
    background: #244b59;
    box-shadow: 0 0 12px rgba(53,193,207,.08);
}

.feeder-bank {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 10px;
    padding: 0 6px 10px;
}

.feeder-mimic {
    position: relative;
    min-height: 164px;
    padding: 12px 11px 10px;
    border: 1px solid var(--line);
    border-top: 3px solid var(--green);
    background: #0e161c;
}

.feeder-mimic::before {
    content: "";
    position: absolute;
    left: 50%;
    top: -13px;
    width: 2px;
    height: 10px;
    background: #4b7180;
}

.feeder-mimic.red {
    border-top-color: var(--red);
}

.feeder-mimic.amber {
    border-top-color: var(--amber);
}

.fm-head {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    align-items: center;
}

.fm-id {
    color: var(--text);
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 600;
}

.fm-status {
    font-family: var(--mono);
    font-size: 8px;
    color: var(--green);
}

.feeder-mimic.red .fm-status {
    color: var(--red);
}

.feeder-mimic.amber .fm-status {
    color: var(--amber);
}

.fm-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7px;
    margin-top: 10px;
}

.fm-cell {
    padding: 6px 7px;
    border: 1px solid var(--line2);
    background: #0b1318;
}

.fm-k {
    color: var(--faint);
    font-family: var(--mono);
    font-size: 7.4px;
    text-transform: uppercase;
}

.fm-v {
    margin-top: 3px;
    color: var(--text);
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 500;
}

.station-legend {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    padding: 8px 10px;
    margin-top: 8px;
    border: 1px solid var(--line2);
    background: #0c1419;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 8px;
}

.led {
    display: inline-block;
    width: 7px;
    height: 7px;
    margin-right: 4px;
    border-radius: 50%;
}

.led.green { background: var(--green); }
.led.amber { background: var(--amber); }
.led.red { background: var(--red); }

.energy-ledger {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--mono);
    font-size: 9px;
}

.energy-ledger th {
    padding: 7px 8px;
    border-bottom: 1px solid var(--line);
    color: var(--faint);
    text-align: left;
    font-weight: 500;
}

.energy-ledger td {
    padding: 8px;
    border-bottom: 1px solid var(--line2);
    color: var(--muted);
}

.energy-ledger td.num {
    color: var(--text);
    text-align: right;
}

@media(max-width: 900px) {
    .energy-strip {
        grid-template-columns: 1fr 1fr;
    }
}

/* ---------- Streamlit controls ---------- */

div[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    border-radius: 0 !important;
    border-color: var(--line) !important;
    background: var(--panel2) !important;
}

.stButton button,
.stDownloadButton button {
    border-radius: 0 !important;
    border: 1px solid var(--line) !important;
    background: #142029 !important;
    color: var(--text) !important;
    box-shadow: none !important;
}

.stButton button:hover,
.stDownloadButton button:hover {
    border-color: var(--cyan) !important;
    color: var(--cyan) !important;
}

div[role="radiogroup"] {
    padding: 5px 7px;
    margin-bottom: 12px;
    border: 1px solid var(--line);
    background: #0d151a;
}

.smallprint {
    padding-top: 10px;
    margin-top: 20px;
    border-top: 1px solid var(--line);
    color: var(--faint);
    font-family: var(--mono);
    font-size: 8.8px;
    line-height: 1.55;
}

@media(max-width: 900px) {
    .ctrl-head {
        align-items: flex-start;
        flex-direction: column;
    }
    .context-strip {
        grid-template-columns: 1fr 1fr;
    }
}

/* ---------- Consumer identity ---------- */

.identity-grid {
    display: grid;
    grid-template-columns: 1.35fr .85fr .85fr .85fr;
    gap: 8px;
    margin: 9px 0 13px;
}

.identity-card {
    border: 1px solid var(--line);
    background: #0e161c;
    padding: 10px 11px;
    min-height: 72px;
}

.identity-label {
    color: var(--faint);
    font-family: var(--mono);
    font-size: 7.8px;
    letter-spacing: .8px;
    text-transform: uppercase;
}

.identity-value {
    margin-top: 5px;
    color: var(--text);
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 600;
    line-height: 1.35;
}

.identity-value.large {
    font-size: 14px;
}

.identity-sub {
    margin-top: 4px;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 8px;
}

/* ---------- Usage analytics ---------- */

.usage-summary {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
    margin: 9px 0 13px;
}

.usage-stat {
    border: 1px solid var(--line);
    background: #0d151a;
    padding: 9px 10px;
    min-height: 68px;
}

.usage-stat .uk {
    color: var(--faint);
    font-family: var(--mono);
    font-size: 7.5px;
    text-transform: uppercase;
}

.usage-stat .uv {
    margin-top: 5px;
    color: var(--text);
    font-family: var(--mono);
    font-size: 16px;
    font-weight: 600;
}

.usage-stat .us {
    margin-top: 3px;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 7.8px;
}

.bill-split {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    margin: 8px 0 12px;
}

.bill-cell {
    position: relative;
    border: 1px solid var(--line);
    background: #0d151a;
    padding: 11px 12px;
}

.bill-cell::after {
    content:"";
    position:absolute;
    left:0;
    right:0;
    bottom:0;
    height:2px;
    background:var(--blue);
}

.bill-cell.red::after { background:var(--red); }
.bill-cell.amber::after { background:var(--amber); }

.bill-k {
    color:var(--faint);
    font-family:var(--mono);
    font-size:7.8px;
    text-transform:uppercase;
}

.bill-v {
    margin-top:5px;
    color:var(--text);
    font-family:var(--mono);
    font-size:19px;
    font-weight:600;
}

.bill-s {
    margin-top:4px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:8px;
}

/* ---------- Better substation mimic ---------- */

.sl-shell {
    border: 1px solid #344751;
    background:
        linear-gradient(rgba(52,71,81,.10) 1px, transparent 1px) 0 0/22px 22px,
        linear-gradient(90deg, rgba(52,71,81,.10) 1px, transparent 1px) 0 0/22px 22px,
        #091116;
    padding: 14px;
}

.sl-titlebar {
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:16px;
    padding:10px 12px;
    border:1px solid var(--line);
    background:#0d171d;
}

.sl-station {
    color:var(--text);
    font-family:var(--mono);
    font-size:14px;
    font-weight:600;
}

.sl-meta {
    margin-top:4px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:8px;
}

.sl-live {
    color:var(--green);
    font-family:var(--mono);
    font-size:8.5px;
    text-align:right;
}

.sl-body {
    padding:16px 4px 6px;
}

.sl-node {
    width:230px;
    margin:0 auto;
    padding:9px 10px;
    border:1px solid #3d5966;
    background:#101c22;
    text-align:center;
    font-family:var(--mono);
}

.sl-node .n1 {
    color:var(--cyan);
    font-size:11px;
    font-weight:600;
}

.sl-node .n2 {
    margin-top:3px;
    color:var(--muted);
    font-size:7.5px;
}

.sl-line {
    width:2px;
    height:22px;
    margin:0 auto;
    background:#577d8b;
}

.sl-breaker {
    width:132px;
    margin:0 auto;
    padding:5px 7px;
    border:1px solid #31515d;
    background:#0d171d;
    color:var(--green);
    font-family:var(--mono);
    font-size:7.8px;
    text-align:center;
}

.sl-transformer {
    width:230px;
    margin:0 auto;
    padding:10px;
    border:1px solid #536773;
    background:#111a20;
    text-align:center;
}

.sl-coils {
    display:flex;
    justify-content:center;
    gap:0;
    margin-bottom:5px;
}

.sl-coil {
    width:30px;
    height:30px;
    border:2px solid #5d8290;
    border-radius:50%;
    margin:0 -4px;
    background:#0d151a;
}

.sl-transformer .t1 {
    color:var(--text);
    font-family:var(--mono);
    font-size:9px;
    font-weight:600;
}

.sl-transformer .t2 {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.5px;
}

.sl-bus-label {
    margin:0 0 5px;
    color:var(--faint);
    font-family:var(--mono);
    font-size:7.5px;
    text-align:center;
    letter-spacing:1px;
}

.sl-bus {
    height:5px;
    margin:0 22px;
    border-top:1px solid #6993a1;
    border-bottom:1px solid #233b45;
    background:#28515e;
}

.sl-feeders {
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(185px,1fr));
    gap:9px;
    padding:20px 5px 4px;
}

.sl-feeder {
    position:relative;
    border:1px solid var(--line);
    border-top:3px solid var(--green);
    background:#0d161b;
    padding:10px;
    min-height:152px;
}

.sl-feeder::before {
    content:"";
    position:absolute;
    top:-20px;
    left:50%;
    width:2px;
    height:17px;
    background:#577d8b;
}

.sl-feeder.amber { border-top-color:var(--amber); }
.sl-feeder.red { border-top-color:var(--red); }

.sl-fhead {
    display:flex;
    justify-content:space-between;
    gap:8px;
    align-items:center;
}

.sl-fid {
    color:var(--text);
    font-family:var(--mono);
    font-size:10px;
    font-weight:600;
}

.sl-fstate {
    color:var(--green);
    font-family:var(--mono);
    font-size:7px;
}

.sl-feeder.amber .sl-fstate { color:var(--amber); }
.sl-feeder.red .sl-fstate { color:var(--red); }

.sl-fgrid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:6px;
    margin-top:8px;
}

.sl-fcell {
    border:1px solid var(--line2);
    background:#0a1217;
    padding:6px;
}

.sl-fk {
    color:var(--faint);
    font-family:var(--mono);
    font-size:6.8px;
    text-transform:uppercase;
}

.sl-fv {
    margin-top:3px;
    color:var(--text);
    font-family:var(--mono);
    font-size:9px;
    font-weight:500;
}

@media(max-width: 900px) {
    .identity-grid,
    .usage-summary,
    .bill-split {
        grid-template-columns:1fr 1fr;
    }
}


/* ==========================================================
   V5 — WATTGUARD DISTINCTIVE OPERATIONS UI
   ========================================================== */

.command-rail {
    display:grid;
    grid-template-columns:repeat(5, 1fr);
    gap:0;
    margin:10px 0 14px;
    border:1px solid var(--line);
    background:#091116;
}

.command-step {
    position:relative;
    min-height:86px;
    padding:12px 13px;
    border-right:1px solid var(--line);
    background:
        linear-gradient(180deg, rgba(54,198,211,.035), transparent 65%),
        #0d151a;
}

.command-step:last-child {
    border-right:none;
}

.command-step::after {
    content:"";
    position:absolute;
    top:50%;
    right:-7px;
    width:12px;
    height:12px;
    background:#0d151a;
    border-top:1px solid var(--line);
    border-right:1px solid var(--line);
    transform:translateY(-50%) rotate(45deg);
    z-index:2;
}

.command-step:last-child::after {
    display:none;
}

.command-step .cs-num {
    color:var(--cyan);
    font-family:var(--mono);
    font-size:8px;
    letter-spacing:1px;
}

.command-step .cs-title {
    margin-top:5px;
    color:var(--text);
    font-family:var(--mono);
    font-size:11px;
    font-weight:600;
}

.command-step .cs-value {
    margin-top:5px;
    color:var(--text);
    font-family:var(--mono);
    font-size:17px;
    font-weight:600;
}

.command-step .cs-sub {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.8px;
}

.dispatch-shell {
    border:1px solid #31434e;
    background:
        linear-gradient(rgba(49,67,78,.09) 1px, transparent 1px) 0 0/18px 18px,
        linear-gradient(90deg, rgba(49,67,78,.09) 1px, transparent 1px) 0 0/18px 18px,
        #0a1217;
    padding:12px 13px;
    margin:8px 0 14px;
}

.dispatch-head {
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:12px;
    padding-bottom:9px;
    border-bottom:1px solid var(--line2);
}

.dispatch-title {
    color:var(--text);
    font-family:var(--mono);
    font-size:11px;
    font-weight:600;
}

.dispatch-sub {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.8px;
}

.dispatch-mode {
    color:var(--green);
    font-family:var(--mono);
    font-size:8px;
    text-align:right;
}

.dispatch-grid {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:8px;
    margin-top:10px;
}

.dispatch-cell {
    border:1px solid var(--line);
    background:#0d151a;
    padding:9px 10px;
}

.dispatch-k {
    color:var(--faint);
    font-family:var(--mono);
    font-size:7.3px;
    text-transform:uppercase;
    letter-spacing:.5px;
}

.dispatch-v {
    margin-top:5px;
    color:var(--text);
    font-family:var(--mono);
    font-size:18px;
    font-weight:600;
}

.dispatch-s {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.5px;
}

.case-launch {
    border:1px solid #31505d;
    border-left:3px solid var(--cyan);
    background:#0e171c;
    padding:11px 12px;
    margin:8px 0 12px;
}

.case-launch-title {
    color:var(--text);
    font-family:var(--mono);
    font-size:10px;
    font-weight:600;
}

.case-launch-sub {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.8px;
}

.case-timeline {
    display:grid;
    grid-template-columns:repeat(5,1fr);
    gap:7px;
    margin:10px 0 12px;
}

.timeline-node {
    position:relative;
    min-height:66px;
    border:1px solid var(--line);
    background:#0d151a;
    padding:9px 9px;
}

.timeline-node.active {
    border-color:#385d6b;
    box-shadow:inset 0 2px 0 var(--cyan);
}

.timeline-node.done {
    box-shadow:inset 0 2px 0 var(--green);
}

.timeline-k {
    color:var(--faint);
    font-family:var(--mono);
    font-size:7px;
    text-transform:uppercase;
}

.timeline-v {
    margin-top:5px;
    color:var(--text);
    font-family:var(--mono);
    font-size:9px;
    font-weight:600;
}

.operator-console {
    border:1px solid var(--line);
    background:#080f13;
    padding:10px 11px;
    font-family:var(--mono);
    font-size:8.5px;
    color:var(--muted);
    line-height:1.75;
}

.operator-console .green {
    color:var(--green);
}

.operator-console .amber {
    color:var(--amber);
}

.operator-console .red {
    color:var(--red);
}

.signal-tag {
    display:inline-block;
    margin:0 5px 6px 0;
    padding:4px 7px;
    border:1px solid #344650;
    background:#0d171c;
    color:#cfd9df;
    font-family:var(--mono);
    font-size:8px;
}

.case-banner {
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:14px;
    border:1px solid #324852;
    border-left:3px solid var(--cyan);
    background:
        linear-gradient(90deg, rgba(54,198,211,.04), transparent 32%),
        #0c151a;
    padding:12px 13px;
    margin:9px 0 12px;
}

.case-banner .cb-id {
    color:var(--text);
    font-family:var(--mono);
    font-size:13px;
    font-weight:600;
}

.case-banner .cb-name {
    margin-top:4px;
    color:#dce5ea;
    font-family:var(--mono);
    font-size:10px;
}

.case-banner .cb-address {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:8px;
}

.case-banner .cb-right {
    color:var(--cyan);
    font-family:var(--mono);
    font-size:9px;
    text-align:right;
}

.outcome-panel {
    border:1px solid var(--line);
    background:#0b1318;
    padding:11px 12px;
    margin-top:10px;
}

.outcome-title {
    color:var(--text);
    font-family:var(--mono);
    font-size:10px;
    font-weight:600;
}

.outcome-sub {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.8px;
}

@media(max-width:1000px){
    .command-rail,
    .case-timeline {
        grid-template-columns:1fr;
    }
    .command-step {
        border-right:none;
        border-bottom:1px solid var(--line);
    }
    .command-step::after {
        display:none;
    }
    .dispatch-grid {
        grid-template-columns:1fr 1fr;
    }
}


/* ==========================================================
   V6 — BEHAVIOUR SHIFT / DIFFERENCE INTELLIGENCE
   ========================================================== */

.shift-shell {
    border:1px solid #314651;
    background:
        linear-gradient(90deg, rgba(54,198,211,.04), transparent 38%),
        #0a1217;
    padding:12px 13px;
    margin:11px 0 14px;
}

.shift-head {
    display:flex;
    justify-content:space-between;
    gap:12px;
    align-items:flex-start;
    padding-bottom:9px;
    border-bottom:1px solid var(--line2);
}

.shift-title {
    color:var(--text);
    font-family:var(--mono);
    font-size:10.5px;
    font-weight:600;
}

.shift-sub {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.8px;
}

.shift-state {
    color:var(--cyan);
    font-family:var(--mono);
    font-size:8px;
    text-align:right;
}

.shift-flow {
    display:grid;
    grid-template-columns:1fr 34px 1fr 34px 1fr 34px 1fr;
    gap:7px;
    align-items:center;
    margin-top:11px;
}

.shift-box {
    min-height:92px;
    border:1px solid var(--line);
    background:#0d161b;
    padding:10px 11px;
}

.shift-box.before {
    box-shadow:inset 0 2px 0 var(--blue);
}

.shift-box.current {
    box-shadow:inset 0 2px 0 var(--cyan);
}

.shift-box.delta.negative {
    box-shadow:inset 0 2px 0 var(--red);
}

.shift-box.delta.positive {
    box-shadow:inset 0 2px 0 var(--green);
}

.shift-box.ai {
    box-shadow:inset 0 2px 0 var(--amber);
}

.shift-k {
    color:var(--faint);
    font-family:var(--mono);
    font-size:7.2px;
    text-transform:uppercase;
    letter-spacing:.55px;
}

.shift-v {
    margin-top:7px;
    color:var(--text);
    font-family:var(--mono);
    font-size:18px;
    font-weight:600;
}

.shift-s {
    margin-top:4px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.7px;
    line-height:1.45;
}

.shift-arrow {
    color:#587581;
    font-family:var(--mono);
    font-size:18px;
    text-align:center;
}

.signature-shell {
    border:1px solid var(--line);
    background:#0a1217;
    padding:10px 11px;
    margin:8px 0 13px;
}

.signature-head {
    display:flex;
    justify-content:space-between;
    gap:10px;
    align-items:flex-start;
}

.signature-title {
    color:var(--text);
    font-family:var(--mono);
    font-size:9px;
    font-weight:600;
}

.signature-sub {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.3px;
}

.signature-grid {
    display:grid;
    grid-template-columns:repeat(6,1fr);
    gap:6px;
    margin-top:9px;
}

.sig-cell {
    border:1px solid var(--line2);
    background:#0d151a;
    padding:7px 7px;
    min-height:62px;
}

.sig-cell.red {
    box-shadow:inset 0 2px 0 var(--red);
}

.sig-cell.amber {
    box-shadow:inset 0 2px 0 var(--amber);
}

.sig-cell.green {
    box-shadow:inset 0 2px 0 var(--green);
}

.sig-k {
    color:var(--faint);
    font-family:var(--mono);
    font-size:6.8px;
}

.sig-v {
    margin-top:4px;
    color:var(--text);
    font-family:var(--mono);
    font-size:12px;
    font-weight:600;
}

.sig-s {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:6.7px;
}

.gap-bridge {
    display:grid;
    grid-template-columns:1fr 36px 1fr 36px 1fr;
    align-items:center;
    gap:7px;
    margin:9px 0 12px;
}

.gap-node {
    border:1px solid var(--line);
    background:#0d151a;
    padding:10px 11px;
    min-height:78px;
}

.gap-node.recorded {
    box-shadow:inset 0 2px 0 var(--green);
}

.gap-node.unbilled {
    box-shadow:inset 0 2px 0 var(--red);
}

.gap-node.total {
    box-shadow:inset 0 2px 0 var(--amber);
}

.gap-op {
    color:#6a7d87;
    font-family:var(--mono);
    font-size:20px;
    text-align:center;
}

.gap-k {
    color:var(--faint);
    font-family:var(--mono);
    font-size:7px;
    text-transform:uppercase;
}

.gap-v {
    margin-top:5px;
    color:var(--text);
    font-family:var(--mono);
    font-size:17px;
    font-weight:600;
}

.gap-s {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7px;
}

@media(max-width:1000px){
    .shift-flow {
        grid-template-columns:1fr;
    }
    .shift-arrow {
        transform:rotate(90deg);
    }
    .signature-grid {
        grid-template-columns:1fr 1fr 1fr;
    }
    .gap-bridge {
        grid-template-columns:1fr;
    }
    .gap-op {
        transform:rotate(90deg);
    }
}


/* ==========================================================
   V7 — TOP-K INSPECTION VALIDATION
   ========================================================== */

.validation-shell {
    border:1px solid #314651;
    background:
        linear-gradient(90deg, rgba(54,198,211,.045), transparent 42%),
        #091116;
    padding:13px;
    margin:10px 0 14px;
}

.validation-head {
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:14px;
    padding-bottom:10px;
    border-bottom:1px solid var(--line2);
}

.validation-title {
    color:var(--text);
    font-family:var(--mono);
    font-size:11px;
    font-weight:600;
}

.validation-sub {
    margin-top:4px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.8px;
    line-height:1.5;
}

.validation-badge {
    border:1px solid #315e4f;
    background:#0b1915;
    color:var(--green);
    padding:6px 8px;
    font-family:var(--mono);
    font-size:8px;
    text-align:right;
}

.proof-grid {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:8px;
    margin-top:11px;
}

.proof-card {
    border:1px solid var(--line);
    background:#0d151a;
    padding:10px 11px;
    min-height:128px;
}

.proof-card.best {
    border-color:#416c61;
    box-shadow:inset 0 3px 0 var(--green);
}

.proof-k {
    color:var(--faint);
    font-family:var(--mono);
    font-size:7.4px;
    text-transform:uppercase;
    letter-spacing:.55px;
}

.proof-v {
    margin-top:7px;
    color:var(--text);
    font-family:var(--mono);
    font-size:20px;
    font-weight:600;
}

.proof-s {
    margin-top:5px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.7px;
    line-height:1.5;
}

.lift-value {
    margin-top:8px;
    color:var(--cyan);
    font-family:var(--mono);
    font-size:12px;
    font-weight:600;
}

.precision-track {
    height:7px;
    margin-top:10px;
    border:1px solid #273841;
    background:#091116;
    overflow:hidden;
}

.precision-fill {
    height:100%;
    background:linear-gradient(90deg,#315a66,#4ab8c8);
}

.random-proof {
    display:grid;
    grid-template-columns:1.2fr 40px 1.2fr 1fr;
    align-items:center;
    gap:9px;
    margin:10px 0 14px;
}

.random-node {
    border:1px solid var(--line);
    background:#0d151a;
    padding:11px 12px;
    min-height:86px;
}

.random-node.random {
    box-shadow:inset 0 2px 0 #6e7e86;
}

.random-node.wg {
    box-shadow:inset 0 2px 0 var(--green);
}

.random-node.result {
    box-shadow:inset 0 2px 0 var(--cyan);
}

.random-op {
    color:#6c7e87;
    font-family:var(--mono);
    font-size:19px;
    text-align:center;
}

.random-k {
    color:var(--faint);
    font-family:var(--mono);
    font-size:7.2px;
    text-transform:uppercase;
}

.random-v {
    margin-top:5px;
    color:var(--text);
    font-family:var(--mono);
    font-size:18px;
    font-weight:600;
}

.random-s {
    margin-top:4px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.6px;
    line-height:1.45;
}

@media(max-width:1000px){
    .proof-grid,
    .random-proof {
        grid-template-columns:1fr 1fr;
    }
    .random-op {
        display:none;
    }
}


/* ==========================================================
   V9 — DISTINCTIVE DIFFERENTIATORS
   ========================================================== */

.peer-shell {
    border:1px solid #314651;
    background:
        linear-gradient(90deg, rgba(54,198,211,.04), transparent 40%),
        #091116;
    padding:12px 13px;
    margin:10px 0 14px;
}

.peer-head {
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:12px;
    padding-bottom:9px;
    border-bottom:1px solid var(--line2);
}

.peer-title {
    color:var(--text);
    font-family:var(--mono);
    font-size:10.5px;
    font-weight:600;
}

.peer-sub {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.8px;
    line-height:1.45;
}

.peer-state {
    color:var(--cyan);
    font-family:var(--mono);
    font-size:8px;
    text-align:right;
}

.peer-grid {
    display:grid;
    grid-template-columns:1fr 42px 1fr;
    gap:9px;
    align-items:stretch;
    margin-top:10px;
}

.peer-card {
    border:1px solid var(--line);
    background:#0d151a;
    padding:10px 11px;
}

.peer-card.target {
    box-shadow:inset 0 3px 0 var(--amber);
}

.peer-card.twin {
    box-shadow:inset 0 3px 0 var(--green);
}

.peer-vs {
    display:flex;
    align-items:center;
    justify-content:center;
    color:#68818c;
    font-family:var(--mono);
    font-size:13px;
}

.peer-id {
    color:var(--text);
    font-family:var(--mono);
    font-size:11px;
    font-weight:600;
}

.peer-name {
    margin-top:3px;
    color:#d7e1e6;
    font-family:var(--mono);
    font-size:9px;
}

.peer-metrics {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:6px;
    margin-top:9px;
}

.peer-cell {
    border:1px solid var(--line2);
    background:#0a1217;
    padding:6px 7px;
}

.peer-k {
    color:var(--faint);
    font-family:var(--mono);
    font-size:6.8px;
    text-transform:uppercase;
}

.peer-v {
    margin-top:3px;
    color:var(--text);
    font-family:var(--mono);
    font-size:10px;
    font-weight:600;
}

.fingerprint-shell {
    border:1px solid #314651;
    background:#091116;
    padding:12px 13px;
    margin:10px 0 14px;
}

.fingerprint-title {
    color:var(--text);
    font-family:var(--mono);
    font-size:10.5px;
    font-weight:600;
}

.fingerprint-sub {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.7px;
    line-height:1.45;
}

.fingerprint-row {
    display:grid;
    grid-template-columns:170px 1fr 56px;
    gap:9px;
    align-items:center;
    margin-top:9px;
}

.fp-label {
    color:#cfd8de;
    font-family:var(--mono);
    font-size:8px;
}

.fp-track {
    height:8px;
    border:1px solid #273841;
    background:#071015;
    overflow:hidden;
}

.fp-fill {
    height:100%;
    background:linear-gradient(90deg,#315966,#45a9ba);
}

.fp-fill.warn {
    background:linear-gradient(90deg,#806329,#d8a640);
}

.fp-fill.hot {
    background:linear-gradient(90deg,#813c35,#d76356);
}

.fp-score {
    color:var(--text);
    font-family:var(--mono);
    font-size:8px;
    text-align:right;
}

.guard-shell {
    border:1px solid #344650;
    background:
        linear-gradient(90deg, rgba(216,166,64,.045), transparent 40%),
        #0a1217;
    padding:12px 13px;
    margin:10px 0 14px;
}

.guard-head {
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:12px;
}

.guard-title {
    color:var(--text);
    font-family:var(--mono);
    font-size:10.5px;
    font-weight:600;
}

.guard-sub {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.7px;
    line-height:1.45;
}

.guard-state {
    padding:6px 8px;
    border:1px solid #66532f;
    background:#171309;
    color:var(--amber);
    font-family:var(--mono);
    font-size:8px;
    text-align:right;
}

.guard-grid {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:7px;
    margin-top:10px;
}

.guard-cell {
    border:1px solid var(--line);
    background:#0d151a;
    padding:8px 9px;
}

.guard-k {
    color:var(--faint);
    font-family:var(--mono);
    font-size:6.8px;
    text-transform:uppercase;
}

.guard-v {
    margin-top:4px;
    color:var(--text);
    font-family:var(--mono);
    font-size:12px;
    font-weight:600;
}

.guard-s {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:6.8px;
}

.ops-proof {
    border:1px solid #314651;
    background:#091116;
    padding:12px 13px;
    margin:10px 0 14px;
}

.ops-proof-grid {
    display:grid;
    grid-template-columns:1fr 34px 1fr 34px 1fr;
    gap:8px;
    align-items:center;
    margin-top:10px;
}

.ops-proof-node {
    border:1px solid var(--line);
    background:#0d151a;
    padding:10px 11px;
    min-height:82px;
}

.ops-proof-node.wg {
    box-shadow:inset 0 2px 0 var(--green);
}

.ops-proof-node.random {
    box-shadow:inset 0 2px 0 #687981;
}

.ops-proof-node.save {
    box-shadow:inset 0 2px 0 var(--cyan);
}

.ops-proof-op {
    color:#667c86;
    font-family:var(--mono);
    font-size:18px;
    text-align:center;
}

.ops-proof-k {
    color:var(--faint);
    font-family:var(--mono);
    font-size:7px;
    text-transform:uppercase;
}

.ops-proof-v {
    margin-top:5px;
    color:var(--text);
    font-family:var(--mono);
    font-size:18px;
    font-weight:600;
}

.ops-proof-s {
    margin-top:3px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.2px;
    line-height:1.45;
}

@media(max-width:1000px){
    .peer-grid,
    .ops-proof-grid {
        grid-template-columns:1fr;
    }
    .peer-vs,
    .ops-proof-op {
        transform:rotate(90deg);
    }
    .guard-grid {
        grid-template-columns:1fr 1fr;
    }
    .fingerprint-row {
        grid-template-columns:120px 1fr 48px;
    }
}


/* ==========================================================
   V10 — CLICKABLE OPERATIONS UI
   ========================================================== */

.alarm-link {
    display:block;
    text-decoration:none !important;
    color:inherit !important;
    cursor:pointer;
    border-radius:2px;
}

.alarm-link:hover .alarm {
    transform:translateY(-1px);
    border-color:#6d4a45;
    background:
        linear-gradient(90deg, rgba(217,87,75,.07), transparent 35%),
        #11191e;
    box-shadow:0 0 0 1px rgba(217,87,75,.08);
}

.alarm-link:hover .alarm.amber {
    border-color:#766038;
    background:
        linear-gradient(90deg, rgba(216,166,64,.07), transparent 35%),
        #11191e;
}

.alarm-link:hover .alarm.green {
    border-color:#365f52;
    background:
        linear-gradient(90deg, rgba(72,175,137,.06), transparent 35%),
        #11191e;
}

.alarm {
    transition:
        transform .12s ease,
        border-color .12s ease,
        background .12s ease,
        box-shadow .12s ease;
}

.click-hint {
    margin-top:6px;
    color:var(--cyan);
    font-family:var(--mono);
    font-size:7.3px;
    letter-spacing:.45px;
}

.interaction-note {
    border:1px solid #2e414b;
    background:#0b1419;
    padding:7px 9px;
    margin:6px 0 10px;
    color:var(--muted);
    font-family:var(--mono);
    font-size:7.8px;
    line-height:1.45;
}

</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# DATA LOADERS
# ============================================================

@st.cache_data
def load_output():
    if not OUTPUT_FILE.exists():
        return None

    data = pd.read_csv(OUTPUT_FILE)

    if "Consumer_ID" in data.columns:
        data["Consumer_ID"] = data["Consumer_ID"].astype(str)

    for col in ["Risk_Score", "Priority_Score", "Estimated_Unbilled_Units"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    return data




@st.cache_data
def load_evaluation():
    if not EVALUATION_FILE.exists():
        return None

    data = pd.read_csv(EVALUATION_FILE)

    if "Consumer_ID" in data.columns:
        data["Consumer_ID"] = data["Consumer_ID"].astype(str)

    return data


@st.cache_data
def load_full_data():
    if not FULL_DATA_FILE.exists():
        return None
    return pd.read_csv(FULL_DATA_FILE)


@st.cache_data
def load_web_history():
    if not WEB_HISTORY_FILE.exists():
        return None

    data = pd.read_csv(
        WEB_HISTORY_FILE,
        compression="gzip",
        parse_dates=["Date"],
    )

    required = {
        "Consumer_ID",
        "Date",
        "Usage",
    }

    if not required.issubset(
        set(data.columns)
    ):
        return None

    data["Consumer_ID"] = data[
        "Consumer_ID"
    ].astype(str)

    data["Usage"] = pd.to_numeric(
        data["Usage"],
        errors="coerce",
    )

    data = data.dropna(
        subset=[
            "Date",
            "Usage",
        ]
    )

    return data


df = load_output()
evaluation_df = load_evaluation()
raw_df = load_full_data()
web_history_df = load_web_history()

if df is None:
    st.error("data/wattguard_output.csv was not found.")
    st.stop()

required_columns = [
    "Consumer_ID",
    "Area",
    "Substation",
    "Feeder_ID",
    "Risk_Score",
    "Risk_Level",
    "Estimated_Unbilled_Units",
    "Priority_Score",
    "Why_Flagged",
    "Action",
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.stop()

# ============================================================
# CONSTANTS / HELPERS
# ============================================================

DEFAULT_TARIFF = 7.5



def render_html(block):
    """
    Render custom HTML without Markdown accidentally turning nested tags into
    visible code blocks.
    """
    block = textwrap.dedent(str(block)).strip()
    block = re.sub(r">\s+<", "><", block)

    if hasattr(st, "html"):
        st.html(block)
    else:
        st.markdown(block, unsafe_allow_html=True)


def _parse_wg_source_id(value):
    value = str(value)

    if value.startswith("WG-"):
        try:
            return int(value.replace("WG-", ""))
        except Exception:
            return np.nan

    return np.nan


def recover_source_index(data, evaluation):
    """
    Preserve the correct SGCC row behind each Chennai demo consumer.

    Priority:
      1. Existing Source_Index / Original_Index
      2. Existing WG-xxxxx ID
      3. Recover mapping from wattguard_evaluation.csv when rows/features match
    """
    out = data.copy()

    if "Source_Index" not in out.columns:
        out["Source_Index"] = np.nan

    existing = pd.to_numeric(
        out["Source_Index"],
        errors="coerce",
    )

    out["Source_Index"] = existing

    # Old WG IDs are already a reliable source mapping.
    wg_from_current = out["Consumer_ID"].map(_parse_wg_source_id)
    out["Source_Index"] = out["Source_Index"].fillna(wg_from_current)

    if "Original_Consumer_ID" in out.columns:
        wg_from_original = out["Original_Consumer_ID"].map(_parse_wg_source_id)
        out["Source_Index"] = out["Source_Index"].fillna(wg_from_original)

    if out["Source_Index"].notna().all():
        return out

    if evaluation is None or "Consumer_ID" not in evaluation.columns:
        return out

    ev = evaluation.copy()
    ev["_eval_source_index"] = ev["Consumer_ID"].map(_parse_wg_source_id)

    # First attempt: same row order + same model/features.
    if len(ev) == len(out):
        shared_checks = [
            c for c in [
                "Risk_Score",
                "Priority_Score",
                "Estimated_Unbilled_Units",
                "mean_usage",
                "max_usage",
                "std_usage",
                "zero_ratio",
            ]
            if c in out.columns and c in ev.columns
        ]

        matches = []

        for c in shared_checks:
            left = pd.to_numeric(out[c], errors="coerce")
            right = pd.to_numeric(ev[c], errors="coerce")

            valid = left.notna() & right.notna()

            if valid.any():
                close = np.isclose(
                    left[valid].to_numpy(),
                    right[valid].to_numpy(),
                    rtol=1e-7,
                    atol=1e-7,
                )

                matches.append(float(close.mean()))

        if matches and np.mean(matches) > 0.98:
            out["Source_Index"] = out["Source_Index"].fillna(
                ev["_eval_source_index"].reset_index(drop=True)
            )
            return out

    # Second attempt: feature signature merge.
    key_cols = [
        c for c in [
            "Risk_Score",
            "Priority_Score",
            "Estimated_Unbilled_Units",
            "mean_usage",
            "max_usage",
            "std_usage",
            "zero_ratio",
        ]
        if c in out.columns and c in ev.columns
    ]

    if len(key_cols) >= 3:
        left = out.reset_index().rename(columns={"index": "_out_row"}).copy()
        right = ev.copy()

        merge_cols = []

        for c in key_cols[:5]:
            mk = f"_k_{c}"

            left[mk] = pd.to_numeric(
                left[c],
                errors="coerce",
            ).round(6)

            right[mk] = pd.to_numeric(
                right[c],
                errors="coerce",
            ).round(6)

            merge_cols.append(mk)

        left["_dup"] = left.groupby(
            merge_cols,
            dropna=False,
        ).cumcount()

        right["_dup"] = right.groupby(
            merge_cols,
            dropna=False,
        ).cumcount()

        mapped = left[
            ["_out_row"] + merge_cols + ["_dup"]
        ].merge(
            right[
                merge_cols
                + ["_dup", "_eval_source_index"]
            ],
            on=merge_cols + ["_dup"],
            how="left",
        )

        recovered = mapped.set_index("_out_row")["_eval_source_index"]
        out["Source_Index"] = out["Source_Index"].fillna(recovered)

    return out


def enrich_demo_identity(data):
    """
    Adds deterministic synthetic names/addresses for the Chennai demo UI.
    They are not real utility/customer records.
    """
    out = data.copy()

    demo_names = [
        "Arun Kumar",
        "Priya S",
        "Karthik R",
        "Nivetha M",
        "Suresh B",
        "Deepa R",
        "Vignesh K",
        "Harini S",
        "Praveen M",
        "Aishwarya R",
        "Raghul S",
        "Meena K",
        "Naveen Raj",
        "Divya P",
        "Ajay Kumar",
        "Keerthana V",
        "Sanjay R",
        "Anitha M",
        "Vijay S",
        "Janani K",
        "Ashwin R",
        "Lakshmi P",
        "Gokul M",
        "Swetha S",
        "Dinesh K",
        "Ramya V",
        "Saravanan R",
        "Pavithra M",
        "Manoj S",
        "Shalini R",
        "Hari Krishnan",
        "Preethi S",
    ]

    area_streets = {
        "T. Nagar": ["2nd Cross St", "North Usman Rd", "South West Boag Rd", "Bazullah Rd"],
        "Anna Nagar": ["2nd Avenue", "4th Avenue", "6th Main Rd", "12th Main Rd"],
        "Adyar": ["1st Main Rd", "LB Road", "Gandhi Nagar Cross St", "Indira Nagar Main Rd"],
        "Velachery": ["100 Feet Rd", "Tansi Nagar Main Rd", "Vijaya Nagar", "Dhandeeswaram Main Rd"],
        "Guindy": ["Race Course Rd", "Five Furlong Rd", "MKN Rd", "Industrial Estate Rd"],
        "Perambur": ["Paper Mills Rd", "Madhavaram High Rd", "Patel Rd", "Perambur High Rd"],
        "Ambattur": ["OT Main Rd", "MTH Rd", "Venkatapuram Main Rd", "Industrial Estate Rd"],
        "Porur": ["Mount Poonamallee Rd", "Arcot Rd", "Kundrathur Main Rd", "Lakshmi Nagar"],
        "Kodambakkam": ["Arcot Rd", "Trustpuram Main Rd", "United India Colony", "Rangarajapuram Main Rd"],
        "Nungambakkam": ["College Rd", "Sterling Rd", "Village Rd", "Tank Bund Rd"],
        "Mylapore": ["RK Mutt Rd", "Luz Church Rd", "Kutchery Rd", "Royapettah High Rd"],
        "Tambaram": ["GST Rd", "Velachery Main Rd", "Mudichur Rd", "MES Rd"],
    }

    connection_types = [
        "Domestic",
        "Domestic",
        "Domestic",
        "Commercial",
        "Small Business",
    ]

    def identity_for_row(row):
        key = str(row.get("Consumer_ID", ""))
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        seed = int(digest[:12], 16)

        area = str(row.get("Area", "Chennai"))
        streets = area_streets.get(
            area,
            ["Main Rd", "1st Cross St", "2nd Main Rd", "Market Rd"],
        )

        name = demo_names[seed % len(demo_names)]
        street = streets[(seed // 7) % len(streets)]
        door = (seed % 148) + 1
        cross = ((seed // 31) % 4) + 1

        address = f"No.{door}, {cross} Cross, {street}, {area}"

        connection = connection_types[
            (seed // 11) % len(connection_types)
        ]

        meter_no = f"MTR-{(seed % 900000) + 100000}"

        return pd.Series(
            [name, address, connection, meter_no]
        )

    identity = out.apply(
        identity_for_row,
        axis=1,
    )

    identity.columns = [
        "Consumer_Name",
        "Short_Address",
        "Connection_Type",
        "Meter_No",
    ]

    for c in identity.columns:
        if c not in out.columns:
            out[c] = identity[c]

    return out


df = recover_source_index(
    df,
    evaluation_df,
)

df = enrich_demo_identity(df)


def queue_consumer_open(consumer_id, source="CONTROL ROOM"):
    """
    Queue a cross-page navigation. We change the navigation widget on the next
    rerun so Streamlit does not complain about mutating an already-rendered widget.
    """
    st.session_state["wg_pending_page"] = "CONSUMER DESK"
    st.session_state["wg_open_consumer"] = str(consumer_id)
    st.session_state["wg_open_source"] = str(source)


def log_operator_event(message, level="INFO"):
    if "wg_event_log" not in st.session_state:
        st.session_state["wg_event_log"] = []

    stamp = datetime.now().strftime("%H:%M:%S")

    st.session_state["wg_event_log"].insert(
        0,
        {
            "time": stamp,
            "level": level,
            "message": str(message),
        },
    )

    st.session_state["wg_event_log"] = st.session_state["wg_event_log"][:12]


def case_status_for(consumer_id):
    if "wg_case_status" not in st.session_state:
        st.session_state["wg_case_status"] = {}

    return st.session_state["wg_case_status"].get(
        str(consumer_id),
        "FLAGGED",
    )


def set_case_status(consumer_id, status):
    if "wg_case_status" not in st.session_state:
        st.session_state["wg_case_status"] = {}

    st.session_state["wg_case_status"][str(consumer_id)] = str(status)


def _numeric_series(data, column):
    if column not in data.columns:
        return pd.Series(dtype=float)

    return pd.to_numeric(
        data[column],
        errors="coerce",
    ).dropna()


def percentile_score(data, column, value, transform=None):
    """
    Relative evidence score from 0-100.
    This is NOT model probability/confidence.
    """
    series = _numeric_series(
        data,
        column,
    )

    if series.empty or pd.isna(value):
        return 0.0

    try:
        value = float(value)
    except Exception:
        return 0.0

    if transform == "abs":
        series = series.abs()
        value = abs(value)

    elif transform == "negative":
        # More negative values become stronger evidence.
        series = -series
        value = -value

    return float(
        (series <= value).mean()
        * 100
    )


def build_evidence_fingerprint(row, data):
    items = [
        (
            "Near-zero reading frequency",
            "zero_ratio",
            None,
        ),
        (
            "Usage volatility",
            "variation",
            None,
        ),
        (
            "Day-to-day change",
            "avg_change",
            "abs",
        ),
        (
            "Sudden drop signal",
            "max_drop",
            "abs",
        ),
        (
            "Recent decline",
            "recent_change_ratio",
            "negative",
        ),
        (
            "Long-term decline",
            "long_term_change",
            "negative",
        ),
    ]

    output = []

    for label, column, transform in items:
        raw = pd.to_numeric(
            row.get(
                column,
                np.nan,
            ),
            errors="coerce",
        )

        score = percentile_score(
            data,
            column,
            raw,
            transform=transform,
        )

        output.append(
            {
                "label": label,
                "column": column,
                "value": raw,
                "score": score,
            }
        )

    return output


def find_low_risk_peer(row, data):
    """
    Finds a low-risk consumer with similar behavioural aggregates.
    Used as a comparison aid, not as a claim that the peer is theft-free.
    """
    current_id = str(
        row.get(
            "Consumer_ID",
            "",
        )
    )

    pool = data[
        data["Consumer_ID"].astype(str)
        != current_id
    ].copy()

    # Prefer same area and connection category.
    if "Area" in pool.columns:
        same_area = pool[
            pool["Area"].astype(str)
            == str(row.get("Area", ""))
        ]

        if len(same_area) >= 10:
            pool = same_area

    if "Connection_Type" in pool.columns:
        same_type = pool[
            pool["Connection_Type"].astype(str)
            == str(
                row.get(
                    "Connection_Type",
                    "",
                )
            )
        ]

        if len(same_type) >= 5:
            pool = same_type

    low_risk = pool[
        pd.to_numeric(
            pool["Risk_Score"],
            errors="coerce",
        ) < 30
    ].copy()

    if not low_risk.empty:
        pool = low_risk

    features = [
        c for c in [
            "mean_usage",
            "median_usage",
            "std_usage",
            "variation",
            "zero_ratio",
        ]
        if c in pool.columns
        and c in row.index
    ]

    if not features or pool.empty:
        return None

    distance = pd.Series(
        0.0,
        index=pool.index,
    )

    used = 0

    for feature in features:
        candidate = pd.to_numeric(
            pool[feature],
            errors="coerce",
        )

        target = pd.to_numeric(
            row.get(
                feature,
                np.nan,
            ),
            errors="coerce",
        )

        if pd.isna(target):
            continue

        spread = float(
            candidate.std()
        )

        if (
            pd.isna(spread)
            or spread <= 1e-9
        ):
            spread = 1.0

        distance += (
            (
                candidate.fillna(
                    candidate.median()
                )
                - float(target)
            ).abs()
            / spread
        )

        used += 1

    if used == 0:
        return None

    best_index = distance.idxmin()

    return pool.loc[
        best_index
    ]


def inspection_readiness(row, data):
    """
    Secondary human-review gate to reduce blind escalation.
    It does not replace the model or the field officer.
    """
    risk = float(
        pd.to_numeric(
            row.get(
                "Risk_Score",
                0,
            ),
            errors="coerce",
        )
        or 0
    )

    priority = float(
        pd.to_numeric(
            row.get(
                "Priority_Score",
                0,
            ),
            errors="coerce",
        )
        or 0
    )

    unbilled = float(
        pd.to_numeric(
            row.get(
                "Estimated_Unbilled_Units",
                0,
            ),
            errors="coerce",
        )
        or 0
    )

    fingerprints = build_evidence_fingerprint(
        row,
        data,
    )

    strong_signals = sum(
        item["score"] >= 75
        for item in fingerprints
    )

    unbilled_series = _numeric_series(
        data,
        "Estimated_Unbilled_Units",
    )

    unbilled_pct = (
        float(
            (
                unbilled_series
                <= unbilled
            ).mean()
            * 100
        )
        if not unbilled_series.empty
        else 0.0
    )

    if (
        risk >= 70
        and strong_signals >= 2
        and priority >= 70
    ):
        state = "READY FOR FIELD"
        note = "Multiple independent signals support inspection priority."

    elif (
        risk >= 45
        and (
            strong_signals >= 1
            or unbilled_pct >= 75
        )
    ):
        state = "REVIEW BEFORE DISPATCH"
        note = "Risk is material, but operator review is recommended before field allocation."

    else:
        state = "MONITOR / HOLD"
        note = "Evidence is not strong enough for immediate field escalation."

    return {
        "state": state,
        "note": note,
        "strong_signals": strong_signals,
        "unbilled_percentile": unbilled_pct,
        "risk": risk,
        "priority": priority,
    }


def build_case_evidence_report(
    row,
    energy,
    history,
    peer,
    readiness,
):
    lines = []

    lines.append("WATTGUARD AI — CASE EVIDENCE PACK")
    lines.append("=" * 54)
    lines.append(
        f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    )
    lines.append("")
    lines.append(
        f"Consumer ID: {row.get('Consumer_ID', '')}"
    )
    lines.append(
        f"Consumer Name: {row.get('Consumer_Name', '')}"
    )
    lines.append(
        f"Address: {row.get('Short_Address', '')}"
    )
    lines.append(
        f"Meter: {row.get('Meter_No', '')}"
    )
    lines.append(
        f"Area / Substation / Feeder: "
        f"{row.get('Area', '')} / "
        f"{row.get('Substation', '')} / "
        f"{row.get('Feeder_ID', '')}"
    )
    lines.append("")
    lines.append(
        f"AI Risk Score: {float(row.get('Risk_Score', 0)):.1f}/100"
    )
    lines.append(
        f"Priority Score: {float(row.get('Priority_Score', 0)):.1f}/100"
    )
    lines.append(
        f"Risk Level: {row.get('Risk_Level', '')}"
    )
    lines.append(
        f"Recommended Action: {clean_text(row.get('Action', ''))}"
    )
    lines.append("")
    lines.append(
        f"Billed / Meter-Recorded 30D: "
        f"{energy['billed']:.1f} U"
        if not pd.isna(energy["billed"])
        else "Billed / Meter-Recorded 30D: N/A"
    )
    lines.append(
        f"Estimated Unexplained / Unbilled: "
        f"{energy['suspected']:.1f} U"
    )
    lines.append(
        f"Estimated Total Consumption: "
        f"{energy['total']:.1f} U"
        if not pd.isna(energy["total"])
        else "Estimated Total Consumption: N/A"
    )
    lines.append("")
    lines.append("WHY FLAGGED")
    lines.append(
        str(
            row.get(
                "Why_Flagged",
                "",
            )
        ).replace(
            "|",
            " | ",
        )
    )
    lines.append("")
    lines.append(
        f"Inspection Readiness: {readiness['state']}"
    )
    lines.append(
        f"Strong Behaviour Signals: {readiness['strong_signals']}"
    )
    lines.append(
        f"Unbilled Impact Percentile: "
        f"{readiness['unbilled_percentile']:.1f}%"
    )

    if (
        history is not None
        and not history.empty
    ):
        latest30 = history.tail(
            30
        )

        previous30 = history.iloc[
            -60:-30
        ]

        lines.append("")
        lines.append("LOAD HISTORY")

        lines.append(
            f"Latest 30D Recorded: "
            f"{latest30['Usage'].sum():.1f} U"
        )

        if not previous30.empty:
            previous_total = float(
                previous30[
                    "Usage"
                ].sum()
            )

            latest_total = float(
                latest30[
                    "Usage"
                ].sum()
            )

            difference = (
                latest_total
                - previous_total
            )

            change_pct = (
                difference
                / previous_total
                * 100
                if previous_total > 0
                else np.nan
            )

            lines.append(
                f"Previous 30D Recorded: "
                f"{previous_total:.1f} U"
            )

            lines.append(
                f"30D Difference: "
                f"{difference:+.1f} U"
            )

            if not pd.isna(
                change_pct
            ):
                lines.append(
                    f"30D Change: "
                    f"{change_pct:+.1f}%"
                )

    if peer is not None:
        lines.append("")
        lines.append("LOW-RISK PEER COMPARATOR")
        lines.append(
            f"Peer: {peer.get('Consumer_ID', '')} "
            f"· {peer.get('Consumer_Name', '')}"
        )
        lines.append(
            f"Peer Risk Score: "
            f"{float(peer.get('Risk_Score', 0)):.1f}/100"
        )

    lines.append("")
    lines.append("IMPORTANT")
    lines.append(
        "This is an AI-assisted investigation pack. "
        "A WattGuard alert is not proof of electricity theft. "
        "Estimated unexplained usage requires field verification."
    )
    lines.append(
        "Names, addresses, meter IDs and Chennai topology in this "
        "prototype are synthetic demo data."
    )

    return "\n".join(
        lines
    )

def kpi(value, label, sub="", cls=""):
    return (
        f'<div class="kpi {cls}">'
        f'<div class="v">{value}</div>'
        f'<div class="l">{label}</div>'
        f'<div class="s">{sub}</div>'
        f'</div>'
    )


def risk_badge(level):
    level = str(level).upper()

    if level == "CRITICAL":
        cls = "red"
    elif level in ["HIGH", "WATCH"]:
        cls = "amber"
    elif level == "LOW":
        cls = "green"
    else:
        cls = "blue"

    return f'<span class="badge {cls}">{level}</span>'


def clean_text(value):
    if pd.isna(value):
        return "-"
    return str(value)


def build_area_filter(data, key_prefix):
    areas = sorted(data["Area"].dropna().astype(str).unique().tolist())

    area = st.selectbox(
        "AREA / SECTION",
        ["ALL CHENNAI"] + areas,
        key=f"{key_prefix}_area",
    )

    if area == "ALL CHENNAI":
        filtered = data.copy()
    else:
        filtered = data[data["Area"].astype(str) == area].copy()

    substations = sorted(
        filtered["Substation"].dropna().astype(str).unique().tolist()
    )

    substation = st.selectbox(
        "SUBSTATION",
        ["ALL SUBSTATIONS"] + substations,
        key=f"{key_prefix}_substation",
    )

    if substation != "ALL SUBSTATIONS":
        filtered = filtered[
            filtered["Substation"].astype(str) == substation
        ].copy()

    feeders = sorted(
        filtered["Feeder_ID"].dropna().astype(str).unique().tolist()
    )

    feeder = st.selectbox(
        "FEEDER",
        ["ALL FEEDERS"] + feeders,
        key=f"{key_prefix}_feeder",
    )

    if feeder != "ALL FEEDERS":
        filtered = filtered[
            filtered["Feeder_ID"].astype(str) == feeder
        ].copy()

    return filtered, area, substation, feeder


def calculate_stats(data, tariff):
    total = len(data)

    high = int((data["Risk_Score"] >= 45).sum())
    critical = int((data["Risk_Score"] >= 70).sum())

    unbilled = float(
        data.loc[
            data["Risk_Score"] >= 45,
            "Estimated_Unbilled_Units",
        ]
        .clip(lower=0)
        .sum()
    )

    revenue = unbilled * tariff

    return total, high, critical, unbilled, revenue


def get_source_index(row):
    """
    Returns the original SGCC row index only when a reliable mapping is
    available in wattguard_output.csv.

    Recommended columns:
      Source_Index
      Original_Index
      Original_Consumer_ID

    Old WG-xxxxx IDs also work.
    """

    for col in ["Source_Index", "Original_Index"]:
        if col in row.index:
            value = pd.to_numeric(row[col], errors="coerce")
            if not pd.isna(value):
                return int(value)

    if "Original_Consumer_ID" in row.index:
        original = str(row["Original_Consumer_ID"])
        if original.startswith("WG-"):
            try:
                return int(original.replace("WG-", ""))
            except Exception:
                pass

    current = str(row["Consumer_ID"])
    if current.startswith("WG-"):
        try:
            return int(current.replace("WG-", ""))
        except Exception:
            pass

    return None


def get_history(row):
    # --------------------------------------------------------
    # Web deployment path:
    # use a compact 90-day history file committed to GitHub.
    # --------------------------------------------------------
    if web_history_df is not None:
        consumer_id = str(
            row.get(
                "Consumer_ID",
                "",
            )
        )

        compact = web_history_df[
            web_history_df[
                "Consumer_ID"
            ].astype(str)
            == consumer_id
        ][
            [
                "Date",
                "Usage",
            ]
        ].copy()

        if not compact.empty:
            compact = compact.sort_values(
                "Date"
            )

            compact[
                "30-Day Average"
            ] = (
                compact["Usage"]
                .rolling(
                    window=30,
                    min_periods=1,
                )
                .mean()
            )

            return compact

    # --------------------------------------------------------
    # Local development path:
    # use the original SGCC full.csv if it exists.
    # --------------------------------------------------------
    if raw_df is None:
        return None

    source_index = get_source_index(row)

    if source_index is None:
        return None

    if source_index not in raw_df.index:
        return None

    raw_row = raw_df.loc[source_index]

    records = []

    for column in raw_df.columns:
        date_value = pd.to_datetime(
            column,
            errors="coerce",
        )

        if pd.isna(date_value):
            continue

        usage_value = pd.to_numeric(
            raw_row[column],
            errors="coerce",
        )

        if pd.isna(usage_value):
            continue

        records.append(
            {
                "Date": date_value,
                "Usage": float(
                    usage_value
                ),
            }
        )

    if not records:
        return None

    history = (
        pd.DataFrame(
            records
        )
        .sort_values(
            "Date"
        )
    )

    history[
        "30-Day Average"
    ] = (
        history["Usage"]
        .rolling(
            window=30,
            min_periods=1,
        )
        .mean()
    )

    return history



def enrich_energy_accounting(data):
    """
    Adds demo energy-accounting columns without pretending that SGCC contains
    official utility bills.

    Preferred source:
      Billed_Units_30D / Recorded_Units_30D if already present.

    Fallback:
      mean_usage * 30 = a 30-day meter-recorded equivalent derived from the
      engineered SGCC feature already present in wattguard_output.csv.

    Estimated_Unbilled_Units remains the WattGuard prototype estimate.
    """
    out = data.copy()

    if "Billed_Units_30D" in out.columns:
        billed = pd.to_numeric(
            out["Billed_Units_30D"],
            errors="coerce",
        )
    elif "Recorded_Units_30D" in out.columns:
        billed = pd.to_numeric(
            out["Recorded_Units_30D"],
            errors="coerce",
        )
    elif "mean_usage" in out.columns:
        billed = (
            pd.to_numeric(
                out["mean_usage"],
                errors="coerce",
            )
            .clip(lower=0)
            * 30
        )
    else:
        billed = pd.Series(
            np.nan,
            index=out.index,
            dtype=float,
        )

    unbilled = (
        pd.to_numeric(
            out["Estimated_Unbilled_Units"],
            errors="coerce",
        )
        .fillna(0)
        .clip(lower=0)
    )

    out["Billed_Units_30D"] = billed.round(1)
    out["Estimated_Theft_Unbilled_Units_30D"] = unbilled.round(1)

    total = billed + unbilled
    out["Estimated_Total_Consumed_Units_30D"] = total.round(1)

    coverage = np.where(
        total > 0,
        (billed / total) * 100,
        np.nan,
    )

    out["Estimated_Billing_Coverage_Pct"] = pd.Series(
        coverage,
        index=out.index,
    ).round(1)

    return out


def energy_breakdown(row):
    """
    Returns a consumer-level 30-day accounting view.

    If exact raw-history linkage exists, use the most recent 30 recorded days.
    Otherwise use the 30-day recorded equivalent prepared above.
    """
    history = get_history(row)

    if history is not None and not history.empty:
        billed = float(
            history.tail(30)["Usage"]
            .clip(lower=0)
            .sum()
        )
        source = "Recent 30-day meter history"
    else:
        billed_value = pd.to_numeric(
            row.get("Billed_Units_30D", np.nan),
            errors="coerce",
        )

        billed = (
            float(billed_value)
            if not pd.isna(billed_value)
            else np.nan
        )

        source = "30-day meter-recorded equivalent"

    suspected = max(
        0.0,
        float(
            pd.to_numeric(
                row.get(
                    "Estimated_Unbilled_Units",
                    0,
                ),
                errors="coerce",
            )
            or 0
        ),
    )

    total = (
        billed + suspected
        if not pd.isna(billed)
        else np.nan
    )

    coverage = (
        billed / total * 100
        if not pd.isna(total) and total > 0
        else np.nan
    )

    return {
        "billed": billed,
        "suspected": suspected,
        "total": total,
        "coverage": coverage,
        "source": source,
    }


df = enrich_energy_accounting(df)


def field_note(row):
    reasons = str(row["Why_Flagged"]).replace("|", ", ")

    return (
        f"{row['Consumer_ID']} in {row['Area']} is ranked for field review because "
        f"its recorded consumption behaviour differs from the reference pattern. "
        f"Main indicators: {reasons}. Estimated unexplained consumption is "
        f"{row['Estimated_Unbilled_Units']:.1f} units. "
        f"Recommended action: {str(row['Action']).lower()}."
    )


def feeder_summary(data, tariff):
    if data.empty:
        return pd.DataFrame()

    grouped = (
        data.groupby(["Area", "Substation", "Feeder_ID"], dropna=False)
        .agg(
            Consumers=("Consumer_ID", "count"),
            Avg_Risk=("Risk_Score", "mean"),
            Max_Risk=("Risk_Score", "max"),
            Recorded_Billed_30D=(
                "Billed_Units_30D",
                lambda s: s.sum(min_count=1),
            ),
            Possible_Unbilled=("Estimated_Unbilled_Units", "sum"),
            Estimated_Total_30D=(
                "Estimated_Total_Consumed_Units_30D",
                lambda s: s.sum(min_count=1),
            ),
        )
        .reset_index()
    )

    alert_counts = (
        data.assign(Alert=(data["Risk_Score"] >= 45).astype(int))
        .groupby(["Area", "Substation", "Feeder_ID"], dropna=False)["Alert"]
        .sum()
        .reset_index()
    )

    critical_counts = (
        data.assign(Critical=(data["Risk_Score"] >= 70).astype(int))
        .groupby(["Area", "Substation", "Feeder_ID"], dropna=False)["Critical"]
        .sum()
        .reset_index()
    )

    grouped = grouped.merge(
        alert_counts,
        on=["Area", "Substation", "Feeder_ID"],
        how="left",
    )

    grouped = grouped.merge(
        critical_counts,
        on=["Area", "Substation", "Feeder_ID"],
        how="left",
    )

    grouped["Revenue_At_Risk"] = (
        grouped["Possible_Unbilled"].clip(lower=0) * tariff
    )

    grouped["Billing_Coverage_Pct"] = np.where(
        grouped["Estimated_Total_30D"] > 0,
        (
            grouped["Recorded_Billed_30D"]
            / grouped["Estimated_Total_30D"]
        ) * 100,
        np.nan,
    )

    grouped["Avg_Risk"] = grouped["Avg_Risk"].round(1)
    grouped["Max_Risk"] = grouped["Max_Risk"].round(1)
    grouped["Recorded_Billed_30D"] = grouped["Recorded_Billed_30D"].round(1)
    grouped["Possible_Unbilled"] = grouped["Possible_Unbilled"].round(1)
    grouped["Estimated_Total_30D"] = grouped["Estimated_Total_30D"].round(1)
    grouped["Billing_Coverage_Pct"] = grouped["Billing_Coverage_Pct"].round(1)
    grouped["Revenue_At_Risk"] = grouped["Revenue_At_Risk"].round(0)

    return grouped.sort_values(
        ["Critical", "Alert", "Max_Risk"],
        ascending=False,
    )


# ============================================================
# HEADER
# ============================================================

now_text = datetime.now().strftime("%d-%m-%Y %H:%M")

render_html(
    f"""
<div class="ctrl-head">
    <div class="ctrl-brand">
        <div class="ctrl-logo">WG</div>
        <div>
            <div class="ctrl-title">WattGuard AI — Chennai Distribution Loss Control Centre</div>
            <div class="ctrl-sub">AI-ASSISTED POWER THEFT & UNBILLED LOAD INVESTIGATION PLATFORM</div>
        </div>
    </div>
    <div class="online">● <strong>DEMO SYSTEM ONLINE</strong> · ANALYSIS READY</div>
</div>
<div class="ticker">
    <span>REGION <strong>CHENNAI DEMO GRID</strong></span>
    <span>DATA SOURCE <strong>SGCC PUBLIC DATASET</strong></span>
    <span>MODEL <strong>RANDOM FOREST V3</strong></span>
    <span>ROC-AUC <strong>0.764</strong></span>
    <span>LAST VIEW REFRESH <strong>{now_text}</strong></span>
</div>
"""
)

# ============================================================
# NAVIGATION
# ============================================================

NAV_OPTIONS = [
    "CONTROL ROOM",
    "CONSUMER DESK",
    "SUBSTATION MIMIC",
    "FIELD QUEUE",
    "MODEL STATUS",
]

# ------------------------------------------------------------
# URL action handler
# Makes HTML alarm cards behave like real clickable case cards.
# ------------------------------------------------------------

requested_consumer = None
requested_source = None

try:
    requested_consumer = st.query_params.get(
        "open_consumer"
    )
    requested_source = st.query_params.get(
        "open_source"
    )
except Exception:
    requested_consumer = None
    requested_source = None

if requested_consumer:
    if isinstance(
        requested_consumer,
        list,
    ):
        requested_consumer = requested_consumer[0]

    if isinstance(
        requested_source,
        list,
    ):
        requested_source = requested_source[0]

    st.session_state["wg_open_consumer"] = str(
        requested_consumer
    )

    st.session_state["wg_open_source"] = (
        str(requested_source)
        if requested_source
        else "CLICKABLE CARD"
    )

    st.session_state["main_nav"] = "CONSUMER DESK"

    try:
        st.query_params.clear()
    except Exception:
        try:
            st.experimental_set_query_params()
        except Exception:
            pass

if "wg_pending_page" in st.session_state:
    st.session_state["main_nav"] = st.session_state.pop(
        "wg_pending_page"
    )

if "main_nav" not in st.session_state:
    st.session_state["main_nav"] = "CONTROL ROOM"

page = st.radio(
    "Navigation",
    NAV_OPTIONS,
    horizontal=True,
    label_visibility="collapsed",
    key="main_nav",
)

# ============================================================
# PAGE 1 — CONTROL ROOM
# ============================================================

if page == "CONTROL ROOM":

    st.markdown(
        '<div class="ops-label">CHENNAI DISTRIBUTION CONTROL / OPERATIONS OVERVIEW</div>',
        unsafe_allow_html=True,
    )

    filter_col1, filter_col2, filter_col3, tariff_col = st.columns(
        [1.1, 1.1, 1.1, 0.8]
    )

    with filter_col1:
        areas = sorted(df["Area"].dropna().astype(str).unique().tolist())
        selected_area = st.selectbox(
            "AREA / SECTION",
            ["ALL CHENNAI"] + areas,
            key="control_area",
        )

    area_df = (
        df.copy()
        if selected_area == "ALL CHENNAI"
        else df[df["Area"].astype(str) == selected_area].copy()
    )

    with filter_col2:
        substations = sorted(
            area_df["Substation"].dropna().astype(str).unique().tolist()
        )
        selected_substation = st.selectbox(
            "SUBSTATION",
            ["ALL SUBSTATIONS"] + substations,
            key="control_substation",
        )

    if selected_substation != "ALL SUBSTATIONS":
        area_df = area_df[
            area_df["Substation"].astype(str) == selected_substation
        ].copy()

    with filter_col3:
        feeders = sorted(
            area_df["Feeder_ID"].dropna().astype(str).unique().tolist()
        )
        selected_feeder = st.selectbox(
            "FEEDER",
            ["ALL FEEDERS"] + feeders,
            key="control_feeder",
        )

    if selected_feeder != "ALL FEEDERS":
        area_df = area_df[
            area_df["Feeder_ID"].astype(str) == selected_feeder
        ].copy()

    with tariff_col:
        tariff = st.number_input(
            "₹ / UNIT",
            min_value=1.0,
            max_value=20.0,
            value=DEFAULT_TARIFF,
            step=0.5,
            key="control_tariff",
        )

    display_area = (
        "ALL CHENNAI"
        if selected_area == "ALL CHENNAI"
        else selected_area.upper()
    )

    display_substation = (
        "ALL"
        if selected_substation == "ALL SUBSTATIONS"
        else selected_substation
    )

    display_feeder = (
        "ALL"
        if selected_feeder == "ALL FEEDERS"
        else selected_feeder
    )

    st.markdown(
        f"""
<div class="context-strip">
    <div class="context-box">
        <div class="k">Active Area</div>
        <div class="v">{display_area}</div>
    </div>
    <div class="context-box">
        <div class="k">Substation</div>
        <div class="v">{display_substation}</div>
    </div>
    <div class="context-box">
        <div class="k">Feeder</div>
        <div class="v">{display_feeder}</div>
    </div>
    <div class="context-box">
        <div class="k">Mode</div>
        <div class="v">INVESTIGATION / DEMO</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    total, high, critical, unbilled, revenue = calculate_stats(
        area_df,
        tariff,
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.markdown(
        kpi(
            f"{total:,}",
            "Consumers monitored",
            display_area,
            "blue",
        ),
        unsafe_allow_html=True,
    )

    c2.markdown(
        kpi(
            f"{high:,}",
            "Active alerts",
            "Risk score ≥ 45",
            "amber",
        ),
        unsafe_allow_html=True,
    )

    c3.markdown(
        kpi(
            f"{critical:,}",
            "Critical alerts",
            "Risk score ≥ 70",
            "red",
        ),
        unsafe_allow_html=True,
    )

    c4.markdown(
        kpi(
            f"{unbilled:,.0f}",
            "Possible unbilled units",
            "Prototype estimate",
            "green",
        ),
        unsafe_allow_html=True,
    )

    c5.markdown(
        kpi(
            f"₹{revenue:,.0f}",
            "Revenue at risk",
            f"At ₹{tariff:.1f}/unit",
            "amber",
        ),
        unsafe_allow_html=True,
    )

    recorded_30d = float(
        area_df["Billed_Units_30D"].sum(min_count=1)
    ) if area_df["Billed_Units_30D"].notna().any() else np.nan

    estimated_total_30d = float(
        area_df["Estimated_Total_Consumed_Units_30D"].sum(min_count=1)
    ) if area_df["Estimated_Total_Consumed_Units_30D"].notna().any() else np.nan

    billing_coverage = (
        recorded_30d / estimated_total_30d * 100
        if not pd.isna(recorded_30d)
        and not pd.isna(estimated_total_30d)
        and estimated_total_30d > 0
        else np.nan
    )

    recorded_text = (
        f"{recorded_30d:,.0f} U"
        if not pd.isna(recorded_30d)
        else "N/A"
    )

    total_text = (
        f"{estimated_total_30d:,.0f} U"
        if not pd.isna(estimated_total_30d)
        else "N/A"
    )

    coverage_text = (
        f"{billing_coverage:.1f}%"
        if not pd.isna(billing_coverage)
        else "N/A"
    )

    render_html(
        f"""
<div class="energy-strip">
    <div class="energy-box">
        <div class="energy-k">Billed / meter-recorded · 30D</div>
        <div class="energy-v">{recorded_text}</div>
        <div class="energy-s">Consumption visible to the billing/meter stream</div>
    </div>
    <div class="energy-box red">
        <div class="energy-k">Estimated theft / unbilled · 30D</div>
        <div class="energy-v">{unbilled:,.0f} U</div>
        <div class="energy-s">Unexplained usage estimate — inspection required</div>
    </div>
    <div class="energy-box amber">
        <div class="energy-k">Estimated total consumed · 30D</div>
        <div class="energy-v">{total_text}</div>
        <div class="energy-s">Billed/recorded + estimated unexplained usage</div>
    </div>
    <div class="energy-box green">
        <div class="energy-k">Estimated billing coverage</div>
        <div class="energy-v">{coverage_text}</div>
        <div class="energy-s">Share of estimated total visible to billing</div>
    </div>
</div>
"""
    )


    # --------------------------------------------------------
    # WattGuard decision rail — product identity
    # --------------------------------------------------------

    top_case = (
        area_df.sort_values(
            "Priority_Score",
            ascending=False,
        ).iloc[0]
        if not area_df.empty
        else None
    )

    if top_case is not None:
        top_reason = str(
            top_case["Why_Flagged"]
        ).split("|")[0].strip()

        render_html(
            f"""
<div class="command-rail">
    <div class="command-step">
        <div class="cs-num">01 / DETECT</div>
        <div class="cs-title">AI RISK</div>
        <div class="cs-value">{top_case['Risk_Score']:.1f}/100</div>
        <div class="cs-sub">{top_case['Consumer_ID']} · highest current priority</div>
    </div>
    <div class="command-step">
        <div class="cs-num">02 / EXPLAIN</div>
        <div class="cs-title">PRIMARY SIGNAL</div>
        <div class="cs-value" style="font-size:11px;">{top_reason}</div>
        <div class="cs-sub">Behavioural evidence, not accusation</div>
    </div>
    <div class="command-step">
        <div class="cs-num">03 / QUANTIFY</div>
        <div class="cs-title">EST. UNBILLED</div>
        <div class="cs-value">{top_case['Estimated_Unbilled_Units']:,.0f} U</div>
        <div class="cs-sub">Prototype unexplained-usage estimate</div>
    </div>
    <div class="command-step">
        <div class="cs-num">04 / PRIORITIZE</div>
        <div class="cs-title">PRIORITY SCORE</div>
        <div class="cs-value">{top_case['Priority_Score']:.1f}/100</div>
        <div class="cs-sub">Risk + estimated impact ranking</div>
    </div>
    <div class="command-step">
        <div class="cs-num">05 / ACT</div>
        <div class="cs-title">FIELD ACTION</div>
        <div class="cs-value" style="font-size:12px;">{clean_text(top_case['Action'])}</div>
        <div class="cs-sub">Human field verification closes the case</div>
    </div>
</div>
"""
        )

    st.write("")

    left, right = st.columns([1.65, 1])

    with left:
        st.markdown(
            """
<div class="panel">
    <div class="panel-head">
        <div class="panel-title">ACTIVE ALARM REGISTER</div>
        <div class="panel-meta">PRIORITY-RANKED INVESTIGATION CASES</div>
    </div>
""",
            unsafe_allow_html=True,
        )

        if area_df.empty:
            st.info("No consumers match the selected filter.")
        else:
            capacity = st.slider(
                "FIELD TEAM CAPACITY THIS SHIFT",
                min_value=5,
                max_value=max(5, min(100, len(area_df))),
                value=min(25, max(5, len(area_df))),
                step=5,
                key="control_capacity",
            )

            alarm_queue = (
                area_df.sort_values(
                    "Priority_Score",
                    ascending=False,
                )
                .head(capacity)
                .copy()
            )

            st.caption(
                "Click any consumer row to open the complete Consumer Desk case file."
            )

            alarm_event = st.dataframe(
                alarm_queue[
                    [
                        "Consumer_ID",
                        "Consumer_Name",
                        "Short_Address",
                        "Area",
                        "Substation",
                        "Feeder_ID",
                        "Risk_Score",
                        "Risk_Level",
                        "Billed_Units_30D",
                        "Estimated_Unbilled_Units",
                        "Estimated_Total_Consumed_Units_30D",
                        "Priority_Score",
                        "Action",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
                height=465,
                on_select="rerun",
                selection_mode="single-row",
                key="control_alarm_register",
            )

            selected_rows = list(
                getattr(
                    getattr(
                        alarm_event,
                        "selection",
                        None,
                    ),
                    "rows",
                    [],
                )
            )

            if selected_rows:
                selected_alarm = alarm_queue.iloc[
                    selected_rows[0]
                ]

                queue_consumer_open(
                    selected_alarm["Consumer_ID"],
                    source="ALARM REGISTER",
                )

                log_operator_event(
                    f"Opened {selected_alarm['Consumer_ID']} "
                    f"({selected_alarm['Consumer_Name']}) from alarm register."
                )

                st.rerun()


        # Guaranteed quick-open control in addition to row click.
        if not area_df.empty:
            quick_cases = (
                area_df.sort_values(
                    "Priority_Score",
                    ascending=False,
                )
                .head(100)
                .copy()
            )

            quick_cases["_open_label"] = (
                quick_cases["Consumer_ID"].astype(str)
                + " · "
                + quick_cases["Consumer_Name"].astype(str)
                + " · "
                + quick_cases["Area"].astype(str)
            )

            quick_label = st.selectbox(
                "QUICK CASE OPEN",
                ["-- SELECT CASE --"]
                + quick_cases["_open_label"].tolist(),
                key="control_quick_case",
            )

            if st.button(
                "OPEN IN CONSUMER DESK →",
                use_container_width=True,
                key="control_open_case_button",
            ):
                if quick_label == "-- SELECT CASE --":
                    st.warning("Select a consumer case first.")
                else:
                    quick_row = quick_cases[
                        quick_cases["_open_label"] == quick_label
                    ].iloc[0]

                    queue_consumer_open(
                        quick_row["Consumer_ID"],
                        source="QUICK CASE OPEN",
                    )

                    log_operator_event(
                        f"Opened {quick_row['Consumer_ID']} "
                        f"({quick_row['Consumer_Name']}) using Quick Case Open."
                    )

                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        with st.expander(
            "TOP LIVE ALARMS  ·  CLICK TO OPEN / CLOSE",
            expanded=True,
        ):

            render_html(
                """
<div class="interaction-note">
Every alarm card below is active. Click the card itself to open that exact
consumer directly in Consumer Desk.
</div>
"""
            )

            top5 = (
                area_df.sort_values(
                    "Priority_Score",
                    ascending=False,
                )
                .head(5)
            )

            if top5.empty:
                st.caption(
                    "No cases for this filter."
                )

            else:
                for _, row in top5.iterrows():

                    risk = float(
                        row[
                            "Risk_Score"
                        ]
                    )

                    if risk >= 70:
                        alarm_class = "alarm"
                        bar_class = "riskbar"

                    elif risk >= 45:
                        alarm_class = "alarm amber"
                        bar_class = "riskbar amber"

                    else:
                        alarm_class = "alarm green"
                        bar_class = "riskbar green"

                    width = max(
                        2,
                        min(
                            100,
                            risk,
                        ),
                    )

                    consumer_id = str(
                        row[
                            "Consumer_ID"
                        ]
                    )

                    consumer_name = str(
                        row.get(
                            "Consumer_Name",
                            "",
                        )
                    )

                    render_html(
                        f"""
<a
    class="alarm-link"
    href="?open_consumer={consumer_id}&amp;open_source=TOP_LIVE_ALARM"
    target="_self"
    title="Open {consumer_id} in Consumer Desk"
>
    <div class="{alarm_class}">
        <div style="display:flex;justify-content:space-between;gap:8px;">
            <span class="alarm-id">
                {consumer_id} · {consumer_name}
            </span>
            {risk_badge(row['Risk_Level'])}
        </div>

        <div class="alarm-meta">
            {row['Area']} · {row['Substation']} · {row['Feeder_ID']} ·
            RISK {row['Risk_Score']:.1f}
        </div>

        <div class="alarm-meta">
            BILLED/REC {row['Billed_Units_30D']:.1f} U ·
            EST UNBILLED {row['Estimated_Unbilled_Units']:.1f} U ·
            EST TOTAL {row['Estimated_Total_Consumed_Units_30D']:.1f} U
        </div>

        <div class="{bar_class}">
            <div style="width:{width}%"></div>
        </div>

        <div class="click-hint">
            OPEN CASE → CONSUMER DESK
        </div>
    </div>
</a>
"""
                    )

        with st.expander(
            "RISK PORTFOLIO  ·  CLICK TO OPEN / CLOSE",
            expanded=True,
        ):

            risk_counts = (
                area_df[
                    "Risk_Level"
                ]
                .astype(
                    str
                )
                .str.upper()
                .value_counts()
                .reindex(
                    [
                        "CRITICAL",
                        "HIGH",
                        "WATCH",
                        "LOW",
                    ]
                )
                .fillna(
                    0
                )
            )

            st.bar_chart(
                risk_counts,
                height=245,
            )

            st.caption(
                "The chart follows the current Area / Substation / Feeder filters."
            )



    # --------------------------------------------------------
    # Capacity-aware dispatch intelligence
    # --------------------------------------------------------

    if not area_df.empty:
        ranked_for_dispatch = area_df.sort_values(
            "Priority_Score",
            ascending=False,
        ).copy()

        dispatch_capacity = min(
            int(
                st.session_state.get(
                    "control_capacity",
                    min(25, len(ranked_for_dispatch)),
                )
            ),
            len(ranked_for_dispatch),
        )

        dispatch_cases = ranked_for_dispatch.head(
            dispatch_capacity
        )

        all_suspected_units = float(
            ranked_for_dispatch[
                "Estimated_Unbilled_Units"
            ]
            .clip(lower=0)
            .sum()
        )

        captured_units = float(
            dispatch_cases[
                "Estimated_Unbilled_Units"
            ]
            .clip(lower=0)
            .sum()
        )

        capture_pct = (
            captured_units / all_suspected_units * 100
            if all_suspected_units > 0
            else 0.0
        )

        critical_total = int(
            (
                ranked_for_dispatch[
                    "Risk_Score"
                ] >= 70
            ).sum()
        )

        critical_captured = int(
            (
                dispatch_cases[
                    "Risk_Score"
                ] >= 70
            ).sum()
        )

        alert_concentration = (
            (
                dispatch_cases[
                    "Risk_Score"
                ] >= 45
            ).mean()
            * 100
            if len(dispatch_cases)
            else 0.0
        )

        render_html(
            f"""
<div class="dispatch-shell">
    <div class="dispatch-head">
        <div>
            <div class="dispatch-title">CAPACITY-AWARE DISPATCH OPTIMIZER</div>
            <div class="dispatch-sub">
                WattGuard does not only rank risk — it adapts the queue to the field team's actual inspection capacity.
            </div>
        </div>
        <div class="dispatch-mode">
            TOP-{dispatch_capacity} MODE<br>
            DECISION SUPPORT ACTIVE
        </div>
    </div>

    <div class="dispatch-grid">
        <div class="dispatch-cell">
            <div class="dispatch-k">Inspections available</div>
            <div class="dispatch-v">{dispatch_capacity}</div>
            <div class="dispatch-s">Current shift capacity</div>
        </div>

        <div class="dispatch-cell">
            <div class="dispatch-k">Critical cases captured</div>
            <div class="dispatch-v">{critical_captured}/{critical_total}</div>
            <div class="dispatch-s">Critical cases inside today's queue</div>
        </div>

        <div class="dispatch-cell">
            <div class="dispatch-k">Suspected units covered</div>
            <div class="dispatch-v">{capture_pct:.1f}%</div>
            <div class="dispatch-s">{captured_units:,.0f} U concentrated in selected cases</div>
        </div>

        <div class="dispatch-cell">
            <div class="dispatch-k">Alert concentration</div>
            <div class="dispatch-v">{alert_concentration:.1f}%</div>
            <div class="dispatch-s">Share of dispatch queue already above alert threshold</div>
        </div>
    </div>
</div>
"""
        )

    export_cols = [
        "Consumer_ID",
        "Consumer_Name",
        "Short_Address",
        "Connection_Type",
        "Meter_No",
        "Area",
        "Substation",
        "Feeder_ID",
        "Estimated_Total_Consumed_Units_30D",
        "Billed_Units_30D",
        "Estimated_Unbilled_Units",
        "Risk_Score",
        "Risk_Level",
        "Priority_Score",
        "Action",
    ]

    enriched_export = (
        area_df[
            [c for c in export_cols if c in area_df.columns]
        ]
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "EXPORT CURRENT CONSUMER ACCOUNT DATA",
        enriched_export,
        file_name="wattguard_consumer_accounts.csv",
        mime="text/csv",
        key="export_enriched_accounts",
    )


    st.markdown(
        '<div class="ops-label">OPERATOR EVENT CONSOLE</div>',
        unsafe_allow_html=True,
    )

    events = st.session_state.get(
        "wg_event_log",
        [],
    )

    if not events:
        events = [
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "level": "INFO",
                "message": "Control room session started. Awaiting operator action.",
            }
        ]

    console_lines = []

    for item in events[:6]:
        level = str(
            item.get("level", "INFO")
        ).upper()

        cls = (
            "red"
            if level == "CRITICAL"
            else "amber"
            if level in ["WARN", "WARNING"]
            else "green"
        )

        console_lines.append(
            f'<div>'
            f'[{item.get("time", "--:--:--")}] '
            f'<span class="{cls}">{level}</span> · '
            f'{item.get("message", "")}'
            f'</div>'
        )

    render_html(
        '<div class="operator-console">'
        + "".join(console_lines)
        + "</div>"
    )

    st.markdown(
        '<div class="ops-label">FEEDER LOSS PRIORITY</div>',
        unsafe_allow_html=True,
    )

    feeder_table = feeder_summary(
        area_df,
        tariff,
    )

    if not feeder_table.empty:
        st.dataframe(
            feeder_table[
                [
                    "Area",
                    "Substation",
                    "Feeder_ID",
                    "Consumers",
                    "Alert",
                    "Critical",
                    "Avg_Risk",
                    "Max_Risk",
                    "Recorded_Billed_30D",
                    "Possible_Unbilled",
                    "Estimated_Total_30D",
                    "Billing_Coverage_Pct",
                    "Revenue_At_Risk",
                ]
            ].rename(
                columns={
                    "Alert": "Alerts",
                    "Critical": "Critical",
                    "Avg_Risk": "Avg Risk",
                    "Max_Risk": "Max Risk",
                    "Recorded_Billed_30D": "Billed/Recorded 30D",
                    "Possible_Unbilled": "Est. Theft/Unbilled",
                    "Estimated_Total_30D": "Est. Total Used",
                    "Billing_Coverage_Pct": "Billing Coverage %",
                    "Revenue_At_Risk": "₹ Revenue Risk",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

# ============================================================
# PAGE 2 — CONSUMER DESK
# ============================================================

elif page == "CONSUMER DESK":

    back_col, case_col = st.columns(
        [0.9, 3.1]
    )

    with back_col:
        if st.button(
            "← CONTROL ROOM",
            use_container_width=True,
            key="consumer_back_control",
        ):
            st.session_state[
                "main_nav"
            ] = "CONTROL ROOM"

            log_operator_event(
                "Returned to Control Room from Consumer Desk."
            )

            st.rerun()

    with case_col:
        st.caption(
            "Consumer Desk · click-through investigation workspace"
        )

    opened_consumer = st.session_state.pop(
        "wg_open_consumer",
        None,
    )

    opened_source = st.session_state.pop(
        "wg_open_source",
        None,
    )

    if opened_consumer is not None:
        match = df[
            df["Consumer_ID"].astype(str)
            == str(opened_consumer)
        ]

        if not match.empty:
            opened_row = match.iloc[0]

            # These keys are set before the widgets are instantiated.
            st.session_state["consumer_area"] = str(
                opened_row["Area"]
            )

            # Reset the selector so the new target becomes visible.
            if "consumer_selector" in st.session_state:
                del st.session_state["consumer_selector"]

            log_operator_event(
                f"Consumer Desk loaded {opened_consumer} "
                f"from {opened_source or 'navigation'}."
            )

    st.markdown(
        '<div class="ops-label">CONSUMER INVESTIGATION DESK / INDIVIDUAL LOAD ACCOUNT</div>',
        unsafe_allow_html=True,
    )

    f1, f2 = st.columns([1, 2])

    with f1:
        consumer_area = st.selectbox(
            "AREA",
            ["ALL CHENNAI"]
            + sorted(
                df["Area"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            ),
            key="consumer_area",
        )

    consumer_pool = (
        df.copy()
        if consumer_area == "ALL CHENNAI"
        else df[
            df["Area"].astype(str) == consumer_area
        ].copy()
    )

    consumer_pool = consumer_pool.sort_values(
        "Priority_Score",
        ascending=False,
    )

    consumer_pool["Selector_Label"] = (
        consumer_pool["Consumer_ID"].astype(str)
        + "  ·  "
        + consumer_pool["Consumer_Name"].astype(str)
        + "  ·  "
        + consumer_pool["Area"].astype(str)
    )

    with f2:
        selector_options = (
            ["-- SELECT CONSUMER --"]
            + consumer_pool["Selector_Label"].tolist()
        )

        default_selector_index = 0

        if opened_consumer is not None:
            target_matches = consumer_pool[
                consumer_pool["Consumer_ID"].astype(str)
                == str(opened_consumer)
            ]

            if not target_matches.empty:
                target_label = target_matches.iloc[0][
                    "Selector_Label"
                ]

                if target_label in selector_options:
                    default_selector_index = selector_options.index(
                        target_label
                    )

        selected_label = st.selectbox(
            "CONSUMER / SERVICE CONNECTION",
            selector_options,
            index=default_selector_index,
            key="consumer_selector",
        )

    if selected_label == "-- SELECT CONSUMER --":
        st.info(
            "Choose a consumer above to open the consumer profile, "
            "daily usage graph, billing split and inspection details."
        )
        st.stop()

    row = consumer_pool[
        consumer_pool["Selector_Label"] == selected_label
    ].iloc[0]

    consumer = str(row["Consumer_ID"])

    current_case_status = case_status_for(
        consumer
    )

    render_html(
        f"""
<div class="case-banner">
    <div>
        <div class="cb-id">CASE FILE · {consumer}</div>
        <div class="cb-name">{row['Consumer_Name']} · {row['Connection_Type']}</div>
        <div class="cb-address">{row['Short_Address']}</div>
    </div>
    <div class="cb-right">
        STATUS · {current_case_status}<br>
        PRIORITY · {row['Priority_Score']:.1f}/100<br>
        FEEDER · {row['Feeder_ID']}
    </div>
</div>
"""
    )

    render_html(
        f"""
<div class="consumer-header">
    <div>
        <div class="consumer-id">{consumer}</div>
        <div class="consumer-sub">
            {row['Consumer_Name']} · {row['Connection_Type']}
        </div>
        <div class="consumer-sub">
            {row['Short_Address']}
        </div>
        <div class="consumer-sub">
            {row['Area']} · {row['Substation']} · {row['Feeder_ID']}
        </div>
        <div style="margin-top:8px;">{risk_badge(row['Risk_Level'])}</div>
    </div>
    <div>
        <div class="big-score">{row['Risk_Score']:.1f}<small>/100</small></div>
        <div class="consumer-sub" style="text-align:right;">AI RISK SCORE</div>
    </div>
</div>
"""
    )

    primary_reason = str(
        row["Why_Flagged"]
    ).split("|")[0].strip()

    render_html(
        f"""
<div class="command-rail">
    <div class="command-step">
        <div class="cs-num">DETECT</div>
        <div class="cs-title">AI RISK</div>
        <div class="cs-value">{row['Risk_Score']:.1f}</div>
        <div class="cs-sub">Behavioural risk signal</div>
    </div>
    <div class="command-step">
        <div class="cs-num">EXPLAIN</div>
        <div class="cs-title">PRIMARY SIGNAL</div>
        <div class="cs-value" style="font-size:10px;">{primary_reason}</div>
        <div class="cs-sub">Readable reason for inspector</div>
    </div>
    <div class="command-step">
        <div class="cs-num">QUANTIFY</div>
        <div class="cs-title">EST. UNBILLED</div>
        <div class="cs-value">{row['Estimated_Unbilled_Units']:,.0f} U</div>
        <div class="cs-sub">Prototype unexplained usage</div>
    </div>
    <div class="command-step">
        <div class="cs-num">PRIORITIZE</div>
        <div class="cs-title">QUEUE SCORE</div>
        <div class="cs-value">{row['Priority_Score']:.1f}</div>
        <div class="cs-sub">Where this case sits operationally</div>
    </div>
    <div class="command-step">
        <div class="cs-num">ACT</div>
        <div class="cs-title">RECOMMENDATION</div>
        <div class="cs-value" style="font-size:11px;">{clean_text(row['Action'])}</div>
        <div class="cs-sub">Field team makes final decision</div>
    </div>
</div>
"""
    )

    render_html(
        f"""
<div class="identity-grid">
    <div class="identity-card">
        <div class="identity-label">Consumer name</div>
        <div class="identity-value large">{row['Consumer_Name']}</div>
        <div class="identity-sub">Synthetic demo identity</div>
    </div>
    <div class="identity-card">
        <div class="identity-label">Meter number</div>
        <div class="identity-value">{row['Meter_No']}</div>
        <div class="identity-sub">Demo meter reference</div>
    </div>
    <div class="identity-card">
        <div class="identity-label">Connection</div>
        <div class="identity-value">{row['Connection_Type']}</div>
        <div class="identity-sub">Consumer category</div>
    </div>
    <div class="identity-card">
        <div class="identity-label">Field action</div>
        <div class="identity-value">{clean_text(row['Action'])}</div>
        <div class="identity-sub">Priority {row['Priority_Score']:.1f}/100</div>
    </div>
</div>
"""
    )

    # --------------------------------------------------------
    # Energy accounting
    # --------------------------------------------------------

    energy = energy_breakdown(row)

    billed_text = (
        f"{energy['billed']:,.1f} U"
        if not pd.isna(energy["billed"])
        else "N/A"
    )

    total_text = (
        f"{energy['total']:,.1f} U"
        if not pd.isna(energy["total"])
        else "N/A"
    )

    coverage_text = (
        f"{energy['coverage']:.1f}%"
        if not pd.isna(energy["coverage"])
        else "N/A"
    )

    revenue_gap = (
        energy["suspected"]
        * DEFAULT_TARIFF
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.markdown(
        kpi(
            total_text,
            "Estimated total consumed",
            "Recorded + unexplained",
            "blue",
        ),
        unsafe_allow_html=True,
    )

    c2.markdown(
        kpi(
            billed_text,
            "Billed / recorded",
            energy["source"],
            "green",
        ),
        unsafe_allow_html=True,
    )

    c3.markdown(
        kpi(
            f"{energy['suspected']:,.1f} U",
            "Est. theft / unbilled",
            "Needs field verification",
            "red",
        ),
        unsafe_allow_html=True,
    )

    c4.markdown(
        kpi(
            coverage_text,
            "Billing coverage",
            "Prototype ratio",
            "amber",
        ),
        unsafe_allow_html=True,
    )

    c5.markdown(
        kpi(
            f"₹{revenue_gap:,.0f}",
            "Est. revenue gap",
            f"At ₹{DEFAULT_TARIFF:.1f}/unit",
            "amber",
        ),
        unsafe_allow_html=True,
    )

    render_html(
        f"""
<div class="bill-split">
    <div class="bill-cell">
        <div class="bill-k">Billed / meter-recorded units</div>
        <div class="bill-v">{billed_text}</div>
        <div class="bill-s">Units visible in the meter/billing-side history</div>
    </div>
    <div class="bill-cell red">
        <div class="bill-k">Estimated theft / unbilled units</div>
        <div class="bill-v">{energy['suspected']:,.1f} U</div>
        <div class="bill-s">WattGuard unexplained-usage estimate; not confirmed theft</div>
    </div>
    <div class="bill-cell amber">
        <div class="bill-k">Estimated actual total consumption</div>
        <div class="bill-v">{total_text}</div>
        <div class="bill-s">Billed/recorded + estimated unexplained usage</div>
    </div>
</div>
"""
    )

    # --------------------------------------------------------
    # Daily usage profile
    # --------------------------------------------------------

    history = get_history(row)

    chart_col, side_col = st.columns([1.7, 1])

    with chart_col:

        render_html(
            """
<div class="panel-head">
    <div class="panel-title">DAILY CONSUMPTION PROFILE</div>
    <div class="panel-meta">METER-RECORDED USAGE · UNITS / DAY</div>
</div>
"""
        )

        if history is not None and not history.empty:

            st.caption(
                "Each bar = electricity units recorded on that day. "
                "Use the range selector to change how many days are shown."
            )

            g1, g2 = st.columns([1, 1])

            with g1:
                period = st.selectbox(
                    "GRAPH RANGE",
                    [
                        "Last 30 days",
                        "Last 60 days",
                        "Last 90 days",
                    ],
                    index=0,
                    key="consumer_history_window",
                )

            with g2:
                graph_type = st.selectbox(
                    "GRAPH VIEW",
                    [
                        "Daily usage",
                        "Daily usage + 7-day trend",
                    ],
                    index=0,
                    key="consumer_graph_type",
                )

            days_map = {
                "Last 30 days": 30,
                "Last 60 days": 60,
                "Last 90 days": 90,
            }

            days = days_map[period]
            shown = history.tail(days).copy()

            shown["7-Day Average"] = (
                shown["Usage"]
                .rolling(
                    7,
                    min_periods=1,
                )
                .mean()
            )

            if graph_type == "Daily usage":

                simple_chart = (
                    shown[
                        ["Date", "Usage"]
                    ]
                    .copy()
                    .set_index("Date")
                    .rename(
                        columns={
                            "Usage": "Daily Units"
                        }
                    )
                )

                st.bar_chart(
                    simple_chart,
                    height=360,
                    x_label="Date",
                    y_label="Units used",
                )

            else:

                trend_chart = (
                    shown[
                        [
                            "Date",
                            "Usage",
                            "7-Day Average",
                        ]
                    ]
                    .copy()
                    .set_index("Date")
                    .rename(
                        columns={
                            "Usage": "Daily Units"
                        }
                    )
                )

                st.line_chart(
                    trend_chart,
                    height=360,
                    x_label="Date",
                    y_label="Units used",
                )

            recent30 = history.tail(30).copy()
            previous30 = history.iloc[-60:-30].copy()

            total_30 = float(
                recent30["Usage"].sum()
            )

            avg_day = float(
                recent30["Usage"].mean()
            )

            peak_row = recent30.loc[
                recent30["Usage"].idxmax()
            ]

            peak_usage = float(
                peak_row["Usage"]
            )

            peak_date = pd.to_datetime(
                peak_row["Date"]
            ).strftime("%d %b")

            previous_avg = (
                float(previous30["Usage"].mean())
                if not previous30.empty
                else np.nan
            )

            change_30 = (
                (
                    (avg_day - previous_avg)
                    / previous_avg
                )
                * 100
                if not pd.isna(previous_avg)
                and previous_avg > 0
                else np.nan
            )

            change_text = (
                f"{change_30:+.1f}%"
                if not pd.isna(change_30)
                else "N/A"
            )

            s1, s2, s3, s4 = st.columns(4)

            s1.metric(
                "Last 30 days",
                f"{total_30:,.1f} units",
            )

            s2.metric(
                "Average per day",
                f"{avg_day:,.1f} units",
            )

            s3.metric(
                "Highest day",
                f"{peak_usage:,.1f} units",
                peak_date,
            )

            s4.metric(
                "Vs previous 30 days",
                change_text,
            )

            # =================================================
            # WATTGUARD BEHAVIOUR SHIFT DETECTOR
            # =================================================

            previous_total = (
                float(previous30["Usage"].sum())
                if not previous30.empty
                else np.nan
            )

            difference_units = (
                total_30 - previous_total
                if not pd.isna(previous_total)
                else np.nan
            )

            absolute_difference = (
                abs(difference_units)
                if not pd.isna(difference_units)
                else np.nan
            )

            if not pd.isna(change_30):
                if change_30 <= -40:
                    shift_label = "MAJOR DROP"
                    shift_class = "negative"
                    shift_note = "Strong fall in recorded consumption"
                elif change_30 <= -20:
                    shift_label = "SIGNIFICANT DROP"
                    shift_class = "negative"
                    shift_note = "Consumption materially below previous window"
                elif change_30 < -8:
                    shift_label = "MODERATE DROP"
                    shift_class = "negative"
                    shift_note = "Lower than preceding 30-day behaviour"
                elif change_30 >= 20:
                    shift_label = "STRONG RISE"
                    shift_class = "positive"
                    shift_note = "Consumption materially above previous window"
                elif change_30 >= 8:
                    shift_label = "MODERATE RISE"
                    shift_class = "positive"
                    shift_note = "Usage increased from preceding window"
                else:
                    shift_label = "STABLE RANGE"
                    shift_class = "positive"
                    shift_note = "No major 30-day shift detected"
            else:
                shift_label = "INSUFFICIENT HISTORY"
                shift_class = "positive"
                shift_note = "Previous comparison window unavailable"

            previous_total_text = (
                f"{previous_total:,.1f} U"
                if not pd.isna(previous_total)
                else "N/A"
            )

            difference_text = (
                f"{difference_units:+,.1f} U"
                if not pd.isna(difference_units)
                else "N/A"
            )

            render_html(
                f"""
<div class="shift-shell">
    <div class="shift-head">
        <div>
            <div class="shift-title">WATTGUARD BEHAVIOUR SHIFT DETECTOR</div>
            <div class="shift-sub">
                Direct comparison of the previous 30-day window against the latest 30-day window.
                This shows exactly what changed before the AI risk score is interpreted.
            </div>
        </div>
        <div class="shift-state">CHANGE SIGNATURE · {shift_label}</div>
    </div>

    <div class="shift-flow">

        <div class="shift-box before">
            <div class="shift-k">Previous 30 days</div>
            <div class="shift-v">{previous_total_text}</div>
            <div class="shift-s">
                Avg {previous_avg:,.1f} U/day
                {"" if not pd.isna(previous_avg) else " · unavailable"}
            </div>
        </div>

        <div class="shift-arrow">→</div>

        <div class="shift-box current">
            <div class="shift-k">Latest 30 days</div>
            <div class="shift-v">{total_30:,.1f} U</div>
            <div class="shift-s">Avg {avg_day:,.1f} U/day · current meter-recorded window</div>
        </div>

        <div class="shift-arrow">→</div>

        <div class="shift-box delta {shift_class}">
            <div class="shift-k">Actual difference</div>
            <div class="shift-v">{difference_text}</div>
            <div class="shift-s">{change_text} · {shift_note}</div>
        </div>

        <div class="shift-arrow">→</div>

        <div class="shift-box ai">
            <div class="shift-k">WattGuard interpretation</div>
            <div class="shift-v" style="font-size:12px;">{shift_label}</div>
            <div class="shift-s">
                AI risk {row['Risk_Score']:.1f}/100 · priority {row['Priority_Score']:.1f}/100
            </div>
        </div>

    </div>
</div>
"""
            )

            # -------------------------------------------------
            # 6 x 5-day change signature
            # -------------------------------------------------

            signature_cells = []

            if (
                len(previous30) >= 30
                and len(recent30) >= 30
            ):
                previous_values = previous30["Usage"].to_numpy()
                recent_values = recent30["Usage"].to_numpy()

                for block_no in range(6):
                    start_i = block_no * 5
                    end_i = start_i + 5

                    before_block = float(
                        previous_values[
                            start_i:end_i
                        ].sum()
                    )

                    after_block = float(
                        recent_values[
                            start_i:end_i
                        ].sum()
                    )

                    block_change = (
                        (
                            (after_block - before_block)
                            / before_block
                        ) * 100
                        if before_block > 0
                        else np.nan
                    )

                    if pd.isna(block_change):
                        cell_cls = "amber"
                        block_text = "N/A"
                    elif block_change <= -20:
                        cell_cls = "red"
                        block_text = f"{block_change:+.0f}%"
                    elif block_change < -8:
                        cell_cls = "amber"
                        block_text = f"{block_change:+.0f}%"
                    else:
                        cell_cls = "green"
                        block_text = f"{block_change:+.0f}%"

                    signature_cells.append(
                        f"""
<div class="sig-cell {cell_cls}">
    <div class="sig-k">5-DAY BLOCK {block_no + 1}</div>
    <div class="sig-v">{block_text}</div>
    <div class="sig-s">{before_block:,.0f} U → {after_block:,.0f} U</div>
</div>
"""
                    )

            if signature_cells:
                render_html(
                    f"""
<div class="signature-shell">
    <div class="signature-head">
        <div>
            <div class="signature-title">30-DAY CHANGE SIGNATURE</div>
            <div class="signature-sub">
                Six five-day blocks compare the previous month with the current month.
                Red blocks show where the consumption drop is concentrated instead of hiding it inside one average.
            </div>
        </div>
    </div>
    <div class="signature-grid">
        {''.join(signature_cells)}
    </div>
</div>
"""
                )

            # -------------------------------------------------
            # Meter-to-gap bridge
            # -------------------------------------------------

            current_recorded = total_30

            current_unbilled = max(
                0.0,
                float(
                    row[
                        "Estimated_Unbilled_Units"
                    ]
                ),
            )

            current_estimated_total = (
                current_recorded
                + current_unbilled
            )

            current_coverage = (
                current_recorded
                / current_estimated_total
                * 100
                if current_estimated_total > 0
                else np.nan
            )

            coverage_bridge_text = (
                f"{current_coverage:.1f}% visible"
                if not pd.isna(current_coverage)
                else "Coverage unavailable"
            )

            render_html(
                f"""
<div class="shift-shell">
    <div class="shift-head">
        <div>
            <div class="shift-title">METER-TO-LOSS BRIDGE</div>
            <div class="shift-sub">
                A simple operational view of what the meter recorded versus what WattGuard estimates may be unexplained.
            </div>
        </div>
        <div class="shift-state">{coverage_bridge_text}</div>
    </div>

    <div class="gap-bridge">
        <div class="gap-node recorded">
            <div class="gap-k">Meter-recorded · latest 30D</div>
            <div class="gap-v">{current_recorded:,.1f} U</div>
            <div class="gap-s">Observed in this consumer's meter history</div>
        </div>

        <div class="gap-op">+</div>

        <div class="gap-node unbilled">
            <div class="gap-k">Est. unexplained / unbilled</div>
            <div class="gap-v">{current_unbilled:,.1f} U</div>
            <div class="gap-s">Prototype estimate · field confirmation required</div>
        </div>

        <div class="gap-op">=</div>

        <div class="gap-node total">
            <div class="gap-k">Estimated consumption footprint</div>
            <div class="gap-v">{current_estimated_total:,.1f} U</div>
            <div class="gap-s">Recorded + estimated unexplained usage</div>
        </div>
    </div>
</div>
"""
            )

            st.markdown(
                '<div class="ops-label">'
                'LAST 30 DAYS — DAILY METER READINGS'
                '</div>',
                unsafe_allow_html=True,
            )

            daily_table = recent30[
                ["Date", "Usage"]
            ].copy()

            daily_table["Date"] = pd.to_datetime(
                daily_table["Date"]
            ).dt.strftime("%d-%m-%Y")

            daily_table = daily_table.rename(
                columns={
                    "Usage": "Units Used"
                }
            )

            st.dataframe(
                daily_table.iloc[::-1],
                use_container_width=True,
                hide_index=True,
                height=300,
            )

        else:
            st.warning(
                "The daily SGCC history is not linked to this demo consumer yet. "
                "WattGuard tried Source_Index, original WG ID, and "
                "wattguard_evaluation.csv matching. Keep wattguard_evaluation.csv "
                "in the data folder so each Chennai demo identity maps back to its "
                "actual SGCC daily load history."
            )

    with side_col:

        render_html(
            """
<div class="panel-head">
    <div class="panel-title">INVESTIGATION SIGNALS</div>
    <div class="panel-meta">WHY WATTGUARD RANKED THIS CASE</div>
</div>
"""
        )

        for reason in str(
            row["Why_Flagged"]
        ).split("|"):
            st.markdown(
                f'<div class="reason">→ {reason.strip()}</div>',
                unsafe_allow_html=True,
            )

        st.write("")

        case_tariff = st.number_input(
            "TARIFF ASSUMPTION ₹ / UNIT",
            min_value=1.0,
            max_value=20.0,
            value=DEFAULT_TARIFF,
            step=0.5,
            key="case_tariff",
        )

        case_revenue = (
            max(
                0.0,
                float(row["Estimated_Unbilled_Units"]),
            )
            * case_tariff
        )

        render_html(
            f"""
<div class="note">
    <strong>FIELD INSPECTION BRIEF</strong><br><br>
    Consumer: {row['Consumer_Name']} ({consumer})<br>
    Address: {row['Short_Address']}<br>
    Meter: {row['Meter_No']}<br>
    Feeder: {row['Feeder_ID']}<br><br>
    AI risk: {row['Risk_Score']:.1f}/100<br>
    Priority: {row['Priority_Score']:.1f}/100<br>
    Estimated unbilled: {row['Estimated_Unbilled_Units']:.1f} units<br>
    Estimated ₹ exposure: ₹{case_revenue:,.0f}<br><br>
    Recommended action: {clean_text(row['Action'])}
</div>
"""
        )

        st.markdown(
            '<div class="ops-label">FIELD CHECKLIST</div>',
            unsafe_allow_html=True,
        )

        checks = [
            "Verify meter seal / terminal condition",
            "Compare meter reading with service history",
            "Inspect bypass / direct tapping indicators",
            "Check sanctioned load vs connected load",
            "Record field outcome before closing case",
        ]

        for i, item in enumerate(checks, start=1):
            st.checkbox(
                f"{i:02d} · {item}",
                key=f"check_{consumer}_{i}",
            )



    # ========================================================
    # DIFFERENTIATOR 1 — EVIDENCE FINGERPRINT
    # ========================================================

    st.markdown(
        '<div class="ops-label">WATTGUARD EVIDENCE FINGERPRINT</div>',
        unsafe_allow_html=True,
    )

    fingerprint = build_evidence_fingerprint(
        row,
        df,
    )

    fp_rows = []

    for item in fingerprint:
        score = float(
            item["score"]
        )

        if score >= 85:
            fp_class = "hot"
        elif score >= 65:
            fp_class = "warn"
        else:
            fp_class = ""

        raw_value = item[
            "value"
        ]

        value_text = (
            f"{raw_value:.3f}"
            if not pd.isna(
                raw_value
            )
            else "N/A"
        )

        fp_rows.append(
            f"""
<div class="fingerprint-row">
    <div class="fp-label">{item['label']}</div>
    <div class="fp-track">
        <div class="fp-fill {fp_class}" style="width:{score:.1f}%"></div>
    </div>
    <div class="fp-score">{score:.0f}/100</div>
</div>
"""
        )

    render_html(
        f"""
<div class="fingerprint-shell">
    <div class="fingerprint-title">
        BEHAVIOURAL EVIDENCE FINGERPRINT
    </div>
    <div class="fingerprint-sub">
        Each bar shows how unusual this behavioural feature is relative to the
        analysed consumer population. It is an evidence percentile, not a theft probability.
    </div>
    {''.join(fp_rows)}
</div>
"""
    )

    # ========================================================
    # DIFFERENTIATOR 2 — LOW-RISK PEER TWIN
    # ========================================================

    peer = find_low_risk_peer(
        row,
        df,
    )

    if peer is not None:
        peer_history = get_history(
            peer
        )

        current_recent = (
            float(
                history.tail(
                    30
                )["Usage"].mean()
            )
            if history is not None
            and not history.empty
            else pd.to_numeric(
                row.get(
                    "mean_usage",
                    np.nan,
                ),
                errors="coerce",
            )
        )

        peer_recent = (
            float(
                peer_history.tail(
                    30
                )["Usage"].mean()
            )
            if peer_history is not None
            and not peer_history.empty
            else pd.to_numeric(
                peer.get(
                    "mean_usage",
                    np.nan,
                ),
                errors="coerce",
            )
        )

        current_recent_text = (
            f"{current_recent:.1f} U/day"
            if not pd.isna(
                current_recent
            )
            else "N/A"
        )

        peer_recent_text = (
            f"{peer_recent:.1f} U/day"
            if not pd.isna(
                peer_recent
            )
            else "N/A"
        )

        current_zero = pd.to_numeric(
            row.get(
                "zero_ratio",
                np.nan,
            ),
            errors="coerce",
        )

        peer_zero = pd.to_numeric(
            peer.get(
                "zero_ratio",
                np.nan,
            ),
            errors="coerce",
        )

        current_variation = pd.to_numeric(
            row.get(
                "variation",
                np.nan,
            ),
            errors="coerce",
        )

        peer_variation = pd.to_numeric(
            peer.get(
                "variation",
                np.nan,
            ),
            errors="coerce",
        )

        render_html(
            f"""
<div class="peer-shell">
    <div class="peer-head">
        <div>
            <div class="peer-title">LOW-RISK PEER TWIN COMPARATOR</div>
            <div class="peer-sub">
                WattGuard finds a behaviourally similar lower-risk consumer and
                compares the two. This helps an officer see what makes the selected
                case stand out without exposing evaluation labels.
            </div>
        </div>
        <div class="peer-state">PEER-BASED CONTEXT</div>
    </div>

    <div class="peer-grid">

        <div class="peer-card target">
            <div class="peer-id">{row['Consumer_ID']}</div>
            <div class="peer-name">{row['Consumer_Name']} · SELECTED CASE</div>

            <div class="peer-metrics">
                <div class="peer-cell">
                    <div class="peer-k">AI Risk</div>
                    <div class="peer-v">{row['Risk_Score']:.1f}/100</div>
                </div>
                <div class="peer-cell">
                    <div class="peer-k">Recent usage</div>
                    <div class="peer-v">{current_recent_text}</div>
                </div>
                <div class="peer-cell">
                    <div class="peer-k">Zero ratio</div>
                    <div class="peer-v">{current_zero:.3f}</div>
                </div>
                <div class="peer-cell">
                    <div class="peer-k">Variation</div>
                    <div class="peer-v">{current_variation:.3f}</div>
                </div>
            </div>
        </div>

        <div class="peer-vs">VS</div>

        <div class="peer-card twin">
            <div class="peer-id">{peer['Consumer_ID']}</div>
            <div class="peer-name">{peer['Consumer_Name']} · LOW-RISK PEER</div>

            <div class="peer-metrics">
                <div class="peer-cell">
                    <div class="peer-k">AI Risk</div>
                    <div class="peer-v">{peer['Risk_Score']:.1f}/100</div>
                </div>
                <div class="peer-cell">
                    <div class="peer-k">Recent usage</div>
                    <div class="peer-v">{peer_recent_text}</div>
                </div>
                <div class="peer-cell">
                    <div class="peer-k">Zero ratio</div>
                    <div class="peer-v">{peer_zero:.3f}</div>
                </div>
                <div class="peer-cell">
                    <div class="peer-k">Variation</div>
                    <div class="peer-v">{peer_variation:.3f}</div>
                </div>
            </div>
        </div>

    </div>
</div>
"""
        )

        if (
            history is not None
            and not history.empty
            and peer_history is not None
            and not peer_history.empty
        ):
            compare_days = min(
                30,
                len(history),
                len(peer_history),
            )

            comparison = pd.DataFrame(
                {
                    "Selected Consumer": (
                        history.tail(
                            compare_days
                        )["Usage"]
                        .reset_index(
                            drop=True
                        )
                    ),
                    "Low-Risk Peer": (
                        peer_history.tail(
                            compare_days
                        )["Usage"]
                        .reset_index(
                            drop=True
                        )
                    ),
                },
                index=[
                    f"D-{compare_days - i - 1}"
                    for i in range(
                        compare_days
                    )
                ],
            )

            st.caption(
                "Selected case vs low-risk peer — latest 30 meter-reading days."
            )

            st.line_chart(
                comparison,
                height=280,
                y_label="Units / day",
            )

    else:
        st.info(
            "A suitable low-risk peer could not be identified for this case."
        )

    # ========================================================
    # DIFFERENTIATOR 3 — FALSE-POSITIVE GUARD
    # ========================================================

    readiness = inspection_readiness(
        row,
        df,
    )

    guard_state = readiness[
        "state"
    ]

    render_html(
        f"""
<div class="guard-shell">
    <div class="guard-head">
        <div>
            <div class="guard-title">FALSE-POSITIVE GUARD / INSPECTION READINESS</div>
            <div class="guard-sub">
                Before dispatch, WattGuard checks whether the case has multiple
                independent behavioural signals and meaningful impact. This is a
                second review layer designed to avoid sending officers based on one
                model score alone.
            </div>
        </div>
        <div class="guard-state">{guard_state}</div>
    </div>

    <div class="guard-grid">
        <div class="guard-cell">
            <div class="guard-k">AI Risk</div>
            <div class="guard-v">{readiness['risk']:.1f}/100</div>
            <div class="guard-s">Primary model signal</div>
        </div>

        <div class="guard-cell">
            <div class="guard-k">Independent signals</div>
            <div class="guard-v">{readiness['strong_signals']}</div>
            <div class="guard-s">Evidence fingerprint bars ≥ 75</div>
        </div>

        <div class="guard-cell">
            <div class="guard-k">Impact percentile</div>
            <div class="guard-v">{readiness['unbilled_percentile']:.0f}th</div>
            <div class="guard-s">Relative estimated unbilled impact</div>
        </div>

        <div class="guard-cell">
            <div class="guard-k">Priority</div>
            <div class="guard-v">{readiness['priority']:.1f}/100</div>
            <div class="guard-s">{readiness['note']}</div>
        </div>
    </div>
</div>
"""
    )

    # ========================================================
    # DIFFERENTIATOR 4 — CASE EVIDENCE PACK
    # ========================================================

    evidence_report = build_case_evidence_report(
        row,
        energy,
        history,
        peer,
        readiness,
    )

    dl1, dl2 = st.columns(
        [1.2, 2.8]
    )

    with dl1:
        st.download_button(
            "DOWNLOAD CASE EVIDENCE PACK",
            data=evidence_report,
            file_name=(
                f"{consumer}_WattGuard_Evidence.txt"
            ),
            mime="text/plain",
            use_container_width=True,
            key=f"case_pack_{consumer}",
        )

    with dl2:
        st.caption(
            "Field-ready export: identity, location, risk, behaviour shift, "
            "estimated impact, peer context and inspection-readiness notes."
        )


    st.markdown(
        '<div class="ops-label">CASE LIFECYCLE / FIELD FEEDBACK</div>',
        unsafe_allow_html=True,
    )

    lifecycle_order = [
        "FLAGGED",
        "ASSIGNED",
        "ON-SITE",
        "VERIFIED",
        "CLOSED",
    ]

    status_now = case_status_for(
        consumer
    )

    status_rank = (
        lifecycle_order.index(status_now)
        if status_now in lifecycle_order
        else 0
    )

    timeline_html = []

    for idx, label in enumerate(lifecycle_order):
        cls = (
            "done"
            if idx < status_rank
            else "active"
            if idx == status_rank
            else ""
        )

        timeline_html.append(
            f"""
<div class="timeline-node {cls}">
    <div class="timeline-k">STEP {idx + 1:02d}</div>
    <div class="timeline-v">{label}</div>
</div>
"""
        )

    render_html(
        '<div class="case-timeline">'
        + "".join(timeline_html)
        + "</div>"
    )

    outcome_left, outcome_right = st.columns(
        [1, 1.2]
    )

    with outcome_left:
        new_status = st.selectbox(
            "CASE STATUS",
            lifecycle_order,
            index=(
                lifecycle_order.index(status_now)
                if status_now in lifecycle_order
                else 0
            ),
            key=f"case_status_{consumer}",
        )

        if st.button(
            "UPDATE CASE STATUS",
            use_container_width=True,
            key=f"update_case_status_{consumer}",
        ):
            set_case_status(
                consumer,
                new_status,
            )

            log_operator_event(
                f"{consumer} case status changed to {new_status}.",
                level=(
                    "INFO"
                    if new_status not in ["VERIFIED"]
                    else "WARNING"
                ),
            )

            st.success(
                f"{consumer} updated to {new_status}."
            )

            st.rerun()

    with outcome_right:
        field_outcome = st.selectbox(
            "FIELD OUTCOME",
            [
                "Not inspected yet",
                "Theft / irregularity confirmed",
                "Not confirmed",
                "Meter defect / technical issue",
                "Needs recheck",
            ],
            key=f"field_outcome_{consumer}",
        )

        field_note = st.text_area(
            "OPERATOR / INSPECTOR NOTE",
            placeholder=(
                "Example: seal condition, connected load, "
                "meter observation, reason for closure..."
            ),
            height=86,
            key=f"field_note_{consumer}",
        )

        if st.button(
            "SAVE FIELD FEEDBACK",
            use_container_width=True,
            key=f"save_feedback_{consumer}",
        ):
            if "wg_feedback" not in st.session_state:
                st.session_state["wg_feedback"] = {}

            st.session_state["wg_feedback"][
                consumer
            ] = {
                "outcome": field_outcome,
                "note": field_note,
                "time": datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S"
                ),
            }

            log_operator_event(
                f"Field feedback saved for {consumer}: {field_outcome}.",
                level="INFO",
            )

            st.success(
                "Field feedback saved for this demo session."
            )

    saved_feedback = st.session_state.get(
        "wg_feedback",
        {},
    ).get(
        consumer
    )

    if saved_feedback:
        render_html(
            f"""
<div class="outcome-panel">
    <div class="outcome-title">LATEST FIELD FEEDBACK</div>
    <div class="outcome-sub">
        {saved_feedback['time']} · {saved_feedback['outcome']}
    </div>
    <div style="
        margin-top:8px;
        color:#d7e0e5;
        font-family:var(--mono);
        font-size:9px;
        line-height:1.6;
    ">
        {saved_feedback['note'] or 'No additional note entered.'}
    </div>
</div>
"""
        )


    st.markdown(
        """
<div class="smallprint">
CONSUMER IDENTITY NOTE: names, meter numbers and street addresses shown in this
prototype are deterministic synthetic demo identities. They are not real Chennai
consumer records. DAILY USAGE is taken from the linked SGCC consumer history when
a reliable source-index mapping is available. "ESTIMATED THEFT / UNBILLED" is an
investigation estimate and must not be treated as confirmed theft without field
verification.
</div>
""",
        unsafe_allow_html=True,
    )

# ============================================================
# PAGE 3 — SUBSTATION MIMIC
# ============================================================

elif page == "SUBSTATION MIMIC":

    st.markdown(
        '<div class="ops-label">SUBSTATION SINGLE-LINE MIMIC / DISTRIBUTION LOSS ANALYTICS</div>',
        unsafe_allow_html=True,
    )

    sf1, sf2, sf3 = st.columns([1, 1.2, .75])

    with sf1:
        station_area = st.selectbox(
            "AREA / SECTION",
            sorted(
                df["Area"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            ),
            key="station_area",
        )

    station_area_df = df[
        df["Area"].astype(str) == station_area
    ].copy()

    station_list = sorted(
        station_area_df["Substation"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    with sf2:
        station_name = st.selectbox(
            "SUBSTATION",
            station_list,
            key="station_name",
        )

    with sf3:
        station_tariff = st.number_input(
            "₹ / UNIT",
            1.0,
            20.0,
            DEFAULT_TARIFF,
            .5,
            key="station_tariff",
        )

    station_df = station_area_df[
        station_area_df["Substation"].astype(str)
        == station_name
    ].copy()

    summary = feeder_summary(
        station_df,
        station_tariff,
    )

    total_consumers = len(station_df)
    alerts = int(
        (station_df["Risk_Score"] >= 45).sum()
    )
    critical = int(
        (station_df["Risk_Score"] >= 70).sum()
    )
    station_unbilled = float(
        station_df["Estimated_Unbilled_Units"]
        .clip(lower=0)
        .sum()
    )
    station_revenue = (
        station_unbilled
        * station_tariff
    )

    s1, s2, s3, s4, s5 = st.columns(5)

    s1.markdown(
        kpi(
            f"{total_consumers:,}",
            "Consumers",
            station_name,
            "blue",
        ),
        unsafe_allow_html=True,
    )

    s2.markdown(
        kpi(
            f"{len(summary)}",
            "Outgoing feeders",
            "Demo topology",
            "blue",
        ),
        unsafe_allow_html=True,
    )

    s3.markdown(
        kpi(
            f"{alerts}",
            "Open alerts",
            f"{critical} critical",
            "red" if critical else "amber",
        ),
        unsafe_allow_html=True,
    )

    s4.markdown(
        kpi(
            f"{station_unbilled:,.0f} U",
            "Est. unbilled",
            "Investigation estimate",
            "red",
        ),
        unsafe_allow_html=True,
    )

    s5.markdown(
        kpi(
            f"₹{station_revenue:,.0f}",
            "Revenue exposure",
            f"At ₹{station_tariff:.1f}/unit",
            "amber",
        ),
        unsafe_allow_html=True,
    )

    feeder_html = []

    for _, fr in summary.head(12).iterrows():

        if int(fr["Critical"]) > 0:
            cls = "red"
            state = "CRITICAL"
        elif int(fr["Alert"]) > 0:
            cls = "amber"
            state = "REVIEW"
        else:
            cls = ""
            state = "NORMAL"

        billed = (
            f"{fr['Recorded_Billed_30D']:,.0f} U"
            if not pd.isna(fr["Recorded_Billed_30D"])
            else "N/A"
        )

        total = (
            f"{fr['Estimated_Total_30D']:,.0f} U"
            if not pd.isna(fr["Estimated_Total_30D"])
            else "N/A"
        )

        feeder_html.append(
            f"""
<div class="sl-feeder {cls}">
    <div class="sl-fhead">
        <div class="sl-fid">{fr['Feeder_ID']}</div>
        <div class="sl-fstate">● {state}</div>
    </div>
    <div class="sl-fgrid">
        <div class="sl-fcell">
            <div class="sl-fk">Consumers</div>
            <div class="sl-fv">{int(fr['Consumers'])}</div>
        </div>
        <div class="sl-fcell">
            <div class="sl-fk">Alerts / Critical</div>
            <div class="sl-fv">{int(fr['Alert'])} / {int(fr['Critical'])}</div>
        </div>
        <div class="sl-fcell">
            <div class="sl-fk">Billed / Recorded</div>
            <div class="sl-fv">{billed}</div>
        </div>
        <div class="sl-fcell">
            <div class="sl-fk">Est. Theft / Unbilled</div>
            <div class="sl-fv">{fr['Possible_Unbilled']:,.0f} U</div>
        </div>
        <div class="sl-fcell">
            <div class="sl-fk">Est. Total Used</div>
            <div class="sl-fv">{total}</div>
        </div>
        <div class="sl-fcell">
            <div class="sl-fk">Max AI Risk</div>
            <div class="sl-fv">{fr['Max_Risk']:.1f}</div>
        </div>
    </div>
</div>
"""
        )

    render_html(
        f"""
<div class="sl-shell">

    <div class="sl-titlebar">
        <div>
            <div class="sl-station">{station_name}</div>
            <div class="sl-meta">{station_area.upper()} · CHENNAI DEMO DISTRIBUTION SUBSTATION</div>
        </div>
        <div class="sl-live">● ANALYTICS ONLINE<br>TOPOLOGY MIMIC / DEMO</div>
    </div>

    <div class="sl-body">

        <div class="sl-node">
            <div class="n1">33 kV INCOMING SUPPLY</div>
            <div class="n2">UPSTREAM GRID / DEMO INCOMER</div>
        </div>

        <div class="sl-line"></div>

        <div class="sl-breaker">● INCOMER VCB · CLOSED</div>

        <div class="sl-line"></div>

        <div class="sl-transformer">
            <div class="sl-coils">
                <div class="sl-coil"></div>
                <div class="sl-coil"></div>
            </div>
            <div class="t1">POWER TRANSFORMER T1 · 33/11 kV</div>
            <div class="t2">VISUAL MIMIC ONLY · NO LIVE SCADA TELEMETRY</div>
        </div>

        <div class="sl-line"></div>

        <div class="sl-breaker">● 11 kV BUS COUPLER · HEALTHY</div>

        <div class="sl-line"></div>

        <div class="sl-bus-label">11 kV DISTRIBUTION BUS</div>
        <div class="sl-bus"></div>

        <div class="sl-feeders">
            {''.join(feeder_html)}
        </div>

    </div>
</div>
"""
    )

    st.markdown(
        '<div class="ops-label">FEEDER ENERGY ACCOUNTING / LOSS PRIORITY</div>',
        unsafe_allow_html=True,
    )

    if not summary.empty:

        display = summary[
            [
                "Feeder_ID",
                "Consumers",
                "Alert",
                "Critical",
                "Recorded_Billed_30D",
                "Possible_Unbilled",
                "Estimated_Total_30D",
                "Billing_Coverage_Pct",
                "Max_Risk",
                "Revenue_At_Risk",
            ]
        ].rename(
            columns={
                "Alert": "Alerts",
                "Recorded_Billed_30D": "Billed / Recorded",
                "Possible_Unbilled": "Est. Theft / Unbilled",
                "Estimated_Total_30D": "Est. Total Used",
                "Billing_Coverage_Pct": "Billing Coverage %",
                "Max_Risk": "Max AI Risk",
                "Revenue_At_Risk": "₹ Revenue Exposure",
            }
        )

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            height=390,
        )

    st.markdown(
        """
<div class="smallprint">
SUBSTATION SCREEN NOTE: the 33/11 kV incomer, VCB, transformer, bus and feeder
layout is a visual prototype of an EB/DISCOM control-room mimic. It is not a
claim of actual Chennai substation topology or live SCADA breaker/voltage/current
telemetry. Area, substation and feeder mappings are synthetic demo labels.
</div>
""",
        unsafe_allow_html=True,
    )

# ============================================================
# PAGE 4 — FIELD QUEUE
# ============================================================

elif page == "FIELD QUEUE":

    st.markdown(
        '<div class="ops-label">FIELD OPERATIONS / DISPATCH BOARD</div>',
        unsafe_allow_html=True,
    )

    q1, q2, q3 = st.columns([1.2, 1.2, 0.8])

    with q1:
        queue_area = st.selectbox(
            "AREA",
            ["ALL CHENNAI"]
            + sorted(df["Area"].dropna().astype(str).unique().tolist()),
            key="queue_area",
        )

    queue_df = (
        df.copy()
        if queue_area == "ALL CHENNAI"
        else df[df["Area"].astype(str) == queue_area].copy()
    )

    with q2:
        action_options = sorted(
            queue_df["Action"].dropna().astype(str).unique().tolist()
        )

        queue_action = st.selectbox(
            "ACTION FILTER",
            ["ALL ACTIONS"] + action_options,
            key="queue_action",
        )

    if queue_action != "ALL ACTIONS":
        queue_df = queue_df[
            queue_df["Action"].astype(str) == queue_action
        ].copy()

    with q3:
        queue_capacity = st.number_input(
            "SHIFT CAPACITY",
            min_value=1,
            max_value=max(1, min(200, len(queue_df))),
            value=min(25, max(1, len(queue_df))),
            step=1,
            key="queue_capacity",
        )

    queue_df = (
        queue_df.sort_values(
            "Priority_Score",
            ascending=False,
        )
        .head(int(queue_capacity))
        .copy()
    )

    if "field_status" not in st.session_state:
        st.session_state["field_status"] = {}

    status_options = [
        "PENDING",
        "ASSIGNED",
        "ON-SITE",
        "INSPECTION COMPLETED",
        "CONFIRMED",
        "NOT CONFIRMED",
        "RECHECK",
    ]

    if queue_df.empty:
        st.info("No field cases match the current filters.")
    else:
        for rank, (_, row) in enumerate(
            queue_df.iterrows(),
            start=1,
        ):
            cid = str(row["Consumer_ID"])

            title = (
                f"{rank:02d} | {cid} | {row['Area']} | "
                f"{row['Feeder_ID']} | "
                f"RISK {row['Risk_Score']:.1f} | "
                f"PRIORITY {row['Priority_Score']:.1f}"
            )

            with st.expander(title):

                if st.button(
                    f"OPEN {row['Consumer_ID']} IN CONSUMER DESK →",
                    use_container_width=True,
                    key=f"field_open_{row['Consumer_ID']}_{idx}",
                ):
                    queue_consumer_open(
                        row["Consumer_ID"],
                        source="FIELD QUEUE",
                    )

                    log_operator_event(
                        f"Opened {row['Consumer_ID']} from Field Queue."
                    )

                    st.rerun()
                x1, x2, x3, x4, x5 = st.columns(5)

                x1.metric(
                    "Risk",
                    f"{row['Risk_Score']:.1f}/100",
                )

                x2.metric(
                    "Billed / recorded",
                    (
                        f"{row['Billed_Units_30D']:.1f} U"
                        if not pd.isna(row["Billed_Units_30D"])
                        else "N/A"
                    ),
                )

                x3.metric(
                    "Est. theft / unbilled",
                    f"{row['Estimated_Unbilled_Units']:.1f} U",
                )

                x4.metric(
                    "Est. total used",
                    (
                        f"{row['Estimated_Total_Consumed_Units_30D']:.1f} U"
                        if not pd.isna(row["Estimated_Total_Consumed_Units_30D"])
                        else "N/A"
                    ),
                )

                x5.metric(
                    "Action",
                    clean_text(row["Action"]),
                )

                st.write(
                    "**Location:**",
                    f"{row['Area']} · {row['Substation']} · {row['Feeder_ID']}",
                )

                st.write(
                    "**Reason:**",
                    str(row["Why_Flagged"]).replace("|", " · "),
                )

                current = st.session_state["field_status"].get(
                    cid,
                    "PENDING",
                )

                status = st.selectbox(
                    "FIELD STATUS",
                    status_options,
                    index=status_options.index(current),
                    key=f"field_status_{cid}",
                )

                st.session_state["field_status"][cid] = status

        queue_export = queue_df[
            [
                "Consumer_ID",
                "Consumer_Name",
                "Short_Address",
                "Area",
                "Substation",
                "Feeder_ID",
                "Risk_Score",
                "Risk_Level",
                "Billed_Units_30D",
                "Estimated_Unbilled_Units",
                "Estimated_Total_Consumed_Units_30D",
                "Estimated_Billing_Coverage_Pct",
                "Priority_Score",
                "Why_Flagged",
                "Action",
            ]
        ].copy()

        queue_export["Field_Status"] = queue_export["Consumer_ID"].map(
            st.session_state["field_status"]
        ).fillna("PENDING")

        queue_csv = queue_export.to_csv(
            index=False,
        ).encode("utf-8")

        st.download_button(
            "EXPORT SHIFT QUEUE",
            data=queue_csv,
            file_name="wattguard_chennai_shift_queue.csv",
            mime="text/csv",
        )

# ============================================================
# PAGE 5 — MODEL STATUS
# ============================================================

elif page == "MODEL STATUS":

    st.markdown(
        '<div class="ops-label">MODEL HEALTH / VALIDATION</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.markdown(
        kpi(
            "42,372",
            "Dataset consumers",
            "SGCC public dataset",
            "blue",
        ),
        unsafe_allow_html=True,
    )

    m2.markdown(
        kpi(
            "1,035",
            "Usage days",
            "Consumption columns",
            "blue",
        ),
        unsafe_allow_html=True,
    )

    m3.markdown(
        kpi(
            "0.764",
            "ROC-AUC",
            "Random Forest V3",
            "green",
        ),
        unsafe_allow_html=True,
    )

    m4.markdown(
        kpi(
            "0.45",
            "Investigation threshold",
            "Operational prototype",
            "amber",
        ),
        unsafe_allow_html=True,
    )

    m5.markdown(
        kpi(
            "0.47",
            "Recall @ 0.45",
            "Theft-labelled class",
            "amber",
        ),
        unsafe_allow_html=True,
    )

    st.write("")

    # --------------------------------------------------------
    # TOP-K INSPECTION VALIDATION
    # --------------------------------------------------------

    if (
        evaluation_df is not None
        and "Priority_Score" in evaluation_df.columns
        and "Actual_Label" in evaluation_df.columns
    ):
        validation_ranked = (
            evaluation_df
            .sort_values(
                "Priority_Score",
                ascending=False,
            )
            .reset_index(drop=True)
        )

        validation_base_rate = float(
            validation_ranked[
                "Actual_Label"
            ].mean()
        )

        topk_results = []

        for k in [25, 50, 100, 250]:
            actual_k = min(
                k,
                len(validation_ranked),
            )

            subset_k = validation_ranked.head(
                actual_k
            )

            theft_k = int(
                subset_k[
                    "Actual_Label"
                ].sum()
            )

            precision_k = (
                theft_k / actual_k
                if actual_k > 0
                else 0.0
            )

            lift_k = (
                precision_k
                / validation_base_rate
                if validation_base_rate > 0
                else 0.0
            )

            random_expected = (
                actual_k
                * validation_base_rate
            )

            topk_results.append(
                {
                    "k": actual_k,
                    "theft": theft_k,
                    "precision": precision_k,
                    "lift": lift_k,
                    "random_expected": random_expected,
                }
            )

        cards = []

        for idx, result in enumerate(
            topk_results
        ):
            card_cls = (
                "proof-card best"
                if idx == 0
                else "proof-card"
            )

            width_pct = min(
                100,
                max(
                    0,
                    result["precision"] * 100,
                ),
            )

            cards.append(
                f"""
<div class="{card_cls}">
    <div class="proof-k">Top {result['k']} inspections</div>
    <div class="proof-v">{result['theft']} / {result['k']}</div>
    <div class="proof-s">
        Theft-labelled cases found in the highest-priority queue
    </div>
    <div class="precision-track">
        <div class="precision-fill" style="width:{width_pct:.1f}%"></div>
    </div>
    <div class="lift-value">
        {result['precision']*100:.0f}% PRECISION · {result['lift']:.2f}× LIFT
    </div>
</div>
"""
            )

        first_result = topk_results[0]

        render_html(
            f"""
<div class="validation-shell">

    <div class="validation-head">
        <div>
            <div class="validation-title">
                INSPECTION EFFICIENCY BENCHMARK
            </div>
            <div class="validation-sub">
                Held-out SGCC evaluation set · {len(validation_ranked):,} consumers ·
                only {validation_base_rate*100:.2f}% are theft-labelled.
                This test asks whether WattGuard concentrates those labelled cases
                near the top of the field-inspection queue.
            </div>
        </div>

        <div class="validation-badge">
            OPERATIONAL PROOF<br>
            PRIORITY RANKING VALIDATED
        </div>
    </div>

    <div class="proof-grid">
        {''.join(cards)}
    </div>

</div>
"""
        )

        render_html(
            f"""
<div class="random-proof">

    <div class="random-node random">
        <div class="random-k">Random inspection · 25 visits</div>
        <div class="random-v">≈ {first_result['random_expected']:.1f} cases</div>
        <div class="random-s">
            Expected theft-labelled cases at the {validation_base_rate*100:.2f}%
            evaluation prevalence.
        </div>
    </div>

    <div class="random-op">→</div>

    <div class="random-node wg">
        <div class="random-k">WattGuard top 25</div>
        <div class="random-v">{first_result['theft']} cases</div>
        <div class="random-s">
            Theft-labelled cases actually present in WattGuard's highest-priority 25.
        </div>
    </div>

    <div class="random-node result">
        <div class="random-k">Inspection concentration</div>
        <div class="random-v">{first_result['lift']:.2f}×</div>
        <div class="random-s">
            Lift over random inspection · Precision@25 =
            {first_result['precision']*100:.0f}%.
        </div>
    </div>

</div>
"""
        )

        st.caption(
            "Interpretation: these are held-out dataset labels used for model "
            "evaluation. In real deployment, a WattGuard alert remains an "
            "inspection priority and does not by itself confirm electricity theft."
        )


        # ----------------------------------------------------
        # Operational workload illustration
        # ----------------------------------------------------

        if (
            first_result["theft"] > 0
            and validation_base_rate > 0
        ):
            random_visits_for_same_yield = (
                first_result["theft"]
                / validation_base_rate
            )

            estimated_visit_reduction = (
                1
                - (
                    first_result["k"]
                    / random_visits_for_same_yield
                )
            ) * 100

            render_html(
                f"""
<div class="ops-proof">
    <div class="validation-title">
        FIELD-WORKLOAD EFFICIENCY ILLUSTRATION
    </div>
    <div class="validation-sub">
        How many inspections would be expected to produce the same
        {first_result['theft']} theft-labelled cases at the evaluation base rate?
    </div>

    <div class="ops-proof-grid">

        <div class="ops-proof-node random">
            <div class="ops-proof-k">Random inspection expectation</div>
            <div class="ops-proof-v">≈ {random_visits_for_same_yield:.0f} visits</div>
            <div class="ops-proof-s">
                Expected visits to encounter {first_result['theft']} labelled cases
                at a {validation_base_rate*100:.2f}% prevalence.
            </div>
        </div>

        <div class="ops-proof-op">→</div>

        <div class="ops-proof-node wg">
            <div class="ops-proof-k">WattGuard ranked queue</div>
            <div class="ops-proof-v">{first_result['k']} visits</div>
            <div class="ops-proof-s">
                Top-ranked queue contains the same
                {first_result['theft']} theft-labelled cases in this evaluation.
            </div>
        </div>

        <div class="ops-proof-op">→</div>

        <div class="ops-proof-node save">
            <div class="ops-proof-k">Illustrative workload reduction</div>
            <div class="ops-proof-v">{estimated_visit_reduction:.0f}%</div>
            <div class="ops-proof-s">
                Statistical evaluation illustration — not a guaranteed field saving.
            </div>
        </div>

    </div>
</div>
"""
            )


    else:
        st.warning(
            "Top-K validation requires data/wattguard_evaluation.csv "
            "with Priority_Score and Actual_Label."
        )

    left, right = st.columns(2)

    with left:
        render_html(
            """
<div class="panel">
    <div class="panel-head">
        <div class="panel-title">DATA BALANCE</div>
        <div class="panel-meta">SGCC SOURCE</div>
    </div>
    <div style="font-family:var(--mono);font-size:11px;line-height:2;">
        NORMAL LABELS <b>38,757</b><br>
        THEFT LABELS <b>3,615</b><br>
        CLASS IMBALANCE <b>PRESENT</b><br>
        FEATURE SET <b>BEHAVIOURAL AGGREGATES</b>
    </div>
</div>
"""
        )

    with right:
        render_html(
            """
<div class="panel">
    <div class="panel-head">
        <div class="panel-title">THRESHOLD = 0.45</div>
        <div class="panel-meta">CURRENT TEST-SPLIT METRICS</div>
    </div>
    <div style="font-family:var(--mono);font-size:11px;line-height:2;">
        PRECISION <b>0.27</b><br>
        RECALL <b>0.47</b><br>
        F1 SCORE <b>0.34</b><br>
        PURPOSE <b>INSPECTION TRIAGE</b>
    </div>
</div>
"""
        )

    render_html(
        """
<div class="panel">
    <div class="panel-head">
        <div class="panel-title">WATTGUARD DECISION FLOW</div>
        <div class="panel-meta">PRODUCT LOGIC</div>
    </div>
    <div style="font-family:var(--mono);font-size:14px;letter-spacing:.45px;line-height:2.2;">
        DETECT → EXPLAIN → QUANTIFY → PRIORITIZE → FIELD VERIFY
    </div>
</div>
"""
    )

    render_html(
        """
<div class="note">
    <strong>MODEL INTERPRETATION</strong><br><br>
    WattGuard's current Risk Score is the Random Forest model output used as an
    investigation score. It should not be described as a calibrated probability
    of theft. The "Why Flagged" field currently uses behavioural indicators and
    rule-based explanations; model-level SHAP explanations can be added later.
</div>
"""
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="smallprint">
WATTGUARD AI · PS-AI05 · HACKATHON PROTOTYPE<br>
MODEL TRAINING: SGCC PUBLIC ELECTRICITY-THEFT DATASET.<br>
CHENNAI AREA, SUBSTATION AND FEEDER LABELS IN THIS DEMO ARE SYNTHETIC MAPPINGS FOR
INTERFACE DEMONSTRATION AND DO NOT REPRESENT REAL CONSUMER IDENTITIES OR ACTUAL
UTILITY INFRASTRUCTURE. "BILLED / RECORDED" IS A 30-DAY METER-HISTORY-DERIVED
EQUIVALENT UNLESS AN OFFICIAL BILLING FIELD IS CONNECTED. "ESTIMATED THEFT /
UNBILLED" IS AN UNEXPLAINED-USAGE ESTIMATE, NOT CONFIRMED THEFT. ₹ VALUES ARE
PROTOTYPE ESTIMATES BASED ON THE SELECTED TARIFF ASSUMPTION. A WATTGUARD ALERT
IS AN INVESTIGATION PRIORITY, NOT A FINAL DETERMINATION OF ELECTRICITY THEFT.
</div>
""",
    unsafe_allow_html=True,
)
