from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.graph_objects as go

from src.data_loader import get_players_by_position, get_player_stats, get_position_stats, get_top_performances
from src.calculations import add_derived_stats, get_radar_data, get_kpi_data, POSITION_METRICS
from src.visualizations import build_radar_chart, build_scatter_plot, build_top_performances_table

POSITIONS = {
    "Outside Hitter":  2,
    "Opposite Hitter": 3,
    "Middle Blocker":  4,
    "Setter":          5,
    "Libero":          1,
}

LEAGUES = {
    "All Leagues": "all",
    "LOVB":        "lovb",
    "MLV":         "mlv",
    "AU":          "au",
}

POSITION_ICONS = {2: "🏐", 3: "🏐", 4: "🧱", 5: "🎯", 1: "🛡️"}

def kpi_card_html(label: str, value, league_avg, percentile: int) -> ui.Tag:
    pct_color = (
        "#3fb950" if percentile >= 66 else
        "#d29922" if percentile >= 33 else
        "#f85149"
    )
    bar_width = max(2, percentile)
    return ui.div(
        ui.div(label, style="color: #8b949e; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px;"),
        ui.div(str(value), style="color: #e6edf3; font-size: 26px; font-weight: 700; line-height: 1; margin-bottom: 6px;"),
        ui.div(
            ui.div(style=f"width: {bar_width}%; height: 3px; background: {pct_color}; border-radius: 2px; transition: width 0.4s ease;"),
            style="width: 100%; background: #30363d; border-radius: 2px; margin-bottom: 5px;"
        ),
        ui.div(
            ui.span(f"{percentile}th pct", style=f"color: {pct_color}; font-size: 10px; font-weight: 600;"),
            ui.span(f" · avg {league_avg}", style="color: #8b949e; font-size: 10px;"),
            style="display: flex; align-items: center;"
        ),
        style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 14px 16px; min-width: 120px;"
    )


app_ui = ui.page_navbar(

    ui.nav_panel("Player Scouting",
        ui.layout_sidebar(
            ui.sidebar(
                ui.div(
                    ui.h5("⚡ VOLLEYBALL", style="color: #4493f8; font-weight: 800; font-size: 13px; letter-spacing: 2px; margin: 0;"),
                    ui.h5("ANALYTICS HUB", style="color: #e6edf3; font-weight: 800; font-size: 13px; letter-spacing: 2px; margin: 0 0 16px 0;"),
                    style="border-bottom: 1px solid #30363d; padding-bottom: 16px; margin-bottom: 20px;"
                ),
                ui.p("LEAGUE", style="color: #8b949e; font-size: 10px; font-weight: 600; letter-spacing: 1px; margin-bottom: 6px;"),
                ui.input_select("league", None, choices=list(LEAGUES.keys()), selected="All Leagues"),
                ui.div(style="height: 14px;"),
                ui.p("POSITION", style="color: #8b949e; font-size: 10px; font-weight: 600; letter-spacing: 1px; margin-bottom: 6px;"),
                ui.input_select("position", None, choices=list(POSITIONS.keys()), selected="Outside Hitter"),
                ui.div(style="height: 14px;"),
                ui.p("PLAYER", style="color: #8b949e; font-size: 10px; font-weight: 600; letter-spacing: 1px; margin-bottom: 6px;"),
                ui.input_select("primary_player", None, choices=[]),
                ui.div(style="height: 24px;"),
                ui.output_ui("player_meta"),
                width=240,
                style="background-color: #0d1117; border-right: 1px solid #21262d; padding: 20px 16px;"
            ),

            ui.div(
                # Player header
                ui.output_ui("player_header"),
                ui.div(style="height: 16px;"),

                # KPI cards row
                ui.div(
                    ui.p("SEASON STATS", style="color: #8b949e; font-size: 10px; font-weight: 600; letter-spacing: 1px; margin-bottom: 10px;"),
                    ui.output_ui("kpi_cards"),
                ),
                ui.div(style="height: 16px;"),

                # Radar + scatter row
                ui.layout_columns(
                    ui.card(
                        output_widget("radar_chart"),
                        style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 0;"
                    ),
                    ui.card(
                        output_widget("scatter_plot"),
                        style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 0;"
                    ),
                    col_widths=[6, 6]
                ),
                ui.div(style="height: 16px;"),

                # Top performances
                ui.card(
                    output_widget("top_performances"),
                    style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 0;"
                ),

                style="padding: 20px; background-color: #0d1117; min-height: 100vh;"
            )
        )
    ),

    ui.nav_panel("Team Tendencies",
        ui.div(ui.h3("Coming Soon", style="color: #8b949e;"), style="padding: 40px;")
    ),

    ui.nav_panel("Match Center",
        ui.div(ui.h3("Coming Soon", style="color: #8b949e;"), style="padding: 40px;")
    ),

    title=ui.tags.span(
        ui.tags.b("VB", style="color: #4493f8;"),
        " Analytics",
        style="color: #e6edf3; font-size: 16px; font-weight: 600; letter-spacing: 0.5px;"
    ),
    navbar_options=ui.navbar_options(bg="#010409", inverse=True),
    id="navbar"
)


