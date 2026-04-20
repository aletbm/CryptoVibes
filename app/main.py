import streamlit as st
from config import PAGE_CONFIG, inject_css
from data import load_mart, load_fear_greed, load_mart_all, load_fear_greed_all
from components.sidebar import render_sidebar
from components.kpi_cards import render_kpi_cards
from components.price_chart import render_price_chart
from components.sentiment_chart import render_sentiment_distribution
from components.comparison_chart import render_comparison_chart

st.set_page_config(**PAGE_CONFIG)
inject_css()

filters = render_sidebar()
coin = filters["coin"]
compare = filters["compare"]
days = filters["days"]

if days == "all":
    df_mart = load_mart_all()
    df_fg = load_fear_greed_all()
else:
    df_mart = load_mart(days)
    df_fg = load_fear_greed(days)

# ── Header
st.markdown(
    '<div class="cv-header">'
    '<div class="cv-header-left">'
    '<span class="cv-logo">◈ CryptoVibes</span>'
    '<span class="cv-tagline">does sentiment predict price?</span>'
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown('<div class="cv-line"></div>', unsafe_allow_html=True)

# ── KPI row
render_kpi_cards(df_mart, df_fg, coin)

st.markdown('<div class="cv-line-sm"></div>', unsafe_allow_html=True)

# ── Charts: price (wide) + sentiment (narrow)
col1, col2 = st.columns([3, 1], gap="large")
with col1:
    render_price_chart(df_mart, coin)
with col2:
    render_sentiment_distribution(df_fg)

# ── Comparison (optional)
if compare:
    st.markdown('<div class="cv-line-sm"></div>', unsafe_allow_html=True)
    render_comparison_chart(df_mart, coin, compare)
