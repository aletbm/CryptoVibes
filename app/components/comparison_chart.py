import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import COLORS, COIN_LABELS

COIN_COLORS = {
    "bitcoin": "#F7931A",
    "ethereum": "#979797",
    "binancecoin": "#F3BA2F",
    "solana": "#14F195",
    "ripple": "#00AAE4",
    "dogecoin": "#C2A633",
    "cardano": "#0033AD",
    "avalanche-2": "#E84142",
    "shiba-inu": "#FF69B4",
    "polkadot": "#E6007A",
}

# CoinGecko small logos (PNG) — served via CDN
COIN_LOGOS = {
    "bitcoin": "https://assets.coingecko.com/coins/images/1/small/bitcoin.png",
    "ethereum": "https://assets.coingecko.com/coins/images/279/small/ethereum.png",
    "binancecoin": "https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png",
    "solana": "https://assets.coingecko.com/coins/images/4128/small/solana.png",
    "ripple": "https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png",
    "dogecoin": "https://assets.coingecko.com/coins/images/5/small/dogecoin.png",
    "cardano": "https://assets.coingecko.com/coins/images/975/small/cardano.png",
    "avalanche-2": "https://assets.coingecko.com/coins/images/12559/small/Avalanche_Circle_RedWhite_Trans.png",
    "shiba-inu": "https://assets.coingecko.com/coins/images/11939/small/shiba.png",
    "polkadot": "https://assets.coingecko.com/coins/images/12171/small/polkadot.png",
}


