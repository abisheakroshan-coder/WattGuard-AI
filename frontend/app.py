
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="WattGuard AI — EB Control Room",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "data" / "wattguard_output.csv"
FULL_DATA_FILE = ROOT / "notebooks" / "full.csv"

# ---------------------------------------------------------
# INDUSTRIAL / EB CONTROL-ROOM THEME
# ---------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap');

:root{
  --bg:#0b1116;
  --panel:#111920;
  --panel2:#0e151b;
  --line:#26323b;
  --line2:#1b252d;
  --text:#e8eef3;
  --muted:#8fa0ad;
  --faint:#60707b;
  --cyan:#36c6d3;
  --green:#3fb58f;
  --amber:#e3a53b;
  --red:#e55c4a;
  --blue:#5b93d3;
  --mono:'IBM Plex Mono', monospace;
  --ui:'Inter', sans-serif;
}
html, body, [class*="css"] {font-family:var(--ui);}
.stApp{
  background:
    linear-gradient(rgba(38,50,59,.20) 1px, transparent 1px) 0 0/32px 32px,
    linear-gradient(90deg, rgba(38,50,59,.20) 1px, transparent 1px) 0 0/32px 32px,
    var(--bg);
  color:var(--text);
}
.block-container{max-width:1380px;padding-top:1rem;padding-bottom:3rem;}
#MainMenu, footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}

.ctrl-head{
  display:flex;justify-content:space-between;align-items:center;
  border:1px solid var(--line);background:var(--panel2);
  padding:14px 16px;margin-bottom:8px;
}
.ctrl-brand{display:flex;align-items:center;gap:12px;}
.ctrl-icon{
  width:38px;height:38px;display:flex;align-items:center;justify-content:center;
  background:#15242e;border:1px solid #315364;color:var(--cyan);
  font-family:var(--mono);font-size:20px;font-weight:600;
}
.ctrl-title{font-size:20px;font-weight:700;letter-spacing:.2px;}
.ctrl-sub{font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:2px;}
.system-state{font-family:var(--mono);font-size:11px;color:var(--green);}
.system-state b{color:var(--text);font-weight:500;}
.status-dot{color:var(--green);margin-right:5px;}

.ticker{
  display:flex;gap:22px;flex-wrap:wrap;
  border:1px solid var(--line);border-top:none;background:#0d141a;
  padding:7px 14px;margin-bottom:14px;
  font-family:var(--mono);font-size:10.5px;color:var(--muted);
}
.ticker strong{color:var(--text);font-weight:500;}

.ops-label{
  font-family:var(--mono);font-size:10px;color:var(--faint);
  letter-spacing:1.3px;text-transform:uppercase;margin:8px 0 7px;
}

.kpi{
  border:1px solid var(--line);background:var(--panel);
  padding:13px 14px;min-height:88px;position:relative;
}
.kpi:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--cyan);}
.kpi.red:before{background:var(--red);}
.kpi.amber:before{background:var(--amber);}
.kpi.green:before{background:var(--green);}
.kpi .v{font-family:var(--mono);font-size:23px;font-weight:600;color:var(--text);}
.kpi .l{font-size:11px;color:var(--muted);margin-top:4px;text-transform:uppercase;letter-spacing:.4px;}
.kpi .s{font-family:var(--mono);font-size:9.5px;color:var(--faint);margin-top:5px;}

.panel{
  border:1px solid var(--line);background:var(--panel);
  padding:14px 15px;margin-bottom:14px;
}
.panel-head{
  display:flex;justify-content:space-between;align-items:flex-end;
  gap:10px;border-bottom:1px solid var(--line2);padding-bottom:9px;margin-bottom:11px;
}
.panel-title{font-size:13px;font-weight:600;letter-spacing:.2px;}
.panel-meta{font-family:var(--mono);font-size:9.5px;color:var(--faint);}

