import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from calc import *

# Increase Column Size for Debugging in Terminal
#print(pd.get_option("display.max_colwidth"))
pd.set_option("display.max_colwidth", None)
# https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
pd.options.mode.copy_on_write = True

# Champion Stats using API V1
def v1_api_champion_stats(api_data, champion_data):
    #print(pd.DataFrame(api_data).keys())
    api_data_df = pd.DataFrame(api_data)
    clean_data = pd.DataFrame(api_data)[['id', 'play', 'win', 'lose', 'kill', 'death', 'assist']]
    
    # game_length_second is 0, resulting in game_length, csm, & gpm being NaN
    function_dictionary = {
        "cs": lambda: average_cs(api_data_df['minion_kill'], api_data_df['neutral_minion_kill'], api_data_df['play']),
        "kda": lambda: kda_ratio(api_data_df['kill'], api_data_df['death'], api_data_df['assist']),
        "gold": lambda: average_gold(api_data_df['gold_earned'], api_data_df['play']),
        #"game_length": lambda: average_game_length(api_data_df['game_length_second'], api_data_df['play']),
        #"csm": lambda: cs_per_minute(clean_data['cs'], clean_data['game_length']),
        #"gpm": lambda: gold_per_minute(clean_data['gold'], clean_data['game_length']),
        "winrate": lambda: win_rate(api_data_df['win'], api_data_df['play'])
    }

    for key, value in function_dictionary.items():
        clean_data.insert( len(clean_data.columns), key, value())

    merged_data = clean_data.merge(champion_data, on='id', how='left')
    #print(merged_data[['name', 'play', 'win', 'lose', 'winrate', 'kda', 'kill', 'death', 'assist', 'cs', 'gold']])#, 'image_url']])
    print("Champion Stats: ")
    return merged_data[['name', 'play', 'win', 'lose', 'winrate', 'kda', 'kill', 'death', 'assist', 'cs', 'gold']]

# Champion Stats using API V2
def v2_api_champion_stats(api_data, champion_data):
    clean_data = pd.DataFrame(api_data)[['id', 'play', 'win', 'lose', 'game_second']]

    basic_data = pd.DataFrame(api_data)['basic']
    combined_basic = dict_from_list(basic_data)
    #print(pd.DataFrame(combined_basic))

    extend_data = pd.DataFrame(api_data)['extend']
    combined_extend = dict_from_list(extend_data)
    #print(pd.DataFrame(combined_extend))

    merged_data = pd.concat([clean_data, pd.DataFrame(combined_basic), pd.DataFrame(combined_extend)], axis=1)
    #print(pd.DataFrame(merged_data).keys())

    # Reminder: New Columns using Created Columns must stay Below
    function_dictionary = {
        "total_cs": lambda: average_cs(merged_data['cs'], merged_data['neutral_cs'], merged_data['play']),
        "kda": lambda: kda_ratio(merged_data['kill'], merged_data['death'], merged_data['assist']),
        "gold_per_match": lambda: average_gold(merged_data['gold'], merged_data['play']),
        "game_length": lambda: average_game_length(merged_data['game_second'], merged_data['play']),
        "winrate": lambda: win_rate(merged_data['win'], merged_data['play']),

        "csm": lambda: cs_per_minute(merged_data['total_cs'], merged_data['game_length']),
        "gpm": lambda: gold_per_minute(merged_data['gold_per_match'], merged_data['game_length'])
    }

    for key, value in function_dictionary.items():
        merged_data.insert( len(merged_data.columns), key, value())

    merged_data_champions = merged_data.merge(champion_data, on='id', how='left')
    #print(pd.DataFrame(merged_data_champions)[['total_cs', 'kda', 'gold_per_match', 'game_length', 'winrate', 'csm', 'gpm', 'name']])
    selected_columns = ['name', 'play', 'win', 'lose', 'winrate', 'kda', 'kill', 'death', 'assist', 'total_cs', 'csm', 'gold_per_match', 'gpm', 'game_length']
    completed_table = pd.DataFrame(merged_data_champions)[selected_columns]
    completed_table.loc[0, 'name'] = "All Champions"
    #print(completed_table)
    print("Champion Stats: ")
    return completed_table

# Get Ranked Stats and filter for current season
def get_ranked_data(seasons_df, season_input, data, reorder):
    seasons_df = seasons_df.rename(columns={'season_id': 'id'})
    #print(reorder)

    # why isnt the current season in the seasons_df already? idk
    #if not reorder['id'].isin([season_input]).any():
    if season_input == reorder.iloc[0, 0]:
        season_stats = pd.DataFrame(data['props']['pageProps']['data']['league_stats'])[['tier_info']]
        solo_stats, flex_stats = season_stats.iloc[0, 0], season_stats.iloc[1, 0]
        solo_df, flex_df = pd.DataFrame([solo_stats]), pd.DataFrame([flex_stats])
        print("SoloQ Stats: ")
        print(solo_df[['tier', 'division', 'lp']])
        print("FlexQ Stats: ")
        print(flex_df[['tier', 'division', 'lp']])
        return
    
    print("SoloQ Stats: ")
    player_rank = seasons_df[['tier', 'division']].loc[seasons_df['id'] == season_input]
    if player_rank.empty:
        print("OPGG didnt store the rank? not my fault")
    else:
        print(player_rank.to_string())