def server(input, output, session):

    @reactive.effect
    def _update_players():
        position_id = POSITIONS[input.position()]
        league = LEAGUES[input.league()]
        df = get_players_by_position(position_id, league)
        choices = {str(r.player_id): f"{r.player_name} — {r.team_code}" for _, r in df.iterrows()}
        ui.update_select("primary_player", choices=choices)

    @reactive.calc
    def players_df():
        position_id = POSITIONS[input.position()]
        league = LEAGUES[input.league()]
        return get_players_by_position(position_id, league)

    @reactive.calc
    def position_stats():
        position_id = POSITIONS[input.position()]
        league = LEAGUES[input.league()]
        df = get_position_stats(position_id, league)
        return add_derived_stats(df)

    @reactive.calc
    def player_stats():
        if not input.primary_player():
            return pd.DataFrame()
        player_id = int(input.primary_player())
        league = LEAGUES[input.league()]
        df = get_player_stats(player_id, league)
        return add_derived_stats(df)

    def selected_player_name() -> str:
        pid = input.primary_player()
        if not pid:
            return ""
        df = players_df()
        row = df[df["player_id"].astype(str) == pid]
        return row.iloc[0]["player_name"] if not row.empty else ""

    @output
    @render.ui
    def player_header():
        name = selected_player_name()
        if not name:
            return ui.div()
        pid = input.primary_player()
        df = players_df()
        row = df[df["player_id"].astype(str) == pid]
        if row.empty:
            return ui.div()
        r = row.iloc[0]
        icon = POSITION_ICONS.get(POSITIONS[input.position()], "🏐")
        return ui.div(
            ui.div(
                ui.h2(name, style="color: #e6edf3; font-size: 24px; font-weight: 700; margin: 0;"),
                ui.div(
                    ui.span(f"{icon} {input.position()}", style="color: #8b949e; font-size: 13px; margin-right: 12px;"),
                    ui.span(f"📍 {r.get('team_name', r.get('team_code', ''))}", style="color: #8b949e; font-size: 13px; margin-right: 12px;"),
                    ui.span(f"🏆 {r.get('league', '').upper()}", style="color: #4493f8; font-size: 13px; font-weight: 600;"),
                    style="margin-top: 4px;"
                ),
                style="flex: 1;"
            ),
            style="display: flex; align-items: center; background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px 20px;"
        )

    @output
    @render.ui
    def player_meta():
        name = selected_player_name()
        if not name:
            return ui.div(
                ui.p("Select a player to view their profile", style="color: #484f58; font-size: 12px; text-align: center;"),
            )
        p_stats = player_stats()
        if p_stats.empty:
            return ui.div()
        sets = int(p_stats.iloc[0].get("sets_played", 0))
        return ui.div(
            ui.div(
                ui.span("Sets Played", style="color: #8b949e; font-size: 11px; display: block;"),
                ui.span(str(sets), style="color: #e6edf3; font-size: 20px; font-weight: 700;"),
                style="text-align: center; background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 10px;"
            )
        )

    @output
    @render.ui
    def kpi_cards():
        p_stats = player_stats()
        pos_stats = position_stats()
        if p_stats.empty or pos_stats.empty:
            return ui.div(ui.p("No data available", style="color: #484f58; font-size: 13px;"))
        position_id = POSITIONS[input.position()]
        kpis = get_kpi_data(p_stats, pos_stats, position_id)
        if not kpis:
            return ui.div()
        cards = [kpi_card_html(k["label"], k["value"], k["league_avg"], k["percentile"]) for k in kpis]
        return ui.div(
            *cards,
            style="display: flex; flex-wrap: wrap; gap: 10px;"
        )

    @output
    @render_widget
    def radar_chart():
        p_stats = player_stats()
        pos_stats = position_stats()
        if p_stats.empty or pos_stats.empty:
            return go.Figure().update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22", height=380)
        position_id = POSITIONS[input.position()]
        radar = get_radar_data(p_stats, pos_stats, position_id)
        return build_radar_chart(radar, selected_player_name())

    @output
    @render_widget
    def scatter_plot():
        pos_stats = position_stats()
        if pos_stats.empty:
            return go.Figure().update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22", height=380)
        return build_scatter_plot(pos_stats, selected_player_name(), POSITIONS[input.position()])

    @output
    @render_widget
    def top_performances():
        pid = input.primary_player()
        if not pid:
            return go.Figure().update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22", height=220)
        league = LEAGUES[input.league()]
        df = get_top_performances(int(pid), league)
        from src.visualizations import build_top_performances_table
        return build_top_performances_table(df)


app = App(app_ui, server)