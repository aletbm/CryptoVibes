import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import COLORS, FG_COLORS

FG_ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]


def render_sentiment_distribution(df_fg: pd.DataFrame):
    c = COLORS

    st.markdown(
        '<p class="cv-section-title">sentiment distribution</p>',
        unsafe_allow_html=True,
    )

    if df_fg.empty:
        st.markdown(
            f'<p style="font-family:JetBrains Mono,monospace;font-size:0.7rem;color:{c["text_dim"]}">no data</p>',
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
            marker=dict(color=[FG_COLORS[label] for label in pcts.index], opacity=0.75),
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
            text=[f"{v:.0f}%" for v in pcts.values],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=8, color=c["text_dim"]),
        )
    )

    fig.update_layout(
        height=185,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", size=8, color=c["text_dim"]),
        showlegend=False,
        margin=dict(l=0, r=36, t=0, b=0),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0, pcts.max() * 1.3],
        ),
        yaxis=dict(
            gridcolor=c["border"],
            tickfont=dict(family="JetBrains Mono", size=8, color=c["text_dim"]),
            showline=False,
        ),
        bargap=0.35,
    )

    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    # Dominant mood — inline, no card
    dominant = counts.idxmax()
    dom_color = FG_COLORS.get(dominant, c["text_muted"])
    dom_pct = pcts[dominant]

    st.markdown(
        f"""
<div style="margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid {c["border"]}">
    <div class="cv-kpi-label">dominant mood</div>
    <div style="font-family:'Quantico',sans-serif;font-size:1.2rem;color:{dom_color};margin:0.3rem 0 0.2rem">{dominant}</div>
    <div class="cv-kpi-sub">{dom_pct:.1f}% · {counts[dominant]} days</div>
    <div class="cv-kpi-bar" style="margin-top:0.6rem"><div class="cv-kpi-bar-fill" style="width:{dom_pct:.0f}%;background:{dom_color}"></div></div>
</div>
<p style="font-family:JetBrains Mono,monospace;font-size:0.52rem;color:{c["text_dim"]};margin-top:0.6rem">{total} days analyzed</p>
""",
        unsafe_allow_html=True,
    )