.alarm{
  border-left:3px solid var(--red);background:#171617;
  padding:10px 12px;margin-bottom:7px;border-top:1px solid #2b2828;border-right:1px solid #2b2828;border-bottom:1px solid #2b2828;
}
.alarm.amber{border-left-color:var(--amber);background:#191812;}
.alarm.green{border-left-color:var(--green);background:#111916;}
.alarm-id{font-family:var(--mono);font-size:12px;font-weight:600;color:var(--text);}
.alarm-meta{font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:3px;}

.riskbar{height:8px;background:#19242c;border:1px solid #283641;overflow:hidden;margin-top:7px;}
.riskbar > div{height:100%;background:var(--red);}
.riskbar.amber > div{background:var(--amber);}
.riskbar.green > div{background:var(--green);}

.badge{
  display:inline-block;padding:3px 7px;font-family:var(--mono);font-size:9.5px;
  border:1px solid var(--line);letter-spacing:.3px;
}
.badge.red{color:var(--red);border-color:#5a2d29;background:#1d1312;}
.badge.amber{color:var(--amber);border-color:#5e4821;background:#1c180f;}
.badge.green{color:var(--green);border-color:#245244;background:#101b17;}

.consumer-header{
  border:1px solid var(--line);background:var(--panel);
  padding:15px 16px;display:flex;justify-content:space-between;align-items:flex-start;
}
.consumer-id{font-family:var(--mono);font-size:18px;font-weight:600;}
.consumer-note{font-size:11px;color:var(--muted);margin-top:4px;}
.big-score{font-family:var(--mono);font-size:30px;font-weight:600;text-align:right;}
.big-score small{font-size:11px;color:var(--muted);font-weight:400;}

.note{
  border:1px solid var(--line);background:#0f171d;padding:11px 12px;
  font-size:12px;line-height:1.55;color:#cfd9e0;
}
.note strong{color:var(--text);}

.reason{
  border-bottom:1px solid var(--line2);padding:8px 0;font-size:12px;color:#ced7de;
}
.reason:last-child{border-bottom:none;}

.money{color:var(--amber);font-family:var(--mono);font-weight:600;}

div[data-testid="stDataFrame"]{border:1px solid var(--line);}
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div{
  border-radius:0!important;background:var(--panel2)!important;
}
.stButton button, .stDownloadButton button{
  border-radius:0!important;border:1px solid var(--line)!important;
  background:#142029!important;color:var(--text)!important;
  box-shadow:none!important;
}
.stButton button:hover, .stDownloadButton button:hover{
  border-color:var(--cyan)!important;color:var(--cyan)!important;
}
div[role="radiogroup"]{
  border:1px solid var(--line);background:#0e151b;padding:5px 7px;margin-bottom:12px;
}
hr{border-color:var(--line2)!important;}

.smallprint{
  font-family:var(--mono);font-size:9.5px;color:var(--faint);
  border-top:1px solid var(--line);padding-top:10px;margin-top:18px;
}

@media(max-width:850px){
  .ctrl-head{flex-direction:column;align-items:flex-start;}
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------
@st.cache_data
def load_output():
    if not OUTPUT_FILE.exists():
        return None
    d = pd.read_csv(OUTPUT_FILE)
    d["Consumer_ID"] = d["Consumer_ID"].astype(str)
    for c in ["Risk_Score", "Priority_Score", "Estimated_Unbilled_Units"]:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    return d

@st.cache_data
def load_full():
    if not FULL_DATA_FILE.exists():
        return None
    return pd.read_csv(FULL_DATA_FILE)

df = load_output()
raw_df = load_full()

if df is None:
    st.error("wattguard_output.csv not found in the data folder.")
    st.stop()

required = [
    "Consumer_ID", "Risk_Score", "Risk_Level",
    "Estimated_Unbilled_Units", "Priority_Score",
    "Why_Flagged", "Action"
]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error("Missing columns: " + ", ".join(missing))
    st.stop()

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def kpi(value, label, sub="", cls=""):
    return f"""
    <div class="kpi {cls}">
      <div class="v">{value}</div>
      <div class="l">{label}</div>
      <div class="s">{sub}</div>
    </div>
    """

def badge(level):
    x = str(level).upper()
    cls = "red" if x == "CRITICAL" else "amber" if x in ["HIGH","WATCH"] else "green"
    return f'<span class="badge {cls}">{x}</span>'

def get_history(consumer_id):
    if raw_df is None:
        return None
    try:
        idx = int(str(consumer_id).replace("WG-", ""))
    except Exception:
        return None
    if idx not in raw_df.index:
        return None

    row = raw_df.loc[idx]
    items = []
    for c in raw_df.columns:
        dt = pd.to_datetime(c, errors="coerce")
        if pd.isna(dt):
            continue
        val = pd.to_numeric(row[c], errors="coerce")
        if pd.isna(val):
            continue
        items.append((dt, float(val)))
    if not items:
        return None

    h = pd.DataFrame(items, columns=["Date", "Usage"]).sort_values("Date")
    h["30-Day Average"] = h["Usage"].rolling(30, min_periods=1).mean()
    return h

def field_note(row):
    reasons = str(row["Why_Flagged"]).replace("|", ", ")
    return (
        f"{row['Consumer_ID']} is ranked for inspection because the recorded "
        f"consumption pattern deviates from normal behaviour. Main signals: {reasons}. "
        f"Estimated unexplained consumption is {row['Estimated_Unbilled_Units']:.1f} units. "
        f"Recommended field action: {str(row['Action']).lower()}."
    )

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
now = datetime.now().strftime("%d-%m-%Y %H:%M")
st.markdown(
    f"""
<div class="ctrl-head">
  <div class="ctrl-brand">
    <div class="ctrl-icon">WG</div>
    <div>
      <div class="ctrl-title">WattGuard AI — Distribution Loss Control Centre</div>
      <div class="ctrl-sub">PS-AI05 · POWER THEFT & UNBILLED LOAD INVESTIGATION PLATFORM</div>
    </div>
  </div>
  <div class="system-state"><span class="status-dot">●</span><b>SYSTEM ONLINE</b> · MODEL READY</div>
</div>
<div class="ticker">
  <span>SHIFT STATUS <strong>ACTIVE</strong></span>
  <span>DATASET <strong>SGCC / 42,372 CONSUMERS</strong></span>
  <span>MODEL <strong>RANDOM FOREST V3</strong></span>
  <span>LAST REFRESH <strong>{now}</strong></span>
</div>
""",
    unsafe_allow_html=True,
)

page = st.radio(
    "Navigation",
    ["CONTROL ROOM", "CONSUMER DESK", "FIELD QUEUE", "MODEL STATUS"],
    horizontal=True,
    label_visibility="collapsed",
)

# ---------------------------------------------------------
# CONTROL ROOM
# ---------------------------------------------------------
if page == "CONTROL ROOM":
    st.markdown('<div class="ops-label">LIVE OPERATIONS SUMMARY</div>', unsafe_allow_html=True)

    tariff = st.number_input(
        "Demo tariff assumption (₹ / unit)",
        min_value=1.0, max_value=20.0, value=7.5, step=0.5,
        help="Used only to estimate potential revenue at risk. Actual tariffs vary by category."
    )

    high = int((df["Risk_Score"] >= 45).sum())
    critical = int((df["Risk_Score"] >= 70).sum())
    unbilled = float(df.loc[df["Risk_Score"] >= 45, "Estimated_Unbilled_Units"].clip(lower=0).sum())
    revenue = unbilled * tariff

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(kpi(f"{len(df):,}", "Consumers monitored", "Current analysis batch"), unsafe_allow_html=True)
    c2.markdown(kpi(f"{high:,}", "Active alerts", "Risk score ≥ 45", "amber"), unsafe_allow_html=True)
    c3.markdown(kpi(f"{critical:,}", "Critical alerts", "Risk score ≥ 70", "red"), unsafe_allow_html=True)
    c4.markdown(kpi(f"{unbilled:,.0f}", "Est. unbilled units", "Investigation estimate", "green"), unsafe_allow_html=True)
    c5.markdown(kpi(f"₹{revenue:,.0f}", "Revenue at risk", f"At ₹{tariff:.1f}/unit assumption", "amber"), unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1.65, 1])

    with left:
        st.markdown("""
        <div class="panel">
          <div class="panel-head">
            <div class="panel-title">ACTIVE ALARM REGISTER</div>
            <div class="panel-meta">SORTED BY INVESTIGATION PRIORITY</div>
          </div>
        """, unsafe_allow_html=True)

        capacity = st.slider(
            "Field team capacity today",
            min_value=5,
            max_value=min(100, len(df)),
            value=min(25, len(df)),
            step=5
        )
        queue = df.sort_values("Priority_Score", ascending=False).head(capacity)

        st.dataframe(
            queue[[
                "Consumer_ID", "Risk_Score", "Risk_Level",
                "Estimated_Unbilled_Units", "Priority_Score", "Action"
            ]],
            use_container_width=True,
            hide_index=True,
            height=465
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="panel">
          <div class="panel-head">
            <div class="panel-title">TOP LIVE ALARMS</div>
            <div class="panel-meta">FIRST 5 CASES</div>
          </div>
        """, unsafe_allow_html=True)

        top5 = df.sort_values("Priority_Score", ascending=False).head(5)
        for _, r in top5.iterrows():
            cls = "alarm" if r["Risk_Score"] >= 70 else "alarm amber"
            width = max(2, min(100, float(r["Risk_Score"])))
            st.markdown(
                f"""
                <div class="{cls}">
                  <div style="display:flex;justify-content:space-between;gap:8px;">
                    <span class="alarm-id">{r['Consumer_ID']}</span>
                    {badge(r['Risk_Level'])}
                  </div>
                  <div class="alarm-meta">
                    RISK {r['Risk_Score']:.1f} · PRIORITY {r['Priority_Score']:.1f}
                    · UNBILLED {r['Estimated_Unbilled_Units']:.1f} U
                  </div>
                  <div class="riskbar"><div style="width:{width}%"></div></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="panel">
          <div class="panel-head">
            <div class="panel-title">RISK PORTFOLIO</div>
            <div class="panel-meta">CURRENT BATCH</div>
          </div>
        """, unsafe_allow_html=True)

        counts = (
            df["Risk_Level"].astype(str).str.upper()
            .value_counts()
            .reindex(["CRITICAL", "HIGH", "WATCH", "LOW"])
            .fillna(0)
        )
        st.bar_chart(counts, height=250)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONSUMER DESK
# ---------------------------------------------------------
elif page == "CONSUMER DESK":
    st.markdown('<div class="ops-label">CONSUMER INVESTIGATION DESK</div>', unsafe_allow_html=True)

    consumer = st.selectbox("Select consumer", df["Consumer_ID"].tolist())
    row = df[df["Consumer_ID"] == consumer].iloc[0]

    st.markdown(
        f"""
        <div class="consumer-header">
          <div>
            <div class="consumer-id">{consumer}</div>
            <div class="consumer-note">AI-assisted investigation record · field confirmation required</div>
            <div style="margin-top:9px">{badge(row['Risk_Level'])}</div>
          </div>
          <div>
            <div class="big-score">{row['Risk_Score']:.1f}<small>/100</small></div>
            <div class="consumer-note" style="text-align:right">AI RISK SCORE</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    a,b,c,d = st.columns(4)
    a.markdown(kpi(f"{row['Priority_Score']:.1f}", "Priority score", "Investigation ranking", "red"), unsafe_allow_html=True)
    b.markdown(kpi(f"{row['Estimated_Unbilled_Units']:.1f}", "Possible unbilled units", "Prototype estimate", "amber"), unsafe_allow_html=True)
    c.markdown(kpi(str(row["Action"]), "Recommended action", "Human verification required", "green"), unsafe_allow_html=True)
    c2 = "red" if str(row["Risk_Level"]).upper()=="CRITICAL" else "amber"
    d.markdown(kpi(str(row["Risk_Level"]).upper(), "Alert severity", "Model assessment", c2), unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1.55, 1])

    with left:
        st.markdown("""
        <div class="panel">
          <div class="panel-head">
            <div class="panel-title">LOAD PROFILE / CONSUMPTION HISTORY</div>
            <div class="panel-meta">RAW SIGNAL + 30-DAY MOVING AVERAGE</div>
          </div>
        """, unsafe_allow_html=True)

        hist = get_history(consumer)
        if hist is not None:
            period = st.selectbox("Display window", ["90 days", "180 days", "365 days", "Full history"])
            if period == "90 days":
                h = hist.tail(90)
            elif period == "180 days":
                h = hist.tail(180)
            elif period == "365 days":
                h = hist.tail(365)
            else:
                h = hist

            st.line_chart(h.set_index("Date")[["Usage", "30-Day Average"]], height=360)

            historical_avg = hist["Usage"].mean()
            recent_avg = hist["Usage"].tail(30).mean()
            change = ((recent_avg-historical_avg)/historical_avg*100) if historical_avg > 0 else 0

            x1,x2,x3 = st.columns(3)
            x1.metric("Historical avg", f"{historical_avg:.1f}")
            x2.metric("Recent 30-day avg", f"{recent_avg:.1f}")
            x3.metric("Recent change", f"{change:+.1f}%")
        else:
            st.info("Raw consumption history unavailable for this consumer.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="panel">
          <div class="panel-head">
            <div class="panel-title">ALERT REASONING</div>
            <div class="panel-meta">WHY THIS CASE WAS FLAGGED</div>
          </div>
        """, unsafe_allow_html=True)

        for reason in str(row["Why_Flagged"]).split("|"):
            st.markdown(f'<div class="reason">→ {reason.strip()}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        tariff = st.number_input("Tariff for this estimate (₹ / unit)", 1.0, 20.0, 7.5, 0.5)
        case_value = max(0, row["Estimated_Unbilled_Units"]) * tariff

        st.markdown(
            f"""
            <div class="panel">
              <div class="panel-head">
                <div class="panel-title">COMMERCIAL IMPACT</div>
                <div class="panel-meta">PROTOTYPE ESTIMATE</div>
              </div>
              <div style="font-family:var(--mono);font-size:11px;color:var(--muted);">ESTIMATED REVENUE AT RISK</div>
              <div class="money" style="font-size:27px;margin-top:4px;">₹{case_value:,.0f}</div>
              <div style="font-size:10px;color:var(--faint);margin-top:5px;">Based on {row['Estimated_Unbilled_Units']:.1f} units × ₹{tariff:.1f}/unit.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="note">
              <strong>FIELD NOTE</strong><br><br>
              {field_note(row)}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="smallprint">
        IMPORTANT: WattGuard flags abnormal consumption for investigation. A risk score is not proof of theft.
        Confirmation must be made by an authorised electricity-board field inspection.
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# FIELD QUEUE
# ---------------------------------------------------------
elif page == "FIELD QUEUE":
    st.markdown('<div class="ops-label">FIELD OPERATIONS / DISPATCH</div>', unsafe_allow_html=True)
    st.subheader("Inspection Dispatch Board")

    capacity = st.number_input(
        "Inspections available this shift",
        min_value=1,
        max_value=min(200, len(df)),
        value=min(25, len(df))
    )
    q = df.sort_values("Priority_Score", ascending=False).head(int(capacity)).copy()

    if "field_status" not in st.session_state:
        st.session_state.field_status = {}

    statuses = ["PENDING", "ASSIGNED", "ON-SITE", "CONFIRMED", "NOT CONFIRMED", "RECHECK"]

    for rank, (_, r) in enumerate(q.iterrows(), start=1):
        cid = str(r["Consumer_ID"])
        with st.expander(
            f"{rank:02d}  |  {cid}  |  RISK {r['Risk_Score']:.1f}  |  PRIORITY {r['Priority_Score']:.1f}"
        ):
            a,b,c = st.columns(3)
            a.metric("Risk", f"{r['Risk_Score']:.1f}/100")
            b.metric("Est. unbilled", f"{r['Estimated_Unbilled_Units']:.1f} units")
            c.metric("Action", str(r["Action"]))

            st.write("**Reason:**", str(r["Why_Flagged"]))

            current = st.session_state.field_status.get(cid, "PENDING")
            status = st.selectbox(
                "Field status",
                statuses,
                index=statuses.index(current),
                key="field_" + cid
            )
            st.session_state.field_status[cid] = status

    export = q[[
        "Consumer_ID","Risk_Score","Risk_Level",
        "Estimated_Unbilled_Units","Priority_Score",
        "Why_Flagged","Action"
    ]].to_csv(index=False).encode("utf-8")

    st.download_button(
        "EXPORT SHIFT QUEUE",
        export,
        "wattguard_shift_queue.csv",
        "text/csv"
    )

# ---------------------------------------------------------
# MODEL STATUS
# ---------------------------------------------------------
elif page == "MODEL STATUS":
    st.markdown('<div class="ops-label">MODEL HEALTH / VALIDATION</div>', unsafe_allow_html=True)
    st.subheader("WattGuard Model Status")

    a,b,c,d = st.columns(4)
    a.markdown(kpi("42,372", "Consumers", "SGCC public dataset"), unsafe_allow_html=True)
    b.markdown(kpi("1,035", "Days history", "Per consumer"), unsafe_allow_html=True)
    c.markdown(kpi("0.764", "ROC-AUC", "Current V3 model", "green"), unsafe_allow_html=True)
    d.markdown(kpi("0.45", "Investigation threshold", "Operational setting", "amber"), unsafe_allow_html=True)

    st.write("")
    l,r = st.columns(2)

    with l:
        st.markdown("""
        <div class="panel">
          <div class="panel-head">
            <div class="panel-title">DATA BALANCE</div>
            <div class="panel-meta">TRAINING SOURCE</div>
          </div>
          <div style="font-family:var(--mono);font-size:12px;line-height:2;">
            NORMAL LABELS <b>38,757</b><br>
            THEFT LABELS <b>3,615</b><br>
            CLASS IMBALANCE <b>PRESENT</b>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with r:
        st.markdown("""
        <div class="panel">
          <div class="panel-head">
            <div class="panel-title">CURRENT THRESHOLD METRICS</div>
            <div class="panel-meta">THRESHOLD = 0.45</div>
          </div>
          <div style="font-family:var(--mono);font-size:12px;line-height:2;">
            PRECISION <b>0.27</b><br>
            RECALL <b>0.47</b><br>
            F1 SCORE <b>0.34</b>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
      <div class="panel-head">
        <div class="panel-title">WATTGUARD DECISION FLOW</div>
        <div class="panel-meta">PRODUCT LOGIC</div>
      </div>
      <div style="font-family:var(--mono);font-size:15px;letter-spacing:.5px;line-height:2;">
        DETECT → EXPLAIN → QUANTIFY → PRIORITIZE → FIELD VERIFY
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    """
<div class="smallprint">
WATTGUARD AI · PS-AI05 · HACKATHON PROTOTYPE ·
SGCC PUBLIC ELECTRICITY-THEFT DATA ·
₹ VALUES ARE ESTIMATES BASED ON USER-SELECTED DEMO TARIFF AND ARE NOT OFFICIAL BILLING FIGURES.
</div>
""",
    unsafe_allow_html=True
)
