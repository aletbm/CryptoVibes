import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import COLORS, FG_COLORS, COIN_LABELS


def render_price_chart(df_mart: pd.DataFrame, coin: str):
    c = COLORS

    st.markdown(
        '<p class="cv-section-title">— Price vs Fear & Greed over time</p>',
        unsafe_allow_html=True,
    )

    df = (
        df_mart[df_mart["coin_id"] == coin].copy()
        if not df_mart.empty
        else pd.DataFrame()
    )

    if df.empty:
        st.markdown(
            f'<div class="cv-card" style="text-align:center;padding:3rem;color:{c["text_muted"]}">no data available for selected range</div>',
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
        vertical_spacing=0.04,
    )

    fig.add_trace(
        go.Scatter(
            x=df["price_date"],
            y=df["close_price_usd"],
            mode="lines",
            name="Price",
            line=dict(color=c["accent"], width=2),
            fill="tozeroy",
            fillcolor=c["accent_glow_sm"],
            hovertemplate="<b>%{x|%b %d}</b><br>Price: $%{y:,.2f}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=df["price_date"],
            y=df["avg_price_change_pct_24h"],
            name="24h Change %",
            marker=dict(
                color=[
                    c["accent"] if v >= 0 else c["fear"]
                    for v in df["avg_price_change_pct_24h"]
                ],
                opacity=0.0,
            ),
            hovertemplate="<b>%{x|%b %d}</b><br>Change: %{y:.2f}%<extra></extra>",
        ),
        row=1,
        col=1,
    )

    min_price = df["close_price_usd"].min() * 0.95
    max_price = df["close_price_usd"].max() * 1.05
    fig.update_yaxes(range=[min_price, max_price], row=1, col=1)

    fig.add_trace(
        go.Bar(
            x=df["price_date"],
            y=df["avg_price_change_pct_24h"],
            name="24h Change %",
            marker=dict(
                color=[
                    c["accent"] if v >= 0 else c["fear"]
                    for v in df["avg_price_change_pct_24h"]
                ],
                opacity=1,
            ),
            hovertemplate="<b>%{x|%b %d}</b><br>Change: %{y:.2f}%<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.update_yaxes(range=[-8, 8], row=2, col=1)

    fig.add_trace(
        go.Scatter(
            x=df["price_date"],
            y=df["fg_value"],
            mode="lines+markers",
            name="Fear & Greed",
            line=dict(color=c["text_muted"], width=1.5, dash="dot"),
            marker=dict(
                color=fg_colors_list,
                size=5,
                line=dict(width=0),
            ),
            hovertemplate="<b>%{x|%b %d}</b><br>F&G: %{y} — %{text}<extra></extra>",
            text=df["fg_label"],
        ),
        row=3,
        col=1,
    )

    fig.add_hrect(y0=0, y1=3, row=3, col=1, fillcolor=f"{c['fear']}", line_width=0)
    fig.add_hrect(y0=97, y1=100, row=3, col=1, fillcolor=f"{c['accent']}", line_width=0)

    fig.update_layout(
        height=410,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", size=10, color=c["text_muted"]),
        showlegend=False,
        margin=dict(l=0, r=0, t=8, b=0),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=c["surface"],
            bordercolor=c["border"],
            font=dict(family="JetBrains Mono", size=11, color=c["text"]),
        ),
        bargap=0.2,
    )

    axis_style = dict(
        gridcolor=c["border"],
        gridwidth=1,
        zeroline=False,
        tickfont=dict(family="JetBrains Mono", size=10, color=c["text_dim"]),
        showline=False,
    )

    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    fig.update_yaxes(title_text="", row=1, col=1)
    fig.update_yaxes(title_text="", range=[0, 100], row=3, col=1)

    fig.update_xaxes(matches="x", row=1, col=1)
    fig.update_xaxes(matches="x", row=2, col=1)
    fig.update_xaxes(matches="x", row=3, col=1)

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": True,
            "modeBarButtonsToKeep": ["zoom2d", "pan2d", "resetScale2d"],
            "scrollZoom": True,  # zoom con scroll del mouse
        },
    )
    coin_label = COIN_LABELS.get(coin, coin)
    st.markdown(
        f'<p style="font-family:JetBrains Mono,monospace;font-size:0.6rem;color:{c["text_dim"]};margin-top:-0.5rem">'
        f"top: {coin_label} price + 24h change bars · bottom: fear & greed index (0–100)"
        f"</p>",
        unsafe_allow_html=True,
    )
