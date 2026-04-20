import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import COLORS, COIN_LABELS

# Paleta de colores para cada coin en el comparison chart
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
        '<p class="cv-section-title">— Cumulative return comparison</p>',
        unsafe_allow_html=True,
    )

    fig = go.Figure()

    for coin_id in all_coins:
        df_coin = df[df["coin_id"] == coin_id].sort_values("price_date").copy()
        df_coin = df_coin.dropna(subset=["close_price_usd"])

        if df_coin.empty or len(df_coin) < 2:
            continue

        # Retorno acumulado desde el primer dia del rango
        base_price = df_coin["close_price_usd"].iloc[0]
        df_coin["cumulative_return"] = (
            df_coin["close_price_usd"] / base_price - 1
        ) * 100

        label = COIN_LABELS.get(coin_id, coin_id)
        color = COIN_COLORS.get(coin_id, c["text_muted"])
        is_primary = coin_id == primary_coin

        fig.add_trace(
            go.Scatter(
                x=df_coin["price_date"],
                y=df_coin["cumulative_return"],
                mode="lines",
                name=label,
                line=dict(
                    color=color,
                    width=2.5 if is_primary else 1.5,
                    dash="solid" if is_primary else "dot",
                ),
                hovertemplate=f"<b>{label}</b><br>%{{x|%b %d, %Y}}<br>Return: %{{y:+.2f}}%<extra></extra>",
            )
        )

    fig.add_hline(
        y=0,
        line_color=c["border"],
        line_width=1,
        line_dash="solid",
    )

    fig.add_hrect(
        y0=0,
        y1=fig.data[0].y.max() * 1.1 if fig.data else 100,
        fillcolor="rgba(57,255,20,0.03)",
        line_width=0,
    )
    fig.add_hrect(
        y0=fig.data[0].y.min() * 1.1 if fig.data else -100,
        y1=0,
        fillcolor="rgba(255,68,68,0.03)",
        line_width=0,
    )

    fig.update_layout(
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", size=10, color=c["text_muted"]),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(family="JetBrains Mono", size=9, color=c["text_muted"]),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=c["surface"],
            bordercolor=c["border"],
            font=dict(family="JetBrains Mono", size=11, color=c["text"]),
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
    fig.update_yaxes(
        **axis_style,
        ticksuffix="%",
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": True,
            "modeBarButtonsToKeep": ["zoom2d", "pan2d", "resetScale2d"],
            "scrollZoom": True,
        },
    )

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
<div style="
    background: {c["surface"]};
    border: 1px solid {color}44;
    border-top: 2px solid {color};
    border-radius: 8px;
    padding: 0.75rem 1rem;
    text-align: center;
">
    <p style="font-family:JetBrains Mono,monospace;font-size:0.6rem;color:{color};margin:0;letter-spacing:0.1em">{row["coin"]}</p>
    <p style="font-family:Quantico,sans-serif;font-weight:400;font-size:1.2rem;color:{ret_color};margin:0.25rem 0 0">{row["return"]}</p>
    <p style="font-family:JetBrains Mono,monospace;font-size:0.55rem;color:{c["text_dim"]};margin:0.2rem 0 0">{row["start"]} → {row["end"]}</p>
</div>
""",
                    unsafe_allow_html=True,
                )