# Overhauled Backend
def get_summoner_stats(player_name, region_id):
    # If Summoner Exists then move forward, else return to get_summoner_name()
    try:
        url = f'https://www.op.gg/summoners/{region_id}/{player_name}/champions'

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0'}
        soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')

        data = soup.select_one('#__NEXT_DATA__').text
        data = json.loads(data)

        # Check if Summoner ID is Valid
        summoner_id = data['props']['pageProps']['data']['summoner_id']
        champion_data = pd.DataFrame(data['props']['pageProps']['data']['champions'])[['id', 'name', 'image_url']]
    
    except:
        print(f"Error: {player_name} is not a valid summoner name.")
        return get_summoner_name()

    # Create List of all Seasons
    season_ids = data['props']['pageProps']['data']['seasons']
    season_df = pd.DataFrame(season_ids)[['id', 'value', 'display_value', 'split', 'season', 'is_preseason']]
    season_df_reorder = season_df[~season_df.is_preseason].loc[:: -1]
    #print(season_df[~season_df.is_preseason].loc[:: -1])

    # Create List of all Played Seasons
    seasons_played = data['props']['pageProps']['data']['previous_seasons']
    tier_info = dict_from_list(pd.DataFrame(seasons_played)['tier_info'])
    seasons_played_df = pd.concat([ pd.DataFrame(seasons_played)['season_id'] , pd.DataFrame(tier_info)], axis=1)
    #print(seasons_played_df)

    '''previous_seasons_data = data['props']['pageProps']['data']['previous_season_tiers']
    current_season_tier = data['props']['pageProps']['data']['current_season_high_tiers']
    print(pd.DataFrame(previous_seasons_data))
    print(current_season_tier)'''

    # Check if Applicable Data Exists
    while True:
        try:
            season_input = int(input("Enter Season ID (1 2 3 4 5 6 7 11 13 15 17 19 21 23 25 27 29 31): "))
            game_type_input = input("Enter Gamemode (RANKED, SOLORANKED, FLEXRANKED): ")

            # Swap API dependant on Season Input Value
            if season_input <= 27:
                api_version = f'https://lol-web-api.op.gg/api/v1.0/internal/bypass/summoners'
                stats_string = 'champion_stats'
            else:
                api_version = f'https://lol-web-api.op.gg/api/v1.0/internal/bypass/summoners/v2'
                stats_string = 'my_champion_stats'

            # Bundle API Call
            opgg_api_call = f'{api_version}/{region_id}/{summoner_id}/most-champions/rank?game_type={game_type_input}&season_id={season_input}'
            api_request = requests.get(opgg_api_call)
            api_json = json.loads(api_request.text)
            api_data = api_json['data'][stats_string]
            break  

        except ValueError:
            print("Invalid Season ID. Please enter a valid integer.")

        except TypeError:
            print(f"No Data for Season: {season_input}.")

    # Grab Season Name (i.e. 15 = S2025) 
    display_season = season_df.loc[season_df['id'] == season_input, 'display_value'].to_string(index=False)

    '''is_split = season_df.loc[season_df['id'] == season_input, 'split']
    is_split_string = is_split.to_string(index=False)
    print(is_split_string)
    if is_split_string != "NaN":
        print("Split Detected")'''
    
    # Output dependant on Season Input
    if season_input <= 27:
        print(f"{player_name}'s Season {display_season} Stats:")
        get_ranked_data(seasons_played_df, season_input, data, season_df_reorder)
        print(v1_api_champion_stats(api_data, champion_data))
    else:
        print(f"{player_name}'s Season {display_season} Stats:")
        get_ranked_data(seasons_played_df, season_input, data, season_df_reorder)
        print(v2_api_champion_stats(api_data, champion_data))

'''# Select Region
def get_region():
    region_ids = {'na', 'euw', 'kr', 'eune', 'oce', 'jp', 'br', 'lan', 'las', 'tr', 'sea', 'tw', 'vn', 'me', 'ru'}
    selected_region = None

    while selected_region not in region_ids:
        selected_region = input(f"Enter Region Code ({region_ids}): ")
        if selected_region not in region_ids:
            print("Invalid input. Please input a valid region code.")

    return selected_region'''

# Get Summoner Name
def get_summoner_name():
    # When times were simple
    #summoner_name = input("Enter Summoner Name: ")
    #get_summoner_stats(summoner_name)

    # Terrible Spot for Region_Id
    region_id = 'na'#get_region()
    names_input = input("Enter Summoner Name: ").split(",")

    for summoner_name in names_input:
        # Remove Leading/Trailing Whitespace and Replace # with -
        summoner_name = summoner_name.lstrip().rstrip().replace("#", "-")
        get_summoner_stats(summoner_name, region_id)
    # Loop Program | Ctrl + C to Exit
    get_summoner_name()

# Main
if __name__ == '__main__':
    get_summoner_name()
