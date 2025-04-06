import re

from api_calls import api_call
from constants import API_BYPASS_URL, API_LOL_URL


# Use ddragon API for Champion JSON
# Surprisingly faster than single OPGG API Call to /meta/champions/
def get_league_api():
    dataVersions = api_call(f'{API_LOL_URL}/api/versions.json')
    apiVersion = dataVersions[0] # Always First

    dataChamps = api_call(f'{API_LOL_URL}/cdn/{apiVersion}/data/en_US/champion.json')
    championData = dataChamps['data']

    # Example: {'Aatrox' : 266, 'Garen' : 86}
    championDict = {i['id']: int(i['key']) for i in championData.values()}
    return championDict

# Fetch List of OPGG Patch Versions
def get_opgg_patches() -> list:
    errorNum = 1 # Probe Error Message
    data = api_call(f'{API_BYPASS_URL}/champions/global/ranked?&version={errorNum}')
    
    versions = data['detail']['detailMessage']['version'][1] # Second Entry
    '''
    Regex Pattern Explanation:
    # ?<=       - Syntax for positive lookbehind (checks what precedes the match)
    # :[space]  - Literal colon and space characters
    #               → Together matches ': ' but doesn't include it in the result
    # .*        - Main matching pattern
    # .         - Matches any character except newline
    # *         - Quantifier (0 or more repetitions)
    #               → Will match everything until end of line/string
    '''
    pattern = r'(?<=: ).*' 
    match = re.search(pattern, versions)
    if match:
        versionsList = match.group().split(',')
    return versionsList # [0] # First in List

# Return specific Champion Stats
def get_champion_stats(championName, championDict, version, region, gametype, tier):
    statsData = api_call(f'{API_BYPASS_URL}/champions/{region}/{gametype}?tier={tier}&version={version}')
    
    # Example: {266 : 'Aatrox', 86 : 'Garen'}
    #reversedChampionDict = {v: k for k, v in championDict.items()}
    # Get Champion ID Int from Champion Dict
    championId = championDict.get(championName)
    
    if not championId:
        return None
    
    # Find the champion in stats data
    matches = list(filter(lambda x: x['id'] == championId, statsData['data']))

    if not matches:
        return None
    championStats = matches[0]

    # Check if Stats are set to Null
    if championStats['average_stats'] is None:
        return None

    return championStats
