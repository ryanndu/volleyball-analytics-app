import duckdb
import pandas as pd
import functools
import hashlib
import time

DB_PATH = "data/volleyball.duckdb"
_connection: duckdb.DuckDBPyConnection | None = None


def _get_connection() -> duckdb.DuckDBPyConnection:
    global _connection
    if _connection is None:
        _connection = duckdb.connect(DB_PATH, read_only=True)
    return _connection


_cache: dict[str, tuple[float, pd.DataFrame]] = {}
_CACHE_TTL = 300  # seconds


def _cached_query(query: str, ttl: float = _CACHE_TTL) -> pd.DataFrame:
    key = hashlib.md5(query.encode()).hexdigest()
    now = time.time()
    if key in _cache:
        ts, df = _cache[key]
        if now - ts < ttl:
            return df.copy()
    con = _get_connection()
    df = con.execute(query).df()
    _cache[key] = (now, df)
    return df.copy()


def get_players_by_position(position: int, league: str = "all") -> pd.DataFrame:
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
    return _cached_query(query)


def get_player_stats(player_id: int, league: str = "all") -> pd.DataFrame:
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
        JOIN (
            SELECT DISTINCT player_name, league, TRY_CAST(player_id AS INT) AS player_id
            FROM player_info
        ) pi
            ON player_boxscores.player_name = pi.player_name
            AND player_boxscores.league = pi.league
        WHERE pi.player_id = {player_id}
        {league_filter}
        GROUP BY player_id, player_boxscores.league
    """
    return _cached_query(query)


def get_position_stats(position: int, league: str = "all") -> pd.DataFrame:
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
        JOIN (
            SELECT DISTINCT player_name, league, primary_position, TRY_CAST(player_id AS INT) AS player_id 
            FROM player_info
        ) pi
            ON player_boxscores.player_name = pi.player_name
            AND player_boxscores.league = pi.league
        WHERE pi.primary_position = {position}
        {league_filter}
        GROUP BY pi.player_id, player_boxscores.league
        ORDER BY player_name
    """
    return _cached_query(query)


POSITION_SORT = {
    1: "SUM(player_boxscores.successful_digs)",
    2: "SUM(player_boxscores.attack_kills)",
    3: "SUM(player_boxscores.attack_kills)",
    4: "SUM(player_boxscores.block_points) + SUM(player_boxscores.block_touches)",
    5: "SUM(player_boxscores.assists)",
}

def get_top_performances(player_id: int, position: int, league: str = "all", top_n: int = 5):    
    league_filter = "" if league == "all" else f"AND player_boxscores.league = '{league}'"
    sort_expr = POSITION_SORT.get(position, "SUM(player_boxscores.attack_kills)")
    
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
                  SUM(player_boxscores.perfect_reception_ratio * player_boxscores.receptions)) AS "Positive_Passes"
        FROM player_boxscores
        JOIN (SELECT DISTINCT player_name, league, TRY_CAST(player_id AS INT) AS player_id FROM player_info) pi
            ON player_boxscores.player_name = pi.player_name
            AND player_boxscores.league = pi.league
        LEFT JOIN schedule
            ON TRY_CAST(player_boxscores.match_id AS BIGINT) = TRY_CAST(schedule.match_id AS BIGINT)
        WHERE pi.player_id = {player_id}
        {league_filter}
        GROUP BY player_boxscores.match_id, schedule.date, schedule.home_team, schedule.away_team
        ORDER BY {sort_expr} DESC
        LIMIT {top_n}
    """
    
    df = _cached_query(query)
    
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime('%b %d, %Y')

    return df