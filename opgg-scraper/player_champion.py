import pandas as pd

from api_calls import api_call
from constants import API_BYPASS_URL
from conversions import *


# Increase Column Size for Debugging in Terminal
pd.set_option("display.max_colwidth", None)
# https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
pd.options.mode.copy_on_write = True

# OPGG API V1 DataFrame
def _v1_api_champion_stats(playerData, championData) -> pd.DataFrame:
    playerDataFrame = pd.DataFrame(playerData)
    selectedDataFrame = pd.DataFrame(playerData)[['id', 'play', 'win', 'lose', 'kill', 'death', 'assist']]
    
    # game_length_second is 0, resulting in game_length, csm, & gpm being NaN
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

    # Merge Function Created Columns with Existing Dataframe
    mergedDataFrame = merge_function_columns(functionDictionary, selectedDataFrame, championData)

    completeDataFrame = mergedDataFrame[['name', 'play', 'win', 'lose', 'winrate', 'kda', 'kill', 'death', 'assist', 'cs', 'gold']]
    return round_dataframe(completeDataFrame)

# OPGG API V2 DataFrame
def _v2_api_champion_stats(playerData, championData) -> pd.DataFrame:
    '''
    Unlike API V1, API V2 Player Data is split between 'basic' and 'extend' dicts
    After converting both dicts into lists, we add each list to the main dict 'selectedDataFrame'
    The resulting dict is 'mergedBasicExtendData'
    '''
    selectedDataFrame = pd.DataFrame(playerData)[['id', 'play', 'win', 'lose', 'game_second']]

    basicData = pd.DataFrame(playerData)['basic']
    basicDataCompression = dict_from_list(basicData)

    extendData = pd.DataFrame(playerData)['extend']
    extendDataCompression = dict_from_list(extendData)

    mergedBasicExtendData = pd.concat([selectedDataFrame, pd.DataFrame(basicDataCompression), pd.DataFrame(extendDataCompression)], axis=1)

    # Reminder: New Columns using Created Columns stay below Created
    functionDictionary = {
        "total_cs": lambda: call_lua_math_function(
            'Average_cs', 
            mergedBasicExtendData['cs'].tolist(), 
            mergedBasicExtendData['neutral_cs'].tolist(), 
            mergedBasicExtendData['play'].tolist()
        ), 
        "kda": lambda: call_lua_math_function(
            'Kda_ratio', 
            mergedBasicExtendData['kill'].tolist(), 
            mergedBasicExtendData['death'].tolist(), 
            mergedBasicExtendData['assist'].tolist()
        ),
        "gold_per_match": lambda: call_lua_math_function(
            'Average_gold', 
            mergedBasicExtendData['gold'].tolist(), 
            mergedBasicExtendData['play'].tolist()
        ),
        "game_length": lambda: call_lua_math_function(
            'Average_game_length', 
            mergedBasicExtendData['game_second'].tolist(), 
            mergedBasicExtendData['play'].tolist()
        ),
        "winrate": lambda: call_lua_math_function(
            'Win_rate', 
            mergedBasicExtendData['win'].tolist(), 
            mergedBasicExtendData['play'].tolist()
        ),
        "csm": lambda: call_lua_math_function(
            'Cs_per_minute', 
            mergedBasicExtendData['total_cs'].tolist(), 
            mergedBasicExtendData['game_length'].tolist()
        ),
        "gpm": lambda: call_lua_math_function(
            'Gold_per_minute', 
            mergedBasicExtendData['gold_per_match'].tolist(), 
            mergedBasicExtendData['game_length'].tolist()
        )
    }

    # Merge Function Created Columns with Existing Dataframe
    mergedChampionData = merge_function_columns(functionDictionary, mergedBasicExtendData, championData)

    selectedColumns = ['name', 'play', 'win', 'lose', 'winrate', 'kda', 'kill', 'death', 'assist', 'total_cs', 'csm', 'gold_per_match', 'gpm', 'game_length']
    completeDataFrame = pd.DataFrame(mergedChampionData)[selectedColumns]
    completeDataFrame.loc[0, 'name'] = "All Champions"
    return round_dataframe(completeDataFrame)

# Return Summoner Stats
def get_summoner_stats(regionId, seasonId, gameType, data):
    # Check if Summoner ID is Valid
    summonerId = data['data']['summoner_id']
    championData = pd.DataFrame(data['data']['championsById']).T[['id', 'name', 'image_url']]
    seasonId = int(seasonId)

    # Swap API dependant on Season Input Value
    if seasonId <= 27:
        version, statsString = '', 'champion_stats'
    else:
        version, statsString = 'v2/', 'my_champion_stats'

    try:
        playerData = api_call(f'{API_BYPASS_URL}/summoners/{version}{regionId}/{summonerId}/most-champions/rank?game_type={gameType}&season_id={seasonId}')
        championStats = playerData['data'][statsString]
        '''
        >>> print( playerData['data'].keys() )
        Ouput API V1:
        >>> dict_keys(['game_type', 'season_id', 'year', 'play', 'win', 'lose', 'champion_stats'])
        Ouput API V2: 
        >>> dict_keys(['game_type', 'season_id', 'play', 'win', 'lose', 'my_champion_stats', 'opponent_champion_stats'])
        '''
    except ValueError:
        #print("Invalid Season ID. Please enter a valid integer.")
        return None
    except TypeError:
        return pd.DataFrame()
    
    if seasonId <= 27:
        return _v1_api_champion_stats(championStats, championData)
    return _v2_api_champion_stats(championStats, championData)
    