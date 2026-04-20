import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import COLORS, FG_COLORS


FG_ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]


def render_sentiment_distribution(df_fg: pd.DataFrame):
    c = COLORS

    st.markdown(
        '<p class="cv-section-title">— Sentiment distribution</p>',
        unsafe_allow_html=True,
    )

    if df_fg.empty:
        st.markdown(
            f'<div class="cv-card" style="text-align:center;padding:3rem;color:{c["text_muted"]}">no data</div>',
            unsafe_allow_html=True,
        )
        return

    counts = df_fg["fg_label"].value_counts().reindex(FG_ORDER, fill_value=0)
    total = counts.sum()
    pcts = (counts / total * 100).round(1)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=pcts.values,
            y=pcts.index,
            orientation="h",
            marker=dict(
                color=[FG_COLORS[label] for label in pcts.index],
                opacity=0.85,
            ),
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
            text=[f"{v:.0f}%" for v in pcts.values],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=9, color=c["text_muted"]),
        )
    )

    fig.update_layout(
        height=200,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", size=9, color=c["text_muted"]),
        showlegend=False,
        margin=dict(l=0, r=40, t=4, b=0),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0, pcts.max() * 1.25],
        ),
        yaxis=dict(
            gridcolor=c["border"],
            tickfont=dict(family="JetBrains Mono", size=9, color=c["text_muted"]),
            showline=False,
        ),
        bargap=0.3,
    )

    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    dominant = counts.idxmax()
    dom_color = FG_COLORS.get(dominant, c["text_muted"])
    dom_pct = pcts[dominant]

    st.markdown(
        f"""
<div class="cv-card" style="margin-top:0.5rem">
    <p class="cv-card-label">DOMINANT MOOD</p>
    <p class="cv-card-value" style="font-size:1.4rem;color:{dom_color}">{dominant}</p>
    <p class="cv-card-sub">{dom_pct:.1f}% of days · {counts[dominant]} total</p>
    <div class="cv-bar-track">
        <div class="cv-bar-fill" style="width:{dom_pct:.0f}%;background:{dom_color};box-shadow:0 0 6px {dom_color};"></div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p style="font-family:JetBrains Mono,monospace;font-size:0.6rem;color:{c["text_dim"]};margin-top:0.5rem">'
        f"{total} days analyzed"
        f"</p>",
        unsafe_allow_html=True,
    )
