import duckdb
import pandas as pd
from pyvolleydata import get_data

DB_PATH = "data/volleyball.duckdb"

LEAGUES = {
    "lovb": None,
    "mlv": None,
    "au": [2024, 2025],
}


def build_database():
    boxscores = pd.DataFrame()
    pbp = pd.DataFrame()
    events = pd.DataFrame()
    player_info = pd.DataFrame()

    for league, seasons in LEAGUES.items():
        bs = get_data.load_player_boxscore(league, seasons)
        pb = get_data.load_pbp(league, seasons)
        el = get_data.load_events_log(league, seasons)
        pi = get_data.load_player_info(league, seasons)
        boxscores = pd.concat([boxscores, bs], ignore_index=True)
        pbp = pd.concat([pbp, pb], ignore_index=True)
        events = pd.concat([events, el], ignore_index=True)
        player_info = pd.concat([player_info, pi], ignore_index=True)

    con = duckdb.connect(DB_PATH)
    con.execute("CREATE OR REPLACE TABLE player_boxscores AS SELECT * FROM boxscores")
    con.execute("CREATE OR REPLACE TABLE pbp AS SELECT * FROM pbp")
    con.execute("CREATE OR REPLACE TABLE events_log AS SELECT * FROM events")
    con.execute("CREATE OR REPLACE TABLE player_info AS SELECT * FROM player_info")
    con.close()

if __name__ == "__main__":
    build_database()