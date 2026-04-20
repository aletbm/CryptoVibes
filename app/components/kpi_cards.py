import streamlit as st
import pandas as pd
from config import COLORS, FG_COLORS


def _price_card(df_coin: pd.DataFrame):
    if df_coin.empty:
        st.markdown(
            '<div class="cv-card"><p class="cv-card-label">PRICE</p><p class="cv-card-value">—</p></div>',
            unsafe_allow_html=True,
        )
        return

    latest = df_coin.iloc[-1]
    price = latest["close_price_usd"]
    change = latest["avg_price_change_pct_24h"]
    change = change if pd.notna(change) else 0
    symbol = latest["symbol"]

    sign = "+" if change >= 0 else ""
    bar_pct = min(abs(change) / 20 * 100, 100)
    bar_class = "" if change >= 0 else "fear-bar"

    if price >= 1000:
        price_str = f"${price:,.0f}"
    elif price >= 1:
        price_str = f"${price:,.2f}"
    else:
        price_str = f"${price:.6f}"

    st.markdown(
        f"""
<div class="cv-card">
    <p class="cv-card-label">CURRENT PRICE — {symbol}</p>
    <p class="cv-card-value">{price_str}</p>
    <p class="cv-card-sub">{sign}{change:.2f}% last 24h</p>
    <div class="cv-bar-track">
        <div class="cv-bar-fill {bar_class}" style="width:{bar_pct}%"></div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _fg_card(df_fg: pd.DataFrame):
    c = COLORS
    if df_fg.empty:
        st.markdown(
            '<div class="cv-card"><p class="cv-card-label">FEAR & GREED</p><p class="cv-card-value">—</p></div>',
            unsafe_allow_html=True,
        )
        return

    latest = df_fg.iloc[-1]
    value = int(latest["fg_value"])
    label = latest["fg_label"]
    change = latest["value_change_vs_prev_day"]
    change = change if pd.notna(change) else 0

    color = FG_COLORS.get(label, c["text_muted"])
    bar_pct = value
    bar_style = f"background:{color}; box-shadow: 0 0 6px {color};"
    sign = "+" if change and change >= 0 else ""
    change_str = f"{sign}{int(change)}" if pd.notna(change) else "—"

    st.markdown(
        f"""
<div class="cv-card">
    <p class="cv-card-label">FEAR & GREED INDEX</p>
    <p class="cv-card-value" style="color:{color}">{value}</p>
    <span class="cv-fg-badge" style="background:{color}22; color:{color}; border:1px solid {color}44">{label}</span>
    <p class="cv-card-sub">{change_str} vs yesterday</p>
    <div class="cv-bar-track">
        <div class="cv-bar-fill" style="width:{bar_pct}%; {bar_style}"></div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _alignment_card(df_coin: pd.DataFrame):
    c = COLORS
    if df_coin.empty or "price_vs_sentiment_alignment" not in df_coin.columns:
        st.markdown(
            '<div class="cv-card"><p class="cv-card-label">ALIGNMENT</p><p class="cv-card-value">—</p></div>',
            unsafe_allow_html=True,
        )
        return

    counts = df_coin["price_vs_sentiment_alignment"].value_counts()
    total = len(df_coin)
    aligned = counts.get("aligned", 0)
    misaligned = counts.get("misaligned", 0)
    aligned_pct = aligned / total * 100 if total else 0
    misaligned_pct = misaligned / total * 100 if total else 0

    dominant = "aligned" if aligned >= misaligned else "misaligned"
    dom_color = c["aligned"] if dominant == "aligned" else c["misaligned"]
    dom_pct = aligned_pct if dominant == "aligned" else misaligned_pct

    st.markdown(
        f"""
<div class="cv-card">
    <p class="cv-card-label">SENTIMENT ALIGNMENT</p>
    <p class="cv-card-value" style="color:{dom_color}">{dom_pct:.0f}%</p>
    <p class="cv-card-sub">price follows sentiment</p>
    <div class="cv-bar-track">
        <div class="cv-bar-fill" style="width:{aligned_pct:.0f}%; background:{c["aligned"]}; box-shadow:0 0 6px {c["aligned"]};"></div>
    </div>
    <p class="cv-card-sub" style="margin-top:0.4rem">{aligned} aligned · {misaligned} misaligned · {total - aligned - misaligned} neutral</p>
</div>
""",
        unsafe_allow_html=True,
    )


def _volume_card(df_coin: pd.DataFrame):
    if df_coin.empty:
        st.markdown(
            '<div class="cv-card"><p class="cv-card-label">VOLUME</p><p class="cv-card-value">—</p></div>',
            unsafe_allow_html=True,
        )
        return

    latest = df_coin.iloc[-1]
    vol = latest["avg_volume_usd"]

    if vol >= 1e9:
        vol_str = f"${vol / 1e9:.1f}B"
    elif vol >= 1e6:
        vol_str = f"${vol / 1e6:.0f}M"
    else:
        vol_str = f"${vol:,.0f}"

    avg_vol = df_coin["avg_volume_usd"].mean()
    vol_vs_avg = (vol / avg_vol - 1) * 100 if avg_vol else 0
    sign = "+" if vol_vs_avg >= 0 else ""
    bar_pct = min(vol / avg_vol * 50, 100) if avg_vol else 50

    st.markdown(
        f"""
<div class="cv-card">
    <p class="cv-card-label">24H VOLUME</p>
    <p class="cv-card-value">{vol_str}</p>
    <p class="cv-card-sub">{sign}{vol_vs_avg:.1f}% vs period avg</p>
    <div class="cv-bar-track">
        <div class="cv-bar-fill" style="width:{bar_pct:.0f}%"></div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_kpi_cards(df_mart: pd.DataFrame, df_fg: pd.DataFrame, coin: str):
    df_coin = (
        df_mart[df_mart["coin_id"] == coin].copy()
        if not df_mart.empty
        else pd.DataFrame()
    )

    col1, col2, col3, col4 = st.columns(4, gap="small")
    with col1:
        _price_card(df_coin)
    with col2:
        _fg_card(df_fg)
    with col3:
        _alignment_card(df_coin)
    with col4:
        _volume_card(df_coin)
