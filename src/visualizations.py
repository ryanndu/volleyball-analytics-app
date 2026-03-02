import plotly.graph_objects as go
import pandas as pd
import numpy as np


def build_radar_chart(radar_data: dict, player_name: str) -> go.Figure:
    labels = radar_data["labels"] + [radar_data["labels"][0]]
    player_percentiles = radar_data["player_radar_percentiles"] + [radar_data["player_radar_percentiles"][0]]
    league_percentiles = radar_data["league_avg_percentiles"] + [radar_data["league_avg_percentiles"][0]]
    player_raw = radar_data["player_raw_stats"] + [radar_data["player_raw_stats"][0]]
    league_raw = radar_data["league_avg_stats"] + [radar_data["league_avg_stats"][0]]

    player_hover = [
        f"{labels[i]}<br>Percentile: {round(player_percentiles[i] * 100)}th<br>Value: {player_raw[i]}"
        for i in range(len(labels))
    ]

    league_hover = [
        f"{labels[i]}<br>League Avg: {league_raw[i]}"
        for i in range(len(labels))
    ]

    PLAYER_COLOR = "#00C9FF"

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=player_percentiles,
        theta=labels,
        fill="toself",
        fillcolor="rgba(0, 201, 255, 0.15)",
        line=dict(color=PLAYER_COLOR, width=2),
        name=player_name,
        text=player_hover,
        hoverinfo="text",
    ))

    fig.add_trace(go.Scatterpolar(
        r=league_percentiles,
        theta=labels,
        fill=None,
        line=dict(color="rgba(255,255,255,0.35)", width=1.5, dash="dash"),
        name="League Avg",
        text=league_hover,
        hoverinfo="text",
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickvals=[0.25, 0.5, 0.75, 1.0],
                ticktext=["25th", "50th", "75th", "100th"],
                tickfont=dict(size=9, color="rgba(255,255,255,0.4)"),
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.1)",
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="white"),
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.1)",
            ),
        ),
        showlegend=True,
        legend=dict(
            font=dict(color="white", size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=40, l=60, r=60),
        title=dict(
            text=f"{player_name} — Percentile Radar",
            font=dict(color="white", size=14),
            x=0.5,
        )
    )

    return fig