def render_comparison_chart(
    df_mart: pd.DataFrame, primary_coin: str, compare_coins: list
):
    c = COLORS

    if not compare_coins:
        return

    all_coins = [primary_coin] + compare_coins
    df = df_mart[df_mart["coin_id"].isin(all_coins)].copy()

    if df.empty:
        return

    st.markdown(
        '<p class="cv-section-title">cumulative return comparison</p>',
        unsafe_allow_html=True,
    )

    fig = go.Figure()

    # Collect last (x, y) per coin for logo placement
    logo_anchors = []

    for coin_id in all_coins:
        df_coin = df[df["coin_id"] == coin_id].sort_values("price_date").copy()
        df_coin = df_coin.dropna(subset=["close_price_usd"])

        if df_coin.empty or len(df_coin) < 2:
            continue

        base_price = df_coin["close_price_usd"].iloc[0]
        df_coin["cumulative_return"] = (
            df_coin["close_price_usd"] / base_price - 1
        ) * 100

        label = COIN_LABELS.get(coin_id, coin_id)
        color = COIN_COLORS.get(coin_id, c["text_muted"])
        is_primary = coin_id == primary_coin

        last_x = df_coin["price_date"].iloc[-1]
        last_y = df_coin["cumulative_return"].iloc[-1]
        logo_anchors.append((coin_id, last_x, last_y))

        fig.add_trace(
            go.Scatter(
                x=df_coin["price_date"],
                y=df_coin["cumulative_return"],
                mode="lines",
                name=label,
                line=dict(
                    color=color,
                    width=2 if is_primary else 1.2,
                    dash="solid" if is_primary else "dot",
                ),
                hovertemplate=f"<b>{label}</b><br>%{{x|%b %d, %Y}}<br>%{{y:+.2f}}%<extra></extra>",
            )
        )

    fig.add_hline(y=0, line_color=c["border"], line_width=1)

    # ── Logo images at end of each line ──────────────────────────────────────
    all_dates = df["price_date"].dropna()
    x_min = all_dates.min()
    x_max = all_dates.max()
    date_range_days = (x_max - x_min).days if hasattr((x_max - x_min), "days") else 30

    # Plotly date axes use milliseconds internally for sizex / x in layout.images
    MS_PER_DAY = 86_400_000
    logo_size_ms = max(int(date_range_days * 0.048), 2) * MS_PER_DAY

    # y-axis span estimate
    all_returns = []
    for coin_id in all_coins:
        dc = df[df["coin_id"] == coin_id].dropna(subset=["close_price_usd"])
        if len(dc) < 2:
            continue
        base = dc["close_price_usd"].iloc[0]
        all_returns += list((dc["close_price_usd"] / base - 1) * 100)

    y_span = (max(all_returns) - min(all_returns)) if all_returns else 100
    logo_size_y = y_span * 0.02  # 10% of visible y range

    layout_images = []
    for coin_id, last_x, last_y in logo_anchors:
        logo_url = COIN_LOGOS.get(coin_id)
        if not logo_url:
            continue
        # Convert timestamp to ms for Plotly
        last_x_ms = int(pd.Timestamp(last_x).timestamp() * 1000)
        layout_images.append(
            dict(
                source=logo_url,
                xref="x",
                yref="y",
                x=last_x_ms
                + logo_size_ms * 0.0,  # center the logo just past the last point
                y=last_y,
                sizex=logo_size_ms,
                sizey=logo_size_y,
                xanchor="center",
                yanchor="middle",
                layer="above",
                sizing="contain",
            )
        )

    fig.update_layout(
        images=layout_images,
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", size=9, color=c["text_dim"]),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(family="JetBrains Mono", size=8, color=c["text_muted"]),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
        margin=dict(l=0, r=44, t=28, b=0),  # extra right margin so logos aren't clipped
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=c["surface"],
            bordercolor=c["border"],
            font=dict(family="JetBrains Mono", size=10, color=c["text"]),
        ),
    )

    axis_style = dict(
        gridcolor=c["border"],
        gridwidth=1,
        zeroline=False,
        tickfont=dict(family="JetBrains Mono", size=9, color=c["text_dim"]),
        showline=False,
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style, ticksuffix="%")

    # Extend x-axis range to give room for logos (use ms timestamps)
    x_min_ms = int(pd.Timestamp(x_min).timestamp() * 1000)
    x_max_ms = int(pd.Timestamp(x_max).timestamp() * 1000)
    fig.update_xaxes(range=[x_min_ms, x_max_ms + logo_size_ms * 2.2])

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": True,
            "modeBarButtonsToKeep": ["zoom2d", "pan2d", "resetScale2d"],
            "scrollZoom": True,
        },
    )

    # Summary row — inline stats, no cards
    rows = []
    for coin_id in all_coins:
        df_coin = (
            df[df["coin_id"] == coin_id]
            .sort_values("price_date")
            .dropna(subset=["close_price_usd"])
        )
        if len(df_coin) < 2:
            continue
        base = df_coin["close_price_usd"].iloc[0]
        last = df_coin["close_price_usd"].iloc[-1]
        ret = (last / base - 1) * 100
        sign = "+" if ret >= 0 else ""
        color = COIN_COLORS.get(coin_id, c["text_muted"])
        rows.append(
            {
                "coin": COIN_LABELS.get(coin_id, coin_id),
                "start": f"${base:,.4f}" if base < 1 else f"${base:,.2f}",
                "end": f"${last:,.4f}" if last < 1 else f"${last:,.2f}",
                "return": f"{sign}{ret:.2f}%",
                "color": color,
                "ret_val": ret,
            }
        )

    if rows:
        cols = st.columns(len(rows))
        for i, row in enumerate(rows):
            color = row["color"]
            ret_color = COLORS["accent"] if row["ret_val"] >= 0 else COLORS["fear"]
            with cols[i]:
                st.markdown(
                    f"""
<div style="padding:0.6rem 0;border-top:2px solid {color};margin-top:0.75rem">
    <div style="font-family:JetBrains Mono,monospace;font-size:0.54rem;color:{color};letter-spacing:0.1em;margin-bottom:0.3rem">{row["coin"]}</div>
    <div style="font-family:'Quantico',sans-serif;font-size:1.3rem;color:{ret_color};margin-bottom:0.2rem">{row["return"]}</div>
    <div style="font-family:JetBrains Mono,monospace;font-size:0.52rem;color:{c["text_dim"]}">{row["start"]} → {row["end"]}</div>
</div>""",
                    unsafe_allow_html=True,
                )
