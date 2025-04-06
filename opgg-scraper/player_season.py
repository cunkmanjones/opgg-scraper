import pandas as pd


# Return Dataframe of Seasons
def get_seasons_list(data) -> pd.DataFrame:
    seasonIds = data['data']['seasons']
    seasonData = pd.DataFrame(seasonIds)[['id', 'value', 'display_value', 'split', 'season', 'is_preseason']]
    
    # Return Reversed Dataframe Order
    return seasonData[~seasonData.is_preseason].loc[:: -1]
