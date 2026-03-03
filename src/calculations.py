import pandas as pd
import numpy as np

POSITION_METRICS = {
    1: {  # Libero
        "radar": {
            "metrics": ["receptions_per_set", "perfect_reception_ratio", "positive_reception_ratio", 
                        "playable_reception_ratio", "digs_per_set", "assists_per_set"],
            "labels": ["Rec/Set", "Perfect Pass %", "Pos Pass %",
                       "Playable Pass %", "Digs/Set", "Ast/Set"],
        },
        "kpi": {
            "metrics": ["sets_played", "pass_rating", "successful_digs", 
                        "digs_per_set", "assists", "assists_per_set"],
            "labels": ["Sets Played", "Pass RTG", "Total Digs", "Digs/Set",
                       "Total Assists", "Ast/Set"],
        }
    },
    2: {  # Outside
        "radar": {
            "metrics": ["kills_per_set", "attack_efficiency", "positive_reception_ratio", 
                        "serve_efficiency", "digs_per_set", "blocks_per_set",],
            "labels": ["Kills/Set", "Hit %", "Pos Pass %", "Serve Eff", "Digs/Set", "Blocks/Set"],
        },
        "kpi": {
            "metrics": ["sets_played", "attack_kills", "kills_per_set", "attack_efficiency",
                        "pass_rating", "successful_digs", "digs_per_set", "total_blocks", 
                        "blocks_per_set", "serve_aces", "serve_aces_per_set", "serve_efficiency"],
            "labels": ["Sets Played", "Total Kills", "Kills/Set", "Hit %", "Pass RTG", "Total Digs", 
                       "Digs/Set", "Total Blocks", "Blocks/Set", "Total Aces", "Aces/Set", "Serve Eff"],
        }
    },
    3: {  # Opposite
        "radar": {
            "metrics": ["kills_per_set", "attack_efficiency", "serve_aces_per_set",
                        "serve_efficiency", "digs_per_set", "blocks_per_set", ],
            "labels": ["Kills/Set", "Hit %", "Aces/Set", 
                        "Serve Eff", "Digs/Set", "Blocks/Set"],
        },
        "kpi": {
            "metrics": ["sets_played", "attack_kills", "kills_per_set", "attack_efficiency",
                        "successful_digs", "digs_per_set", "total_blocks", "blocks_per_set",
                        "serve_aces", "serve_aces_per_set", "serve_efficiency"],
            "labels": ["Sets Played", "Total Kills", "Kills/Set", "Hit %", 
                        "Total Digs", "Digs/Set", "Total Blocks", "Blocks/Set",
                        "Total Aces", "Aces/Set", "Serve Eff"],
        }
    },
    4: {  # Middle
        "radar": {
            "metrics": ["kills_per_set", "attack_efficiency", "serve_aces_per_set",
                        "serve_efficiency", "block_touches_per_set", "block_kills_per_set"],
            "labels": ["Kills/Set", "Hit %", "Aces/Set", 
                        "Serve Eff", "Block Touches/Set", "Block Kills/Set"],
        },
        "kpi": {
            "metrics": ["sets_played", "attack_kills", "kills_per_set", "attack_efficiency",
                        "total_blocks", "block_points", "block_touches", "blocks_per_set",
                        "serve_aces", "serve_aces_per_set", "serve_efficiency"],
            "labels": ["Sets Played", "Total Kills", "Kills/Set", "Hit %", "Total Blocks", "Block Kills", 
                       "Block Touches", "Blocks/Set", "Total Aces", "Aces/Set", "Serve Eff"],
        }
    },
    5: {  # Setter
        "radar": {
            "metrics": ["assists_per_set", "kills_per_set", "attack_efficiency",
                        "serve_efficiency", "digs_per_set", "blocks_per_set"],
            "labels": ["Ast/Set", "Kills/Set", "Hit %", 
                        "Serve Eff", "Digs/Set", "Blocks/Set"],
        },
        "kpi": {
            "metrics": ["sets_played", "assists", "assists_per_set", "attack_kills", "kills_per_set", 
                        "attack_efficiency", "serve_aces", "serve_aces_per_set", "serve_efficiency",
                        "total_blocks", "blocks_per_set", "successful_digs", "digs_per_set"],
            "labels": ["Sets Played", "Total Assists", "Ast/Set", "Total Kills", "Kills/Set", "Hit %", "Total Aces", 
                       "Aces/Set", "Serve Eff", "Total Blocks", "Blocks/Set", "Total Digs", "Digs/Set"],
        }
    },
}


