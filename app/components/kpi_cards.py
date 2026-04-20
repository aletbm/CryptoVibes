import streamlit as st
import pandas as pd
from config import COLORS, FG_COLORS


def _price_kpi(df_coin: pd.DataFrame) -> str:
    if df_coin.empty:
        return '<div class="cv-kpi-item"><div class="cv-kpi-label">price</div><div class="cv-kpi-value">—</div></div>'

    latest = df_coin.iloc[-1]
    price = latest["close_price_usd"]
    change = latest["avg_price_change_pct_24h"]
    change = change if pd.notna(change) else 0
    symbol = latest["symbol"]

    sign = "+" if change >= 0 else ""
    bar_pct = min(abs(change) / 20 * 100, 100)
    bar_class = "" if change >= 0 else " neg"

    if price >= 1000:
        price_str = f"${price:,.0f}"
    elif price >= 1:
        price_str = f"${price:,.2f}"
    else:
        price_str = f"${price:.6f}"

    return f"""
<div class="cv-kpi-item">
    <div class="cv-kpi-label">price — {symbol}</div>
    <div class="cv-kpi-value">{price_str}</div>
    <div class="cv-kpi-sub">{sign}{change:.2f}% 24h</div>
    <div class="cv-kpi-bar"><div class="cv-kpi-bar-fill{bar_class}" style="width:{bar_pct:.0f}%"></div></div>
</div>"""


def _fg_kpi(df_fg: pd.DataFrame) -> str:
    c = COLORS
    if df_fg.empty:
        return '<div class="cv-kpi-item"><div class="cv-kpi-label">fear &amp; greed</div><div class="cv-kpi-value">—</div></div>'

    latest = df_fg.iloc[-1]
    value = int(latest["fg_value"])
    label = latest["fg_label"]
    change = latest["value_change_vs_prev_day"]
    change = change if pd.notna(change) else 0

    color = FG_COLORS.get(label, c["text_muted"])
    sign = "+" if change and change >= 0 else ""
    change_str = f"{sign}{int(change)}" if pd.notna(change) else "—"

    return f"""
<div class="cv-kpi-item">
    <div class="cv-kpi-label">fear &amp; greed</div>
    <div class="cv-kpi-value" style="color:{color}">{value}</div>
    <span class="cv-badge" style="background:{color}18;color:{color};border:1px solid {color}33">{label}</span>
    <div class="cv-kpi-sub" style="margin-top:0.45rem">{change_str} vs yesterday</div>
    <div class="cv-kpi-bar"><div class="cv-kpi-bar-fill" style="width:{value}%;background:{color}"></div></div>
</div>"""


def _alignment_kpi(df_coin: pd.DataFrame) -> str:
    c = COLORS
    if df_coin.empty or "price_vs_sentiment_alignment" not in df_coin.columns:
        return '<div class="cv-kpi-item"><div class="cv-kpi-label">alignment</div><div class="cv-kpi-value">—</div></div>'

    counts = df_coin["price_vs_sentiment_alignment"].value_counts()
    total = len(df_coin)
    aligned = counts.get("aligned", 0)
    misaligned = counts.get("misaligned", 0)
    aligned_pct = aligned / total * 100 if total else 0
    misaligned_pct = misaligned / total * 100 if total else 0

    dominant = "aligned" if aligned >= misaligned else "misaligned"
    dom_color = c["aligned"] if dominant == "aligned" else c["misaligned"]
    dom_pct = aligned_pct if dominant == "aligned" else misaligned_pct

    return f"""
<div class="cv-kpi-item">
    <div class="cv-kpi-label">sentiment alignment</div>
    <div class="cv-kpi-value" style="color:{dom_color}">{dom_pct:.0f}%</div>
    <div class="cv-kpi-sub">price follows sentiment</div>
    <div class="cv-kpi-bar"><div class="cv-kpi-bar-fill" style="width:{aligned_pct:.0f}%;background:{c["aligned"]}"></div></div>
    <div class="cv-kpi-sub" style="margin-top:0.4rem">{aligned} aligned · {misaligned} misaligned</div>
</div>"""


def _volume_kpi(df_coin: pd.DataFrame) -> str:
    if df_coin.empty:
        return '<div class="cv-kpi-item"><div class="cv-kpi-label">volume</div><div class="cv-kpi-value">—</div></div>'

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

    return f"""
<div class="cv-kpi-item">
    <div class="cv-kpi-label">24h volume</div>
    <div class="cv-kpi-value">{vol_str}</div>
    <div class="cv-kpi-sub">{sign}{vol_vs_avg:.1f}% vs period avg</div>
    <div class="cv-kpi-bar"><div class="cv-kpi-bar-fill" style="width:{bar_pct:.0f}%"></div></div>
</div>"""


def render_kpi_cards(df_mart: pd.DataFrame, df_fg: pd.DataFrame, coin: str):
    df_coin = (
        df_mart[df_mart["coin_id"] == coin].copy()
        if not df_mart.empty
        else pd.DataFrame()
    )

    html = (
        '<div class="cv-kpi-row">'
        + _price_kpi(df_coin)
        + _fg_kpi(df_fg)
        + _alignment_kpi(df_coin)
        + _volume_kpi(df_coin)
        + "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
