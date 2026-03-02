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
            "metrics": ["sets_played", "pass_rating", "total_digs", 
                        "digs_per_set", "total_assists", "assists_per_set"],
            "labels": [],
        }
    },
    2: {  # Outside
        "radar": {
            "metrics": ["kills_per_set", "attack_efficiency", "positive_reception_ratio", 
                        "serve_efficiency", "digs_per_set", "blocks_per_set"],
            "labels": ["Kills/Set", "Hit %", "Pos Pass %", 
                        "Serve Eff", "Digs/Set", "Blocks/Set"],
        },
        "kpi": {
            "metrics": ["sets_played", "attack_efficiency", "kills_per_set", ],
            "labels": [],
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
            "metrics": [],
            "labels": [],
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
            "metrics": [],
            "labels": [],
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
            "metrics": [],
            "labels": [],
        }
    },
}