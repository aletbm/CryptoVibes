import streamlit as st

PAGE_CONFIG = {
    "page_title": "CryptoVibes",
    "page_icon": "◈",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

COLORS = {
    "bg": "#0a0a0a",
    "surface": "#111111",
    "surface2": "#1a1a1a",
    "border": "#1f1f1f",
    "accent": "#39ff14",
    "accent_dim": "#2bc410",
    "accent_glow": "rgba(57,255,20,0.15)",
    "accent_glow_sm": "rgba(57,255,20,0.08)",
    "text": "#ffffff",
    "text_muted": "#888888",
    "text_dim": "#444444",
    "fear": "#ff4444",
    "greed": "#39ff14",
    "neutral": "#888888",
    "aligned": "#39ff14",
    "misaligned": "#ff4444",
}

COIN_LABELS = {
    "bitcoin": "BTC — Bitcoin",
    "ethereum": "ETH — Ethereum",
    "binancecoin": "BNB — BNB",
    "solana": "SOL — Solana",
    "ripple": "XRP — XRP",
    "dogecoin": "DOGE — Dogecoin",
    "cardano": "ADA — Cardano",
    "avalanche-2": "AVAX — Avalanche",
    "shiba-inu": "SHIB — Shiba Inu",
    "polkadot": "DOT — Polkadot",
}

FG_COLORS = {
    "Extreme Fear": "#ff2222",
    "Fear": "#ff8844",
    "Neutral": "#888888",
    "Greed": "#88dd44",
    "Extreme Greed": "#39ff14",
}


def inject_css():
    c = COLORS
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Quantico:ital,wght@0,400;0,700;1,400;1,700&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    background: {c["bg"]} !important;
    color: {c["text"]} !important;
    font-family: 'JetBrains Mono', monospace;
}}

.stMainBlockContainer {{ padding: 0 3.5rem 4rem 3.5rem !important; }}

[data-testid="stSidebar"] {{
    background: {c["bg"]} !important;
    border-right: 1px solid {c["border"]} !important;
}}

[data-testid="stSidebarHeader"] {{ height: 10px; }}

[data-testid="stSidebarUserContent"] * {{
    color: {c["text"]} !important;
    font-family: 'JetBrains Mono', monospace !important;
}}

section[data-testid="stSidebar"] > div {{ padding-top: 2.5rem; }}

.cv-header {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding: 2.5rem 0 1.5rem 0;
}}

.cv-header-left {{
    display: flex;
    align-items: baseline;
    gap: 1.25rem;
}}

.cv-logo {{
    font-family: 'Quantico', sans-serif;
    font-weight: 700;
    font-size: 1.3rem;
    color: {c["accent"]};
    letter-spacing: 0.04em;
}}

.cv-tagline {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: {c["text_dim"]};
    letter-spacing: 0.1em;
}}

.cv-header-date {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: {c["text_dim"]};
    letter-spacing: 0.08em;
}}

.cv-line {{
    height: 1px;
    background: {c["border"]};
    margin: 0 0 2.5rem 0;
}}

.cv-line-sm {{
    height: 1px;
    background: {c["border"]};
    margin: 2rem 0;
}}

.cv-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.56rem;
    color: {c["text_dim"]};
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 1.75rem;
}}

.cv-kpi-row {{
    display: flex;
    gap: 0;
    margin-bottom: 2.5rem;
}}

.cv-kpi-item {{
    flex: 1;
    padding: 0 2rem 0 0;
    border-right: 1px solid {c["border"]};
    margin-right: 2rem;
}}

.cv-kpi-item:last-child {{
    border-right: none;
    margin-right: 0;
    padding-right: 0;
}}

.cv-kpi-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.56rem;
    color: {c["text_dim"]};
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}}

.cv-kpi-value {{
    font-family: 'Quantico', sans-serif;
    font-weight: 400;
    font-size: 1.9rem;
    line-height: 1;
    color: {c["text"]};
    letter-spacing: -0.02em;
    margin-bottom: 0.35rem;
}}

.cv-kpi-value.positive {{ color: {c["accent"]}; }}
.cv-kpi-value.negative {{ color: {c["fear"]}; }}

.cv-kpi-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: {c["text_muted"]};
    margin-top: 0.2rem;
}}

.cv-kpi-bar {{
    height: 2px;
    background: {c["border"]};
    margin-top: 0.9rem;
    border-radius: 1px;
    overflow: hidden;
}}

.cv-kpi-bar-fill {{
    height: 100%;
    border-radius: 1px;
    background: {c["accent"]};
}}

.cv-kpi-bar-fill.neg {{ background: {c["fear"]}; }}

.cv-badge {{
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.52rem;
    padding: 0.15rem 0.5rem;
    border-radius: 2px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}}

.cv-section-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.56rem;
    color: {c["text_dim"]};
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}}

.stSelectbox > div > div {{
    background: {c["bg"]} !important;
    border: 1px solid {c["border"]} !important;
    border-radius: 3px !important;
    color: {c["text"]} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}}

.stSelectbox label {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.56rem !important;
    color: {c["text_dim"]} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}}

.stSlider > div > div > div {{ color: {c["accent"]} !important; }}

.stSlider label {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.56rem !important;
    color: {c["text_dim"]} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}}

div[data-testid="stMarkdownContainer"] > p {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.56rem !important;
    color: {c["text_dim"]} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}}

div[data-testid="metric-container"] {{ display: none; }}

::-webkit-scrollbar {{ width: 3px; background: {c["bg"]}; }}
::-webkit-scrollbar-thumb {{ background: {c["border"]}; border-radius: 2px; }}
</style>
""",
        unsafe_allow_html=True,
    )
