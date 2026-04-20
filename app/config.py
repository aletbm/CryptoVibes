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

.stMainBlockContainer {{ padding: 1rem 3rem 3rem 3rem !important;}}

[data-testid="stSidebar"] {{
    background: {c["surface"]} !important;
    border-right: 1px solid {c["border"]} !important;
}}

[data-testid="stSidebarHeader"] {{
    height: 10px;
}}

[data-testid="stSidebarUserContent"] * {{
    color: {c["text"]} !important;
    font-family: 'JetBrains Mono', monospace !important;
}}

section[data-testid="stSidebar"] > div {{
    padding-top: 2rem;
}}

.cv-header {{
    display: flex;
    align-items: baseline;
    gap: 1rem;
    padding: 1.5rem 0 1rem 0;
    border-bottom: 1px solid {c["border"]};
    margin-bottom: 1.5rem;
}}

.cv-logo {{
    font-family: 'Quantico', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    color: {c["accent"]};
    letter-spacing: -0.02em;
    text-shadow: 0 0 20px {c["accent_glow"]};
}}

.cv-tagline {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: {c["text_muted"]};
    letter-spacing: 0.1em;
    text-transform: lowercase;
}}

.cv-divider {{
    height: 1px;
    background: {c["border"]};
    margin: 1.5rem 0;
}}

.cv-card {{
    background: {c["surface"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
    padding: 2rem 1.5rem;
    position: relative;
    overflow: hidden;
    height: auto;
}}

.cv-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, {c["accent_dim"]}, transparent);
}}

.cv-card-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem !important;
    color: {c["text_muted"]};
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}}

.cv-card-value {{
    font-family: "Quantico", sans-serif;
    font-weight: 400;
    font-size: 1.5rem !important;
    line-height: 1;
    color: {c["text"]};
    letter-spacing: -0.03em;
}}

.cv-card-value.positive {{ color: {c["accent"]}; }}
.cv-card-value.negative {{ color: {c["fear"]}; }}

.cv-card-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem !important;
    color: {c["text_muted"]};
    margin-top: 0.5rem;
}}

.cv-bar-track {{
    background: {c["surface2"]};
    border-radius: 2px;
    height: 3px;
    margin-top: 0.75rem;
    overflow: hidden;
}}

.cv-bar-fill {{
    height: 100%;
    border-radius: 2px;
    background: {c["accent"]};
    box-shadow: 0 0 6px {c["accent"]};
}}

.cv-bar-fill.fear-bar {{ background: {c["fear"]}; box-shadow: 0 0 6px {c["fear"]}; }}

.cv-fg-badge {{
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    letter-spacing: 0.08em;
    margin-top: 0.5rem;
}}

.cv-section-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: {c["text_muted"]};
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}}

.stSelectbox > div > div {{
    background: {c["surface"]} !important;
    border: 1px solid {c["border"]} !important;
    border-radius: 8px !important;
    color: {c["text"]} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}}

.stSelectbox label {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    color: {c["text_muted"]} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}}

.stSlider > div > div > div {{
    color: {c["accent"]} !important;
}}

.stSlider label {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    color: {c["text_muted"]} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}}

div[data-testid="stMarkdownContainer"] > p{{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    color: {c["text_muted"]} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}}

div[data-testid="metric-container"] {{
    display: none;
}}


/*footer, #MainMenu, header {{ visibility: hidden; }}*/

::-webkit-scrollbar {{ width: 4px; background: {c["bg"]}; }}
::-webkit-scrollbar-thumb {{ background: {c["border"]}; border-radius: 2px; }}
</style>
""",
        unsafe_allow_html=True,
    )
