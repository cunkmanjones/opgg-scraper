import pandas as pd

from api_calls import api_call
from constants import API_SUMMONER_URL
from conversions import *


# Increase Column Size for Debugging in Terminal
pd.set_option("display.max_colwidth", None)
# https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
pd.options.mode.copy_on_write = True

# OPGG API V3
def _v3_api_champion_stats(playerData, championData, seasonId) -> pd.DataFrame:
    playerDataFrame = pd.DataFrame(playerData)

    # Game Seconds Null prior to 13 (S9)
    if seasonId <= 11:
        functionDictionary = {
            "cs": lambda: call_lua_math_function(
                'Average_cs', 
                playerDataFrame['minion_kill'].tolist(), 
                playerDataFrame['neutral_minion_kill'].tolist(), 
                playerDataFrame['play'].tolist()
            ),
            "kda": lambda: call_lua_math_function(
                'Kda_ratio', 
                playerDataFrame['kill'].tolist(), 
                playerDataFrame['death'].tolist(), 
                playerDataFrame['assist'].tolist()
            ),
            "gold": lambda: call_lua_math_function(
                'Average_gold', 
                playerDataFrame['gold_earned'].tolist(), 
                playerDataFrame['play'].tolist()
            ),
            "winrate": lambda: call_lua_math_function(
                'Win_rate', 
                playerDataFrame['win'].tolist(), 
                playerDataFrame['play'].tolist()
            )
        }
        selectedColumns = ['name', 'play', 'win', 'lose', 'winrate', 'kda', 'kill', 'death', 'assist', 'cs', 'gold']
    else:
        functionDictionary = {
            "total_cs": lambda: call_lua_math_function(
                'Average_cs', 
                playerDataFrame['minion_kill'].tolist(), 
                playerDataFrame['neutral_minion_kill'].tolist(), 
                playerDataFrame['play'].tolist()
            ), 
            "kda": lambda: call_lua_math_function(
                'Kda_ratio', 
                playerDataFrame['kill'].tolist(), 
                playerDataFrame['death'].tolist(), 
                playerDataFrame['assist'].tolist()
            ),
            "gold_per_match": lambda: call_lua_math_function(
                'Average_gold', 
                playerDataFrame['gold_earned'].tolist(), 
                playerDataFrame['play'].tolist()
            ),
            "game_length": lambda: call_lua_math_function(
                'Average_game_length', 
                playerDataFrame['game_length_second'].tolist(), 
                playerDataFrame['play'].tolist()
            ),
            "winrate": lambda: call_lua_math_function(
                'Win_rate', 
                playerDataFrame['win'].tolist(), 
                playerDataFrame['play'].tolist()
            ),
            "csm": lambda: call_lua_math_function(
                'Cs_per_minute', 
                playerDataFrame['total_cs'].tolist(), 
                playerDataFrame['game_length'].tolist()
            ),
            "gpm": lambda: call_lua_math_function(
                'Gold_per_minute', 
                playerDataFrame['gold_per_match'].tolist(), 
                playerDataFrame['game_length'].tolist()
            )
        }
        selectedColumns = ['name', 'play', 'win', 'lose', 'winrate', 'kda', 'kill', 'death', 'assist', 'total_cs', 'csm', 'gold_per_match', 'gpm', 'game_length']

    mergedDataFrame = merge_function_columns(functionDictionary, playerDataFrame, championData)
    completeDataFrame = mergedDataFrame[selectedColumns]
    return round_dataframe(completeDataFrame)

# Return Summoner Stats
def get_summoner_stats(regionId, seasonId, gameType, data, championData):
    # Check if Summoner ID is Valid
    summonerId = data['data']['summoner_id']
    seasonId = int(seasonId)

    try:
        playerData = api_call(f'{API_SUMMONER_URL}/{regionId}/summoners/{summonerId}/most-champions/rank?game_type={gameType}&season_id={seasonId}') ###
        championStats = playerData['data']['champion_stats']
    except ValueError:
        #print("Invalid Season ID.")
        return None
    except TypeError:
        return pd.DataFrame()

    return _v3_api_champion_stats(championStats, championData, seasonId)
    