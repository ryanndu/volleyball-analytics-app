import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Color palette ──────────────────────────────────────────────────────────
BG_BASE = "rgba(0,0,0,0)"
BG_SURFACE = "#12161e"
GRID_COLOR = "rgba(255,255,255,0.06)"
BORDER_COLOR = "rgba(255,255,255,0.08)"
TEXT_PRIMARY = "#eaf0f6"
TEXT_SECONDARY = "#6b7b8d"
ACCENT = "#5ce0d8"
ACCENT_DIM = "rgba(92, 224, 216, 0.12)"


def build_radar_chart(radar_data: dict, player_name: str) -> go.Figure:
    labels = radar_data["labels"] + [radar_data["labels"][0]]
    player_pct = radar_data["player_radar_percentiles"] + [radar_data["player_radar_percentiles"][0]]
    league_pct = radar_data["league_avg_percentiles"] + [radar_data["league_avg_percentiles"][0]]
    player_raw = radar_data["player_raw_stats"] + [radar_data["player_raw_stats"][0]]
    league_raw = radar_data["league_avg_stats"] + [radar_data["league_avg_stats"][0]]

    player_hover = [
        f"{labels[i]}<br>Percentile: {round(player_pct[i] * 100)}th<br>Value: {player_raw[i]}"
        for i in range(len(labels))
    ]
    league_hover = [
        f"{labels[i]}<br>League Avg: {league_raw[i]}"
        for i in range(len(labels))
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=player_pct,
        theta=labels,
        fill="toself",
        fillcolor=ACCENT_DIM,
        line=dict(color=ACCENT, width=2.5),
        name=player_name.split()[-1],
        text=player_hover,
        hoverinfo="text",
    ))

    fig.add_trace(go.Scatterpolar(
        r=league_pct,
        theta=labels,
        fill=None,
        line=dict(color="rgba(255,255,255,0.2)", width=1.5, dash="dot"),
        name="League Avg",
        text=league_hover,
        hoverinfo="text",
    ))

    fig.update_layout(
        polar=dict(
            bgcolor=BG_BASE,
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickvals=[0.25, 0.5, 0.75, 1.0],
                ticktext=["25", "50", "75", "100"],
                tickfont=dict(size=8, color="rgba(255,255,255,0.25)"),
                gridcolor=GRID_COLOR,
                linecolor=GRID_COLOR,
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=TEXT_SECONDARY, family="DM Sans, sans-serif"),
                gridcolor=GRID_COLOR,
                linecolor=GRID_COLOR,
            ),
        ),
        showlegend=True,
        legend=dict(
            font=dict(color=TEXT_SECONDARY, size=10, family="DM Sans, sans-serif"),
            bgcolor=BG_BASE,
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
        ),
        paper_bgcolor=BG_BASE,
        plot_bgcolor=BG_BASE,
        height=380,
        margin=dict(t=50, b=50, l=60, r=60),
        title=dict(
            text="PERCENTILE RADAR",
            font=dict(color=TEXT_SECONDARY, size=10, family="DM Sans, sans-serif"),
            x=0.02,
            y=0.98,
        ),
    )
    return fig


