from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.graph_objects as go

from src.data_loader import (
    get_players_by_position,
    get_player_stats,
    get_position_stats,
    get_top_performances,
)
from src.calculations import add_derived_stats, get_radar_data, get_kpi_data, POSITION_METRICS
from src.visualizations import (
    build_radar_chart,
    build_scatter_plot,
    build_top_performances_table,
)

# ── Constants ──────────────────────────────────────────────────────────────
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

POSITION_TAGS = {
    2: ("OH", "#5ce0d8"),
    3: ("OPP", "#e0a85c"),
    4: ("MB", "#a87be0"),
    5: ("SET", "#e07b7b"),
    1: ("LIB", "#7be07b"),
}

# ── Stylesheet ─────────────────────────────────────────────────────────────
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset ── */
* { font-family: 'DM Sans', sans-serif !important; box-sizing: border-box; }
html, body { background: #0b0f15 !important; margin: 0; padding: 0; color: #eaf0f6; }

/* ── Layout containers ── */
.bslib-sidebar-layout,
.bslib-sidebar-layout > .main,
.bslib-page-fill,
.shiny-bound-ui,
.tab-content,
.tab-pane { background: #0b0f15 !important; }

.card {
    box-shadow: none !important;
    border: none !important;
    background: transparent !important;
}

/* ── Sidebar ── */
.bslib-sidebar-layout > .sidebar {
    background: linear-gradient(180deg, #0e1219 0%, #0b0f15 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}

/* ── Select inputs ── */
.selectize-control .selectize-input {
    background: #141a24 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #eaf0f6 !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    font-size: 13px !important;
    padding: 9px 12px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.selectize-control .selectize-input.focus {
    border-color: #5ce0d8 !important;
    box-shadow: 0 0 0 3px rgba(92,224,216,0.08) !important;
}
.selectize-dropdown {
    background: #141a24 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #eaf0f6 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important;
}
.selectize-dropdown .option:hover,
.selectize-dropdown .option.active {
    background: rgba(92,224,216,0.08) !important;
    color: #eaf0f6 !important;
}
.selectize-dropdown .option {
    padding: 8px 12px !important;
}

/* ── Labels (hide default shiny labels) ── */
.control-label { display: none !important; }

/* ── Skeleton shimmer ── */
@keyframes shimmer {
    0%   { background-position: -600px 0; }
    100% { background-position: 600px 0; }
}
.skeleton {
    background: linear-gradient(90deg, #141a24 30%, #1c2430 50%, #141a24 70%);
    background-size: 600px 100%;
    animation: shimmer 1.6s infinite ease-in-out;
    border-radius: 10px;
}
.skeleton-chart { height: 380px; width: 100%; border-radius: 12px; }
.skeleton-table { height: 260px; width: 100%; border-radius: 12px; }
.skeleton-kpi {
    height: 100px;
    width: 140px;
    display: inline-block;
    margin: 4px;
    border-radius: 10px;
}

/* ── KPI cards ── */
.kpi-card {
    transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1),
                border-color 0.2s ease,
                box-shadow 0.2s ease;
    cursor: default;
}
.kpi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(92,224,216,0.25) !important;
    box-shadow: 0 6px 24px rgba(0,0,0,0.3);
}

/* ── Navbar ── */
.navbar {
    background: #080b10 !important;
    border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    box-shadow: none !important;
    padding: 0 24px !important;
}
.navbar-brand {
    padding: 12px 0 !important;
}
.navbar .nav-link {
    color: #6b7b8d !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 14px 16px !important;
    transition: color 0.2s ease !important;
    border-bottom: 2px solid transparent !important;
}
.navbar .nav-link:hover {
    color: #eaf0f6 !important;
}
.navbar .nav-link.active {
    color: #5ce0d8 !important;
    border-bottom-color: #5ce0d8 !important;
}

/* ── Surface panels ── */
.surface-panel {
    background: #12161e;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
}
.surface-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(92,224,216,0.15), transparent);
}

/* ── Chart containers ── */
.chart-container {
    background: #12161e;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 8px;
    position: relative;
    overflow: hidden;
}
.chart-container::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(92,224,216,0.1), transparent);
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* ── Widget cleanup ── */
.widget-subarea { padding: 0 !important; }
.jupyter-widgets-output-area { padding: 0 !important; }

/* ── Fade-in animation ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeUp 0.35s ease-out forwards; }
.fade-in-delay-1 { animation-delay: 0.05s; opacity: 0; }
.fade-in-delay-2 { animation-delay: 0.1s; opacity: 0; }
.fade-in-delay-3 { animation-delay: 0.15s; opacity: 0; }

/* ── Position badge ── */
.pos-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
}

