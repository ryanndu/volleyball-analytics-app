import duckdb
import pandas as pd
import plotly.graph_objects as go

DB_PATH = "data/volleyball.duckdb"

def get_players_by_position(position: int, league: str = "all"):
    con = duckdb.connect(DB_PATH, read_only=True)
    league_filter = "" if league == "all" else f"AND league = '{league}'"
    query = f"""
        SELECT
            ANY_VALUE(player_name) as player_name,
            primary_position,
            player_id,
            league,
            CASE WHEN league = 'au' THEN 'AU'
                ELSE LAST(team_code ORDER BY match_datetime)
            END AS team_code,
            LAST(team_name ORDER BY match_datetime) AS team_name,
        FROM player_info
        WHERE primary_position = '{position}'
        {league_filter}
        GROUP BY player_id, primary_position, league
        ORDER BY player_name
    """

    df = con.execute(query).df()
    con.close()
    return df


def get_player_stats(player_id: int, league: str = "all"):
    con = duckdb.connect(DB_PATH, read_only=True)
    league_filter = "" if league == "all" else f"AND player_boxscores.league = '{league}'"
    query = f"""
        SELECT
            ANY_VALUE(player_boxscores.player_name) AS player_name,
            player_id,
            player_boxscores.league,
            COUNT(*) AS sets_played,
            SUM(earned_points) AS points,
            SUM(attack_attempts) AS attack_attempts,
            SUM(attack_kills) AS attack_kills,
            SUM(attack_errors) AS attack_errors,
            SUM(serves) AS serve_attempts,
            SUM(serve_aces) AS serve_aces,
            SUM(serve_errors) AS serve_errors,
            SUM(block_points) AS block_points,
            SUM(block_touches) AS block_touches,
            SUM(receptions) AS receptions,
            SUM(reception_errors) AS reception_errors,
            ROUND(AVG(perfect_reception_ratio), 3) AS perfect_reception_ratio,
            ROUND(AVG(positive_reception_ratio), 3) AS positive_reception_ratio,
            SUM(assists) AS assists,
            SUM(successful_digs) AS successful_digs
        FROM player_boxscores
        JOIN (SELECT DISTINCT player_name, league, TRY_CAST(player_id AS INT) AS player_id FROM player_info) pi
            ON player_boxscores.player_name = pi.player_name
            AND player_boxscores.league = pi.league
        WHERE pi.player_id = {player_id}
        {league_filter}
        GROUP BY player_id, player_boxscores.league
    """
    df = con.execute(query).df()
    con.close()
    return df


def get_position_stats(position: int, league: str = "all"):
    con = duckdb.connect(DB_PATH, read_only=True)
    league_filter = "" if league == "all" else f"AND player_boxscores.league = '{league}'"
    query = f"""
        SELECT
            ANY_VALUE(player_boxscores.player_name) AS player_name,
            player_id,
            player_boxscores.league,
            COUNT(*) AS sets_played,
            SUM(earned_points) AS points,
            SUM(attack_attempts) AS attack_attempts,
            SUM(attack_kills) AS attack_kills,
            SUM(attack_errors) AS attack_errors,
            SUM(serves) AS serve_attempts,
            SUM(serve_aces) AS serve_aces,
            SUM(serve_errors) AS serve_errors,
            SUM(block_points) AS block_points,
            SUM(block_touches) AS block_touches,
            SUM(receptions) AS receptions,
            SUM(reception_errors) AS reception_errors,
            ROUND(AVG(perfect_reception_ratio), 3) AS perfect_reception_ratio,
            ROUND(AVG(positive_reception_ratio), 3) AS positive_reception_ratio,
            SUM(assists) AS assists,
            SUM(successful_digs) AS successful_digs
        FROM player_boxscores
        JOIN (SELECT DISTINCT player_name, league, primary_position, TRY_CAST(player_id AS INT) AS player_id FROM player_info) pi
            ON player_boxscores.player_name = pi.player_name
            AND player_boxscores.league = pi.league
        WHERE pi.primary_position = {position}
        {league_filter}
        GROUP BY pi.player_id, player_boxscores.league
        ORDER BY player_name
    """
    df = con.execute(query).df()
    con.close()
    return df


def get_top_performances(player_id: int, league: str = "all", top_n: int = 5):
    con = duckdb.connect(DB_PATH, read_only=True)
    
    league_filter = "" if league == "all" else f"AND player_boxscores.league = '{league}'"
    
    query = f"""
        SELECT
            schedule.date AS "Date",
            schedule.home_team AS "Home",
            schedule.away_team AS "Away",
            COUNT(*) AS "Sets",
            SUM(player_boxscores.attack_kills) AS "Kills",
            SUM(player_boxscores.assists) AS "Assists",
            SUM(player_boxscores.serve_aces) AS "Aces",
            SUM(player_boxscores.block_points) AS "Block_Kills",
            SUM(player_boxscores.block_touches) AS "Block_Touches",
            SUM(player_boxscores.successful_digs) AS "Digs",
            ROUND(SUM(player_boxscores.perfect_reception_ratio * player_boxscores.receptions)) AS "Perfect_Passes",
            ROUND(SUM(player_boxscores.positive_reception_ratio * player_boxscores.receptions) - 
                  SUM(player_boxscores.perfect_reception_ratio * player_boxscores.receptions)) AS "Positive_Passes",
            (SUM(player_boxscores.attack_kills) + 
             SUM(player_boxscores.assists) + 
             SUM(player_boxscores.serve_aces) + 
             SUM(player_boxscores.block_points) + 
             SUM(player_boxscores.successful_digs) +
             ROUND(SUM(player_boxscores.perfect_reception_ratio * player_boxscores.receptions)) +
             ROUND(SUM(player_boxscores.positive_reception_ratio * player_boxscores.receptions))) AS "Total_Impact"
             
        FROM player_boxscores
        JOIN (SELECT DISTINCT player_name, league, TRY_CAST(player_id AS INT) AS player_id FROM player_info) pi
            ON player_boxscores.player_name = pi.player_name
            AND player_boxscores.league = pi.league
        JOIN schedule
            ON player_boxscores.match_id = schedule.match_id
        WHERE pi.player_id = {player_id}
        {league_filter}
        GROUP BY player_boxscores.match_id, schedule.date, schedule.home_team, schedule.away_team
        ORDER BY "Total_Impact" DESC
        LIMIT {top_n}
    """
    
    df = con.execute(query).df()
    con.close()
    
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime('%Y-%m-%d')
        
    return df