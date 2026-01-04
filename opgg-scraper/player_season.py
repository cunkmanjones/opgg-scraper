import pandas as pd

from api_calls import api_call
from constants import API_SUMMONER_URL


# Return Dataframe of Seasons
def get_seasons_list() -> pd.DataFrame:
    seasons = api_call(f'{API_SUMMONER_URL}/meta/seasons')
    seasonData = pd.DataFrame(seasons['data'])
    
    return seasonData[~seasonData.is_preseason].loc[:: -1]