def add_derived_stats(df : pd.DataFrame):
    df = df.copy()
    sets = df["sets_played"].replace(0, np.nan)
    receptions = df["receptions"].replace(0, np.nan)
    attacks = df["attack_attempts"].replace(0, np.nan)
    serves = df["serve_attempts"].replace(0, np.nan)

    # --- PASSING & DEFENSE ---
    df["receptions_per_set"] = (df["receptions"] / sets).round(2)
    df["playable_reception_ratio"] = ((df["receptions"] - df["reception_errors"]) / receptions).round(2)
    df["digs_per_set"] = (df["successful_digs"] / sets).round(2)
    
    pefect_receptions = (df["perfect_reception_ratio"] * df["receptions"]).round()
    positive_receptions = (df["positive_reception_ratio"] * df["receptions"] - pefect_receptions).round()
    poor_receptions = (df["receptions"] - positive_receptions - pefect_receptions - df["reception_errors"]).round()
    df["pass_rating"] = ((3 * pefect_receptions + 2 * positive_receptions + poor_receptions) / df["receptions"]).round(2)
    

    # --- SETTING ---
    df["assists_per_set"] = (df["assists"] / sets).round(2)

    # --- OFFENSE ---
    df["kills_per_set"] = (df["attack_kills"] / sets).round(2)
    df["attack_efficiency"] = ((df["attack_kills"] - df["attack_errors"]) / attacks).round(2)

    # --- SERVING ---
    df["serve_aces_per_set"] = (df["serve_aces"] / sets).round(2)
    df["serve_efficiency"] = ((df["serve_aces"] - df["serve_errors"]) / serves).round(2)

    # --- BLOCKING ---
    df["blocks_per_set"] = ((df["block_points"] + df["block_touches"]) / sets).round(2) 
    df["block_kills_per_set"] = (df["block_points"] / sets).round(2) 
    df["block_touches_per_set"] = (df["block_touches"] / sets).round(2)
    df["total_blocks"] = df["block_points"] + df["block_touches"]

    return df


def calculate_percentiles(df: pd.DataFrame, metrics: list) -> pd.DataFrame:
    df = df.copy()
    for metric in metrics:
        if metric in df.columns:
            df[f"{metric}_percentile"] = df[metric].rank(pct=True).round(3)
    return df   


def get_radar_data(player_df: pd.DataFrame, league_df: pd.DataFrame, position: int):
    config = POSITION_METRICS[position]["radar"]
    metrics = config["metrics"]
    labels = config["labels"]

    ranked_df = calculate_percentiles(league_df, metrics)
    target_player_id = player_df.iloc[0]["player_id"]
    player_row = ranked_df[ranked_df["player_id"] == target_player_id].iloc[0].fillna(0)

    player_radar_percentiles = [player_row.get(f"{m}_percentile", 0) for m in metrics]
    league_avg_percentiles = [0.5 for _ in metrics] 
    
    player_raw_stats = [player_row.get(m, 0) for m in metrics]
    league_avg_stats = [league_df[m].mean().round(2) if m in league_df.columns else 0 for m in metrics]

    return {
        "labels": labels,
        "player_radar_percentiles": player_radar_percentiles,
        "league_avg_percentiles": league_avg_percentiles,
        "player_raw_stats": player_raw_stats,
        "league_avg_stats": league_avg_stats,
    }


def get_kpi_data(player_df: pd.DataFrame, league_df: pd.DataFrame, position: int) -> list:
    config = POSITION_METRICS[position]["kpi"]
    metrics = config["metrics"]
    labels = config["labels"]

    ranked_df = calculate_percentiles(league_df, metrics)
    target_player_id = player_df.iloc[0]["player_id"]
    player_row = ranked_df[ranked_df["player_id"] == target_player_id].iloc[0].fillna(0)

    kpi_cards = []
    
    for i, metric in enumerate(metrics):
        player_val = player_row.get(metric, 0)
        league_avg = league_df[metric].mean() if metric in league_df.columns else 0
        percentile_rank = player_row.get(f"{metric}_percentile", 0)
        
        kpi_cards.append({
            "label": labels[i],
            "value": round(player_val, 2), 
            "league_avg": round(league_avg, 2),
            "percentile": int(percentile_rank * 100)
        })

    return kpi_cards