import duckdb
import pandas as pd

DB_PATH = "data/volleyball.duckdb"

def get_player_by_position(position: int, league: str = "all"):
    con = duckdb.connect(DB_PATH, read_only=True)
    league_filter = "" if league == "all" else f"AND league = '{league}'"
    query = f"""
        SELECT
            ANY_VALUE(player_name) as player_name,
            primary_position,
            player_id,
            league,
            CASE WHEN league = 'au' THEN 'AU'
                ELSE MAX(team_code)
            END AS team_code,
            MAX(team_name) AS team_name,
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
            SUM(sets_played) AS sets_played,
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
        JOIN player_info
            ON player_boxscores.player_name = player_info.player_name 
            AND player_boxscores.league = player_info.league
        WHERE TRY_CAST(player_info.player_id AS INT) = {player_id}
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
            SUM(sets_played) AS sets_played,
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
        JOIN player_info
            ON player_boxscores.player_name = player_info.player_name 
            AND player_boxscores.league = player_info.league
        WHERE player_info.primary_position = {position}
        {league_filter}
        GROUP BY player_id, player_boxscores.league
        ORDER BY player_name
    """
    df = con.execute(query).df()
    con.close()
    return df