def build_scatter_plot(position_stats: pd.DataFrame, player_name: str, position: int) -> go.Figure:
    from src.calculations import POSITION_METRICS

    df = position_stats.copy()

    if position == 1:
        x_col, y_col = "digs_per_set", "pass_rating"
        x_label, y_label = "Digs / Set", "Pass Rating"
    elif position == 5:
        x_col, y_col = "assists_per_set", "serve_efficiency"
        x_label, y_label = "Assists / Set", "Serve Efficiency"
    elif position == 4:
        x_col, y_col = "blocks_per_set", "attack_efficiency"
        x_label, y_label = "Blocks / Set", "Hit %"
    else:
        x_col, y_col = "kills_per_set", "attack_efficiency"
        x_label, y_label = "Kills / Set", "Hit %"

    df[x_col] = pd.to_numeric(df[x_col], errors="coerce")
    df[y_col] = pd.to_numeric(df[y_col], errors="coerce")
    df = df.dropna(subset=[x_col, y_col])

    others = df[df["player_name"] != player_name]
    player = df[df["player_name"] == player_name]

    x_mean = df[x_col].mean()
    y_mean = df[y_col].mean()

    fig = go.Figure()

    # Other players – subtle dots
    fig.add_trace(go.Scatter(
        x=others[x_col].tolist(),
        y=others[y_col].tolist(),
        mode="markers",
        name="Others",
        marker=dict(
            color="rgba(107,123,141,0.35)",
            size=7,
            line=dict(color="rgba(107,123,141,0.5)", width=0.5),
        ),
        text=others["player_name"].tolist(),
        hovertemplate="<b>%{text}</b><br>" + x_label + ": %{x}<br>" + y_label + ": %{y}<extra></extra>",
    ))

    # Selected player – accent glow
    if not player.empty:
        fig.add_trace(go.Scatter(
            x=player[x_col].tolist(),
            y=player[y_col].tolist(),
            mode="markers+text",
            name=player_name,
            marker=dict(
                color=ACCENT,
                size=13,
                line=dict(color="white", width=2),
                symbol="diamond",
            ),
            text=[player_name.split()[-1]],
            textposition="top center",
            textfont=dict(color=TEXT_PRIMARY, size=11, family="DM Sans, sans-serif"),
            hovertemplate="<b>%{text}</b><br>" + x_label + ": %{x}<br>" + y_label + ": %{y}<extra></extra>",
        ))

    fig.add_vline(x=x_mean, line=dict(color="rgba(255,255,255,0.08)", dash="dot", width=1))
    fig.add_hline(y=y_mean, line=dict(color="rgba(255,255,255,0.08)", dash="dot", width=1))

    fig.update_layout(
        paper_bgcolor=BG_BASE,
        plot_bgcolor=BG_BASE,
        height=380,
        showlegend=False,
        margin=dict(l=50, r=30, t=50, b=50),
        title=dict(
            text="POSITIONAL COMPARISON",
            font=dict(color=TEXT_SECONDARY, size=10, family="DM Sans, sans-serif"),
            x=0.02,
            y=0.98,
        ),
        xaxis=dict(
            title=dict(text=x_label, font=dict(color=TEXT_SECONDARY, size=11, family="DM Sans, sans-serif")),
            color=TEXT_SECONDARY,
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_SECONDARY, size=10, family="DM Mono, monospace"),
            automargin=True,
        ),
        yaxis=dict(
            title=dict(text=y_label, font=dict(color=TEXT_SECONDARY, size=11, family="DM Sans, sans-serif")),
            color=TEXT_SECONDARY,
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_SECONDARY, size=10, family="DM Mono, monospace"),
        ),
    )
    fig._config = {"staticPlot": True, "displayModeBar": False}
    return fig


def build_top_performances_table(df: pd.DataFrame, position: int) -> go.Figure:
    from src.calculations import POSITION_METRICS

    fig = go.Figure()
    if df.empty:
        fig.update_layout(paper_bgcolor=BG_BASE, height=200)
        return fig

    config = POSITION_METRICS[position]["top_performances"]
    col_keys = config["cols"]
    col_labels = config["labels"]
    col_widths = config["widths"]

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%b %d, %Y")
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    cell_values = [df[k].tolist() if k in df.columns else ["—"] * len(df) for k in col_keys]

    # Alternating row fills for readability
    n_rows = len(df)
    row_fills = [["#12161e" if i % 2 == 0 else "#161c26" for i in range(n_rows)] for _ in col_keys]

    fig.add_trace(go.Table(
        columnwidth=col_widths,
        header=dict(
            values=[f"<b>{l}</b>" for l in col_labels],
            fill_color="#1a2030",
            font=dict(color=TEXT_SECONDARY, size=10, family="DM Sans, sans-serif"),
            align=["left"] + ["center"] * (len(col_labels) - 1),
            line_color="rgba(255,255,255,0.06)",
            height=34,
        ),
        cells=dict(
            values=cell_values,
            fill_color=row_fills,
            font=dict(color=TEXT_PRIMARY, size=11, family="DM Mono, monospace"),
            align=["left"] + ["center"] * (len(col_labels) - 1),
            line_color="rgba(255,255,255,0.04)",
            height=32,
        ),
    ))

    fig.update_layout(
        paper_bgcolor=BG_BASE,
        height=260,
        margin=dict(l=0, r=0, t=40, b=0),
        title=dict(
            text="TOP PERFORMANCES",
            font=dict(color=TEXT_SECONDARY, size=10, family="DM Sans, sans-serif"),
            x=0.01,
            y=0.97,
        ),
    )
    fig._config = {"staticPlot": True, "displayModeBar": False}
    return fig