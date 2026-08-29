import streamlit as st

# ============================================================
# PALETTE
# ============================================================
INK = "#0F1B24"
PANEL = "#16242E"
MANIFEST = "#E8E4D9"
RUST = "#C8763B"
SEAL = "#4F7A5B"
WAYBILL = "#3E6E8E"
ALERT = "#A63D40"
MUTED = "#5C6B73"

QUADRANT_COLORS = {
    "Intervene First": RUST, "Protect": WAYBILL,
    "Monitor / Investigate": ALERT, "Lower Priority": MUTED,
    "High Scale + High Risk": RUST, "High Scale + Low Risk": WAYBILL,
    "Low Scale + High Risk": ALERT, "Low Scale + Low Risk": MUTED,
}
FAILURE_TYPE_COLORS = {
    "Type 1 - Delivery-Driven": WAYBILL, "Type 2 - Intrinsic": ALERT,
    "Type 3 - Mixed": RUST, "Type 4 - Unclear": MUTED,
}

def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@500;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'IBM Plex Sans', sans-serif;
        color: {MANIFEST};
    }}

    .stApp {{
        background-color: {INK};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {PANEL};
        border-right: 1px solid rgba(232,228,217,0.08);
    }}

    h1, h2, h3 {{
        font-family: 'Zilla Slab', serif !important;
        font-weight: 700 !important;
        color: {MANIFEST} !important;
        letter-spacing: -0.01em;
    }}

    h1 {{ border-bottom: 2px solid {RUST}; padding-bottom: 0.4rem; }}

    p, .stCaption, [data-testid="stCaptionContainer"] {{
        font-family: 'IBM Plex Sans', sans-serif;
        color: {MANIFEST} !important;
        opacity: 0.85;
    }}

    /* Sidebar nav radio */
    div[role="radiogroup"] label {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    /* Tabs */
    button[data-baseweb="tab"] {{
        font-family: 'IBM Plex Mono', monospace !important;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {RUST} !important;
        border-bottom-color: {RUST} !important;
    }}

    /* Dataframes */
    [data-testid="stDataFrame"] {{
        border: 1px solid rgba(232,228,217,0.12);
        border-radius: 2px;
    }}

    /* Dividers */
    hr {{ border-color: rgba(232,228,217,0.12) !important; }}

    /* Kill Streamlit's default metric widget styling entirely - we use kpi_card() instead */
    [data-testid="stMetric"] {{ display: none; }}
    </style>
    """, unsafe_allow_html=True)


def kpi_card(label, value, sublabel="", tone="neutral"):
    """Renders a manifest-style KPI card. tone: 'good' | 'bad' | 'neutral'"""
    accent = {"good": SEAL, "bad": RUST, "neutral": WAYBILL}.get(tone, WAYBILL)
    html = f"""
    <div style="
        background:{PANEL}; border-left:3px solid {accent};
        padding:14px 16px; border-radius:2px; margin-bottom:8px;
        font-family:'IBM Plex Sans', sans-serif;
    ">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.7rem;
                    text-transform:uppercase; letter-spacing:0.08em; opacity:0.65;">
            {label}
        </div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:1.9rem;
                    font-weight:600; color:{MANIFEST}; margin-top:2px;">
            {value}
        </div>
        <div style="font-size:0.78rem; opacity:0.6; margin-top:2px;">{sublabel}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def stamp(text, tone="neutral"):
    """Renders an ink-stamp style badge - the signature element."""
    color = {"good": SEAL, "bad": RUST, "critical": ALERT, "neutral": WAYBILL, "muted": MUTED}.get(tone, WAYBILL)
    html = f"""
    <span style="
        display:inline-block; border:1.5px solid {color}; color:{color};
        font-family:'IBM Plex Mono',monospace; font-size:0.7rem; font-weight:600;
        text-transform:uppercase; letter-spacing:0.06em; padding:3px 10px;
        border-radius:2px; transform:rotate(-1.5deg); margin:2px 4px 2px 0;
        background:rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08);
    ">{text}</span>
    """
    return html


def hero(title, subtitle):
    html = f"""
    <div style="border-bottom:2px solid {RUST}; padding-bottom:14px; margin-bottom:24px;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:{RUST};
                    text-transform:uppercase; letter-spacing:0.12em; margin-bottom:4px;">
            MARKETPLACE MANIFEST — RISK & GROWTH TRACKING
        </div>
        <div style="font-family:'Zilla Slab',serif; font-weight:700; font-size:2.3rem; color:{MANIFEST};">
            {title}
        </div>
        <div style="font-size:1rem; opacity:0.7; margin-top:4px;">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def styled_fig(fig, height=420):
    """Applies consistent manifest-theme styling to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor=PANEL, plot_bgcolor=PANEL,
        font=dict(family="IBM Plex Sans, sans-serif", color=MANIFEST, size=13),
        height=height,
        margin=dict(l=40, r=20, t=30, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(family="IBM Plex Mono, monospace", size=11)),
        xaxis=dict(gridcolor="rgba(232,228,217,0.08)", zerolinecolor="rgba(232,228,217,0.15)"),
        yaxis=dict(gridcolor="rgba(232,228,217,0.08)", zerolinecolor="rgba(232,228,217,0.15)"),
    )
    return fig
