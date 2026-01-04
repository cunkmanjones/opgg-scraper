import re

from api_calls import api_call
from constants import API_CHAMPION_URL, API_LOL_URL


# Use ddragon API for Champion JSON
def get_league_api():
    versions = api_call(f'{API_LOL_URL}/api/versions.json')
    apiVersion = versions[0] # Always First

    dataChamps = api_call(f'{API_LOL_URL}/cdn/{apiVersion}/data/en_US/champion.json')
    championData = dataChamps['data']

    # Example: {'Aatrox' : 266, 'Garen' : 86}
    championDict = {i['id']: int(i['key']) for i in championData.values()}
    
    return championDict

# Fetch List of OPGG Patch Versions
def get_opgg_patches() -> list:
    patches = api_call(f'{API_CHAMPION_URL}/meta/versions')
    versions = patches['data']

    return versions[:10] # Versions after 10th lack Data

# Return specific Champion Stats
def get_champion_stats(championName, championDict, version, region, gametype, tier):
    championData = api_call(f'{API_CHAMPION_URL}/{region}/champions/{gametype}?tier={tier}&version={version}')
    
    # Example: {266 : 'Aatrox', 86 : 'Garen'}
    #reversedChampionDict = {v: k for k, v in championDict.items()}
    # Get Champion ID Int from Champion Dict
    championId = championDict.get(championName)
    
    if not championId:
        return None
    
    # Find the champion in stats data
    matches = list(filter(lambda x: x['id'] == championId, championData['data']))

    if not matches:
        return None
    championStats = matches[0]

    # Check if Stats are set to Null
    if championStats['average_stats'] is None:
        return None

    return championStats
