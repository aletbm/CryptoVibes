import streamlit as st
from config import COIN_LABELS, COLORS


def render_sidebar() -> dict:
    c = COLORS

    with st.sidebar:
        st.markdown(
            f"""
<div style="
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: {c["text_dim"]};
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid {c["border"]};
">
    ◈ CryptoVibes<br>
    <span style="color:{c["text_dim"]};letter-spacing:0.08em;">market sentiment tracker</span>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<p class="cv-section-title">primary coin</p>',
            unsafe_allow_html=True,
        )

        coin_id = st.selectbox(
            "coin",
            options=list(COIN_LABELS.keys()),
            format_func=lambda x: COIN_LABELS[x],
            label_visibility="collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<p class="cv-section-title">compare with</p>',
            unsafe_allow_html=True,
        )

        compare_options = [k for k in COIN_LABELS.keys() if k != coin_id]
        compare_coins = st.multiselect(
            "compare",
            options=compare_options,
            default=[],
            format_func=lambda x: COIN_LABELS[x],
            label_visibility="collapsed",
            max_selections=6,
            placeholder="up to 6 coins...",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<p class="cv-section-title">time range</p>',
            unsafe_allow_html=True,
        )

        time_options = [7, 15, 30, 60, 90, 180, 365, 730, "all"]
        time_labels = {
            7: "7d",
            15: "15d",
            30: "30d",
            60: "60d",
            90: "90d",
            180: "180d",
            365: "1y",
            730: "2y",
            "all": "all",
        }

        days = st.select_slider(
            "days",
            options=time_options,
            value=365,
            label_visibility="collapsed",
            format_func=lambda x: time_labels[x],
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
<div style="
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    color: {c["text_dim"]};
    letter-spacing: 0.08em;
    line-height: 2;
    padding-top: 1rem;
    border-top: 1px solid {c["border"]};
">
    sources<br>
    yfinance · CoinGecko · Alternative.me<br><br>
    updated daily 00:00 UTC
</div>
""",
            unsafe_allow_html=True,
        )

    return {"coin": coin_id, "compare": compare_coins, "days": days}
