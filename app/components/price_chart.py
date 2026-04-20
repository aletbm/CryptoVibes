import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import COLORS, FG_COLORS, COIN_LABELS

# CoinGecko small logos (PNG) — same dict as comparison_chart
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


def render_price_chart(df_mart: pd.DataFrame, coin: str):
    c = COLORS

    st.markdown(
        '<p class="cv-section-title">price vs fear &amp; greed</p>',
        unsafe_allow_html=True,
    )

    df = (
        df_mart[df_mart["coin_id"] == coin].copy()
        if not df_mart.empty
        else pd.DataFrame()
    )

    if df.empty:
        st.markdown(
            f'<p style="font-family:JetBrains Mono,monospace;font-size:0.7rem;color:{c["text_dim"]};padding:3rem 0">no data available</p>',
            unsafe_allow_html=True,
        )
        return

    df = df.sort_values("price_date")
    fg_colors_list = [FG_COLORS.get(label, c["text_muted"]) for label in df["fg_label"]]

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.65, 0.15, 0.35],
        vertical_spacing=0.03,
    )

    # Price line
    fig.add_trace(
        go.Scatter(
            x=df["price_date"],
            y=df["close_price_usd"],
            mode="lines",
            name="Price",
            line=dict(color=c["accent"], width=1.5),
            fill="tozeroy",
            fillcolor=c["accent_glow_sm"],
            hovertemplate="<b>%{x|%b %d}</b><br>$%{y:,.2f}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Invisible bar for hover (row 1)
    fig.add_trace(
        go.Bar(
            x=df["price_date"],
            y=df["avg_price_change_pct_24h"],
            name="24h Δ",
            marker=dict(
                color=[
                    c["accent"] if v >= 0 else c["fear"]
                    for v in df["avg_price_change_pct_24h"]
                ],
                opacity=0.0,
            ),
            hovertemplate="<b>%{x|%b %d}</b><br>%{y:.2f}%<extra></extra>",
        ),
        row=1,
        col=1,
    )

    min_price = df["close_price_usd"].min() * 0.95
    max_price = df["close_price_usd"].max() * 1.05
    fig.update_yaxes(range=[min_price, max_price], row=1, col=1)

    # Change bars
    fig.add_trace(
        go.Bar(
            x=df["price_date"],
            y=df["avg_price_change_pct_24h"],
            name="24h Δ",
            marker=dict(
                color=[
                    c["accent"] if v >= 0 else c["fear"]
                    for v in df["avg_price_change_pct_24h"]
                ],
                opacity=0.9,
            ),
            hovertemplate="<b>%{x|%b %d}</b><br>%{y:.2f}%<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.update_yaxes(range=[-8, 8], row=2, col=1)

    # F&G line
    fig.add_trace(
        go.Scatter(
            x=df["price_date"],
            y=df["fg_value"],
            mode="lines+markers",
            name="F&G",
            line=dict(color=c["text_dim"], width=1.2, dash="dot"),
            marker=dict(color=fg_colors_list, size=4, line=dict(width=0)),
            hovertemplate="<b>%{x|%b %d}</b><br>F&G %{y} — %{text}<extra></extra>",
            text=df["fg_label"],
        ),
        row=3,
        col=1,
    )

    fig.add_hrect(
        y0=0, y1=3, row=3, col=1, fillcolor=c["fear"], line_width=0, opacity=0.15
    )
    fig.add_hrect(
        y0=97, y1=100, row=3, col=1, fillcolor=c["accent"], line_width=0, opacity=0.15
    )

    # ── Logo at end of price line (row 1) ─────────────────────────────────────
    logo_url = COIN_LOGOS.get(coin)
    layout_images = []
    MS_PER_DAY = 86_400_000
    if logo_url and not df.empty:
        x_min = df["price_date"].min()
        x_max = df["price_date"].max()
        date_range_days = (
            (x_max - x_min).days if hasattr((x_max - x_min), "days") else 30
        )

        # Plotly date axes require sizex / x in milliseconds
        logo_size_ms = max(int(date_range_days * 0.048), 2) * MS_PER_DAY

        last_x = df["price_date"].iloc[-1]
        last_x_ms = int(pd.Timestamp(last_x).timestamp() * 1000)
        last_price = df["close_price_usd"].iloc[-1]
        price_span = max_price - min_price
        logo_size_price = price_span * 0.05  # 13% of visible price range

        layout_images.append(
            dict(
                source=logo_url,
                xref="x",
                yref="y",
                x=last_x_ms
                + logo_size_ms * 0.0,  # center the logo just past the last point
                y=last_price,
                sizex=logo_size_ms,
                sizey=logo_size_price,
                xanchor="center",
                yanchor="middle",
                layer="above",
                sizing="contain",
            )
        )

    fig.update_layout(
        images=layout_images,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", size=9, color=c["text_dim"]),
        showlegend=False,
        margin=dict(l=0, r=44, t=4, b=0),  # extra right margin for logo
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=c["surface"],
            bordercolor=c["border"],
            font=dict(family="JetBrains Mono", size=10, color=c["text"]),
        ),
        bargap=0.2,
    )

    axis_style = dict(
        gridcolor=c["border"],
        gridwidth=1,
        zeroline=False,
        tickfont=dict(family="JetBrains Mono", size=9, color=c["text_dim"]),
        showline=False,
    )

    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    fig.update_yaxes(range=[0, 100], row=3, col=1)
    fig.update_xaxes(matches="x", row=1, col=1)
    fig.update_xaxes(matches="x", row=2, col=1)
    fig.update_xaxes(matches="x", row=3, col=1)

    # Extend x range on all subplots to give room for the logo
    if logo_url and not df.empty:
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

    coin_label = COIN_LABELS.get(coin, coin)
    st.markdown(
        f'<p style="font-family:JetBrains Mono,monospace;font-size:0.54rem;color:{c["text_dim"]};margin-top:-0.25rem">'
        f"{coin_label} · price / 24h change / fear&greed index"
        f"</p>",
        unsafe_allow_html=True,
    )