/* ── Section labels ── */
.section-label {
    color: #4a5568;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
"""

# ── Chart placeholder (empty dark figure) ──────────────────────────────────
def _empty_figure(height: int = 380) -> go.Figure:
    return go.Figure().update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )


# ── KPI card component ────────────────────────────────────────────────────
def kpi_card_html(label: str, value, league_avg, percentile: int) -> ui.Tag:
    if percentile >= 75:
        pct_color = "#5ce0d8"
    elif percentile >= 50:
        pct_color = "#5ca8e0"
    elif percentile >= 25:
        pct_color = "#e0a85c"
    else:
        pct_color = "#e07b7b"
    bar_width = max(3, percentile)

    return ui.div(
        ui.div(
            label,
            style="color: #4a5568; font-size: 9px; font-weight: 600; letter-spacing: 1.2px; "
                  "text-transform: uppercase; margin-bottom: 10px;",
        ),
        ui.div(
            str(value),
            style="color: #eaf0f6; font-size: 26px; font-weight: 700; line-height: 1; "
                  "margin-bottom: 10px; font-family: 'DM Mono', monospace !important;",
        ),
        ui.div(
            ui.div(
                style=f"width: {bar_width}%; height: 3px; background: {pct_color}; "
                      f"border-radius: 2px; transition: width 0.5s ease;",
            ),
            style="width: 100%; background: rgba(255,255,255,0.06); border-radius: 2px; margin-bottom: 8px;",
        ),
        ui.div(
            ui.span(
                f"{percentile}th",
                style=f"color: {pct_color}; font-size: 11px; font-weight: 700; "
                      f"font-family: 'DM Mono', monospace !important;",
            ),
            ui.span(
                f"  avg {league_avg}",
                style="color: #3a4556; font-size: 10px; font-family: 'DM Mono', monospace !important;",
            ),
        ),
        class_="kpi-card",
        style="background: #12161e; border: 1px solid rgba(255,255,255,0.05); "
              "border-radius: 10px; padding: 16px 18px; min-width: 130px; flex: 1;",
    )


def skeleton_kpis():
    return ui.div(
        *[ui.div(class_="skeleton skeleton-kpi") for _ in range(6)],
        style="display: flex; flex-wrap: wrap; gap: 10px;",
    )


# ── App UI ─────────────────────────────────────────────────────────────────
app_ui = ui.page_navbar(
    ui.nav_panel(
        "Player Scouting",
        ui.tags.head(ui.tags.style(CUSTOM_CSS)),
        ui.layout_sidebar(
            ui.sidebar(
                # Branding
                ui.div(
                    ui.div(
                        ui.tags.span(
                            "VB",
                            style="color: #5ce0d8; font-weight: 800; font-size: 18px; "
                                  "letter-spacing: 2px; font-family: 'DM Mono', monospace !important;",
                        ),
                        ui.tags.span(
                            " ANALYTICS",
                            style="color: #6b7b8d; font-weight: 600; font-size: 11px; "
                                  "letter-spacing: 3px; vertical-align: middle;",
                        ),
                    ),
                    style="border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 20px; margin-bottom: 24px;",
                ),
                # League filter
                ui.p("LEAGUE", class_="section-label"),
                ui.input_select("league", None, choices=list(LEAGUES.keys()), selected="All Leagues"),
                ui.div(style="height: 20px;"),
                # Position filter
                ui.p("POSITION", class_="section-label"),
                ui.input_select("position", None, choices=list(POSITIONS.keys()), selected="Outside Hitter"),
                ui.div(style="height: 20px;"),
                # Player select
                ui.p("PLAYER", class_="section-label"),
                ui.input_select("primary_player", None, choices=[]),
                ui.div(style="height: 28px;"),
                # Player meta card
                ui.output_ui("player_meta"),
                width=260,
                style="background: linear-gradient(180deg, #0e1219, #0b0f15); "
                      "border-right: 1px solid rgba(255,255,255,0.05); padding: 24px 20px;",
            ),
            # ── Main content area ──
            ui.div(
                # Player header
                ui.output_ui("player_header"),
                ui.div(style="height: 20px;"),
                # KPI section
                ui.div(
                    ui.p("SEASON OVERVIEW", class_="section-label"),
                    ui.output_ui("kpi_cards"),
                    class_="fade-in fade-in-delay-1",
                ),
                ui.div(style="height: 20px;"),
                # Charts row
                ui.layout_columns(
                    ui.div(
                        output_widget("radar_chart"),
                        class_="chart-container fade-in fade-in-delay-2",
                    ),
                    ui.div(
                        output_widget("scatter_plot"),
                        class_="chart-container fade-in fade-in-delay-2",
                    ),
                    col_widths=[6, 6],
                ),
                ui.div(style="height: 20px;"),
                # Top performances table
                ui.div(
                    output_widget("top_performances"),
                    class_="chart-container fade-in fade-in-delay-3",
                ),
                style="padding: 24px 28px; background: #0b0f15; min-height: 100vh;",
            ),
        ),
    ),
    ui.nav_panel(
        "Team Tendencies",
        ui.tags.head(ui.tags.style(CUSTOM_CSS)),
        ui.div(
            ui.div(
                ui.p("TEAM TENDENCIES", style="color: #4a5568; font-size: 10px; font-weight: 600; letter-spacing: 1.5px;"),
                ui.p("Coming soon", style="color: #6b7b8d; font-size: 14px; margin-top: 8px;"),
                class_="surface-panel",
                style="max-width: 400px; text-align: center; margin: 60px auto;",
            ),
            style="padding: 40px; background: #0b0f15; min-height: 100vh;",
        ),
    ),
    ui.nav_panel(
        "Match Center",
        ui.tags.head(ui.tags.style(CUSTOM_CSS)),
        ui.div(
            ui.div(
                ui.p("MATCH CENTER", style="color: #4a5568; font-size: 10px; font-weight: 600; letter-spacing: 1.5px;"),
                ui.p("Coming soon", style="color: #6b7b8d; font-size: 14px; margin-top: 8px;"),
                class_="surface-panel",
                style="max-width: 400px; text-align: center; margin: 60px auto;",
            ),
            style="padding: 40px; background: #0b0f15; min-height: 100vh;",
        ),
    ),
    title=ui.tags.span(
        ui.tags.b("VB", style="color: #5ce0d8; font-family: 'DM Mono', monospace !important;"),
        ui.tags.span(
            " Analytics",
            style="color: #eaf0f6; font-size: 14px; font-weight: 600; letter-spacing: 0.5px;",
        ),
    ),
    navbar_options=ui.navbar_options(bg="#080b10", inverse=True),
    id="navbar",
)


# ── Server ─────────────────────────────────────────────────────────────────
def server(input, output, session):

    # ── Reactive data sources ──────────────────────────────────────────────
    @reactive.calc
    def players_df():
        position_id = POSITIONS[input.position()]
        league = LEAGUES[input.league()]
        return get_players_by_position(position_id, league)

    # Single effect to update the player dropdown (uses cached players_df)
    @reactive.effect
    def _update_players():
        df = players_df()
        choices = {
            str(r.player_id): f"{r.player_name}  ·  {r.team_code}"
            for _, r in df.iterrows()
        }
        ui.update_select("primary_player", choices=choices)

    @reactive.calc
    def position_stats():
        position_id = POSITIONS[input.position()]
        league = LEAGUES[input.league()]
        return add_derived_stats(get_position_stats(position_id, league))

    @reactive.calc
    def player_stats():
        pid = input.primary_player()
        if not pid:
            return pd.DataFrame()
        df = players_df()
        if not any(df["player_id"].astype(str) == str(pid)):
            return pd.DataFrame()
        league = LEAGUES[input.league()]
        return add_derived_stats(get_player_stats(int(pid), league))

    def selected_player_name() -> str:
        pid = input.primary_player()
        if not pid:
            return ""
        df = players_df()
        row = df[df["player_id"].astype(str) == pid]
        return row.iloc[0]["player_name"] if not row.empty else ""

    # ── Player header ──────────────────────────────────────────────────────
    @output
    @render.ui
    def player_header():
        name = selected_player_name()
        if not name:
            return ui.div(
                ui.div(
                    ui.p(
                        "Select a player from the sidebar to begin scouting",
                        style="color: #4a5568; font-size: 13px; margin: 0;",
                    ),
                    class_="surface-panel",
                    style="text-align: center; padding: 28px;",
                ),
            )

        pid = input.primary_player()
        df = players_df()
        row = df[df["player_id"].astype(str) == pid]
        if row.empty:
            return ui.div()
        r = row.iloc[0]

        pos_id = POSITIONS[input.position()]
        pos_abbr, pos_color = POSITION_TAGS.get(pos_id, ("—", "#6b7b8d"))

        return ui.div(
            ui.div(
                ui.h2(
                    name,
                    style="color: #eaf0f6; font-size: 24px; font-weight: 700; margin: 0 0 8px 0; "
                          "letter-spacing: -0.5px;",
                ),
                ui.div(
                    ui.span(
                        pos_abbr,
                        class_="pos-badge",
                        style=f"background: {pos_color}22; color: {pos_color}; border: 1px solid {pos_color}44; margin-right: 10px;",
                    ),
                    ui.span(
                        r.get("team_name", r.get("team_code", "")),
                        style="color: #6b7b8d; font-size: 13px; margin-right: 16px;",
                    ),
                    ui.span(
                        r.get("league", "").upper(),
                        style="color: #5ce0d8; font-size: 11px; font-weight: 700; letter-spacing: 1px; "
                              "font-family: 'DM Mono', monospace !important;",
                    ),
                ),
            ),
            class_="surface-panel fade-in",
        )

    # ── Sidebar meta ───────────────────────────────────────────────────────
    @output
    @render.ui
    def player_meta():
        name = selected_player_name()
        if not name:
            return ui.div(
                ui.p(
                    "No player selected",
                    style="color: #3a4556; font-size: 11px; text-align: center; padding: 16px 0;",
                ),
            )
        p_stats = player_stats()
        if p_stats.empty:
            return ui.div()
        sets_val = int(p_stats.iloc[0].get("sets_played", 0))
        points_val = int(p_stats.iloc[0].get("points", 0))

        def _mini_stat(label: str, val: str) -> ui.Tag:
            return ui.div(
                ui.span(
                    label,
                    style="color: #3a4556; font-size: 9px; font-weight: 600; letter-spacing: 1.2px; display: block; margin-bottom: 4px;",
                ),
                ui.span(
                    val,
                    style="color: #eaf0f6; font-size: 22px; font-weight: 700; font-family: 'DM Mono', monospace !important;",
                ),
                style="text-align: center; flex: 1;",
            )

    # ── KPI cards ──────────────────────────────────────────────────────────
    @output
    @render.ui
    def kpi_cards():
        p_stats = player_stats()
        pos_stats = position_stats()
        if p_stats.empty or pos_stats.empty:
            return skeleton_kpis()
        position_id = POSITIONS[input.position()]
        kpis = get_kpi_data(p_stats, pos_stats, position_id)
        if not kpis:
            return ui.div()
        cards = [kpi_card_html(k["label"], k["value"], k["league_avg"], k["percentile"]) for k in kpis]
        return ui.div(*cards, style="display: flex; flex-wrap: wrap; gap: 10px;")

    # ── Charts ─────────────────────────────────────────────────────────────
    @output
    @render_widget
    def radar_chart():
        p_stats = player_stats()
        pos_stats = position_stats()
        if p_stats.empty or pos_stats.empty:
            return _empty_figure(380)
        position_id = POSITIONS[input.position()]
        radar = get_radar_data(p_stats, pos_stats, position_id)
        if not radar:
            return _empty_figure(380)
        return build_radar_chart(radar, selected_player_name())

    @output
    @render_widget
    def scatter_plot():
        pos_stats = position_stats()
        if pos_stats.empty:
            return _empty_figure(380)
        return build_scatter_plot(pos_stats, selected_player_name(), POSITIONS[input.position()])

    @output
    @render_widget
    def top_performances():
        pid = input.primary_player()
        if not pid:
            return _empty_figure(260)
        league = LEAGUES[input.league()]
        position_id = POSITIONS[input.position()]
        df = get_top_performances(int(pid), position_id, league)
        return build_top_performances_table(df, position_id)


app = App(app_ui, server)