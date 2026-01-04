import re

from api_calls import api_call
from constants import API_SUMMONER_URL


# Fetch OP.GG Summoner ID String (47 Char)
def get_summoner_id(playerString, region):
    '''
    Regex Pattern Explanation:
    # ^.+       - 1+ characters for player name (required)
    # \#        - Literal # character
    # [^#]{3,5} - 3-5 non-# characters for tagline 
    # $         - End of string
    '''
    match = re.fullmatch(r'^(.+)\#([^#]{3,5})$', playerString)
    if not match:
        return None
    playerName, tagline = match.group(1).strip(), match.group(2) # ('#' + match.group(2)) returns auto entries
    #print(f"Name: {playerName} | Tagline: {tagline}")

    # Summarized Player Data JSON
    playerData = api_call(f'{API_SUMMONER_URL}/v3/{region}/summoners?riot_id={playerName}') # Look for Tagline + Autocomplete Solution
    
    # If missing 'data' or 'data' is Empty return None
    if not playerData.get('data') or len(playerData['data']) == 0:
        return None
    
    for entry in playerData['data']:
        if entry.get('game_name') == playerName:  
            summonerId = entry.get('summoner_id') # OP.GG Summoner ID String (47 Char)
        else:
            return None
    #summonerId = playerData['data'][0].get('summoner_id') 
    
    # Expanded Player Data JSON
    playerDataExpanded = api_call(f'{API_SUMMONER_URL}/{region}/summoners/{summonerId}')
    
    return playerDataExpanded
