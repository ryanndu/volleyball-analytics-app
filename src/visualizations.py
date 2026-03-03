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


def build_scatter_plot(position_stats: pd.DataFrame, player_name: str, position: int) -> go.Figure:
    from src.calculations import POSITION_METRICS

    df = position_stats.copy()

    if position == 1:
        x_col, y_col     = "digs_per_set", "pass_rating"
        x_label, y_label = "Digs/Set", "Pass Rating"
    elif position == 5:
        x_col, y_col     = "assists_per_set", "serve_efficiency"
        x_label, y_label = "Assists/Set", "Serve Efficiency"
    elif position == 4:
        x_col, y_col     = "blocks_per_set", "attack_efficiency"
        x_label, y_label = "Blocks/Set", "Hit %"
    else:
        x_col, y_col     = "kills_per_set", "attack_efficiency"
        x_label, y_label = "Kills/Set", "Hit %"

    df[x_col] = pd.to_numeric(df[x_col], errors="coerce")
    df[y_col] = pd.to_numeric(df[y_col], errors="coerce")
    df = df.dropna(subset=[x_col, y_col])

    others = df[df["player_name"] != player_name]
    player = df[df["player_name"] == player_name]

    x_mean = df[x_col].mean()
    y_mean = df[y_col].mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=others[x_col].tolist(),
        y=others[y_col].tolist(),
        mode="markers",
        name="Others",
        marker=dict(color="#30363d", size=8, opacity=0.8, line=dict(color="#8b949e", width=1)),
        text=others["player_name"].tolist(),
        hovertemplate="<b>%{text}</b><br>" + x_label + ": %{x}<br>" + y_label + ": %{y}<extra></extra>"
    ))

    if not player.empty:
        fig.add_trace(go.Scatter(
            x=player[x_col].tolist(),
            y=player[y_col].tolist(),
            mode="markers+text",
            name=player_name,
            marker=dict(color="#00C9FF", size=14, line=dict(color="white", width=2)),
            text=[player_name.split()[-1]],
            textposition="top center",
            textfont=dict(color="white", size=11),
            hovertemplate="<b>%{text}</b><br>" + x_label + ": %{x}<br>" + y_label + ": %{y}<extra></extra>"
        ))

    fig.add_vline(x=x_mean, line=dict(color="#8b949e", dash="dot", width=1))
    fig.add_hline(y=y_mean, line=dict(color="#8b949e", dash="dot", width=1))

    fig.update_layout(
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        height=380,
        showlegend=False,
        margin=dict(l=50, r=60, t=50, b=50),
        title=dict(
            text="POSITIONAL COMPARISON",
            font=dict(color="#8b949e", size=11, ),
            x=0.01
        ),
        xaxis=dict(
            title=dict(text=x_label, font=dict(color="#8b949e", size=11)),
            color="#8b949e",
            gridcolor="#21262d",
            zerolinecolor="#21262d",
            tickfont=dict(color="#8b949e", size=10),
            automargin=True,
        ),
        yaxis=dict(
            title=dict(text=y_label, font=dict(color="#8b949e", size=11)),
            color="#8b949e",
            gridcolor="#21262d",
            zerolinecolor="#21262d",
            tickfont=dict(color="#8b949e", size=10),
        ),
    )
    fig._config = {"staticPlot": True, "displayModeBar": False}
    return fig


def build_top_performances_table(df: pd.DataFrame, position: int) -> go.Figure:
    from src.calculations import POSITION_METRICS
    fig = go.Figure()

    if df.empty:
        fig.update_layout(paper_bgcolor="#0d1117", height=200)
        return fig

    config = POSITION_METRICS[position]["top_performances"]
    col_keys   = config["cols"]
    col_labels = config["labels"]
    col_widths = config["widths"]

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%b %d, %Y")
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    cell_values = [df[k].tolist() if k in df.columns else ["—"] * len(df) for k in col_keys]

    fig.add_trace(go.Table(
        columnwidth=col_widths,
        header=dict(
            values=[f"<b>{l}</b>" for l in col_labels],
            fill_color="#1c2128",
            font=dict(color="#8b949e", size=11),
            align=["left"] + ["center"] * (len(col_labels) - 1),
            line_color="#30363d",
            height=32,
        ),
        cells=dict(
            values=cell_values,
            fill_color=["#0d1117"],
            font=dict(color="#e6edf3", size=11),
            align=["left"] + ["center"] * (len(col_labels) - 1),
            line_color="#21262d",
            height=30,
        )
    ))

    fig.update_layout(
        paper_bgcolor="#0d1117",
        height=260,
        margin=dict(l=0, r=0, t=40, b=0),
        title=dict(text="TOP PERFORMANCES", font=dict(color="#8b949e", size=11), x=0.01, y=0.97)
    )
    fig._config = {"staticPlot": True, "displayModeBar": False}
    return fig