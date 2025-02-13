#import math
#import sys
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

# Get Summoner Stats
def get_summoner_stats(player_name):
    # If Summoner Exists then move forward, else return to get_summoner_name()
    try:
        url = f'https://www.op.gg/summoners/na/{player_name}/champions'

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0'}
        soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')

        # Get Data Keys
        data = soup.select_one('#__NEXT_DATA__').text
        data = json.loads(data)

        # Check if Summoner ID is Valid
        data['props']['pageProps']['data']['summoner_id']
    except:
        print(f"Error: {player_name} is not a valid summoner name.")
        return get_summoner_name()

    # Look at Data Keys - Debugging
    #print(data['props']['pageProps']['data'].keys())

    # Get Champion Stats
    #champion_stats = data['props']['pageProps']['data']['most_champions']['champion_stats']
    try:
        champion_stats = data['props']['pageProps']['data']['most_champions']['champion_stats']
    except:
        print(f"Error: {player_name} has no ranked data.")
        return get_summoner_name()
    #print(champion_stats)

    #test = pd.DataFrame(data['props']['pageProps']['data']['league_stats'])
    #print(test['tier_info'])

    # Get Ranked Stats
    #league_stats = pd.DataFrame(data['props']['pageProps']['data']['league_stats'])
    # tier, division, lp, level, tier_image_url, border_image_url
    #ranked_stats = league_stats[['tier_info']]
    ranked_stats = pd.DataFrame(data['props']['pageProps']['data']['league_stats'])[['tier_info']]

    # .iloc[row, column]
    solo_stats = ranked_stats.iloc[0, 0]
    flex_stats = ranked_stats.iloc[1, 0]
    solo_df = pd.DataFrame([solo_stats])
    flex_df = pd.DataFrame([flex_stats])

    print(f"{player_name} SoloQ Stats:")
    print(solo_df[['tier', 'division', 'lp']])
    #print(solo_df[['tier_image_url']])
    print(f"{player_name} FlexQ Stats:")
    print(flex_df[['tier', 'division', 'lp']])
    #print(flex_df[['tier_image_url']])

    # Champion-Stats Data Frame
    cs_selected_columns = ['id', 'play', 'win', 'lose', 'kill', 'death', 'assist']
    cs_df = pd.DataFrame(champion_stats)
    #print(cs_df[selected_columns])

    cs_df_container = cs_df[cs_selected_columns]
    # Reminder: Keys that use Newly Created Columns must use their Parent Container
    # Example: cs_df_container['cs'] instead of cs_df['cs']
    cs_df_dictionary = {
        "cs": lambda: average_cs(cs_df['minion_kill'], cs_df['neutral_minion_kill'], cs_df['play']),
        "kda": lambda: kda_ratio(cs_df['kill'], cs_df['death'], cs_df['assist']),
        "gold": lambda: average_gold(cs_df['gold_earned'], cs_df['play']),
        "game_length": lambda: average_game_length(cs_df['game_length_second'], cs_df['play']),
        "csm": lambda: cs_per_minute(cs_df_container['cs'], cs_df_container['game_length']),
        "gpm": lambda: gold_per_minute(cs_df_container['gold'], cs_df_container['game_length']),
        "winrate": lambda: win_rate(cs_df['win'], cs_df['play'])
    }
    for key, value in cs_df_dictionary.items():
        cs_df_container.insert( len(cs_df_container.columns), key, value())
    #print(cs_df_container)
    
    # Champion-Data Data Frame
    champion_data = data['props']['pageProps']['data']['champions']
    #cd_selected_columns = ['id', 'name']
    cd_df_container = pd.DataFrame(champion_data)[['id', 'name', 'image_url']]
    #print(cd_df_container)

    # Merge Data Frames
    merged_container = cs_df_container.merge(cd_df_container, on='id', how='left')
    #print(merged_container[['name', 'play', 'win', 'lose', 'kill', 'death', 'assist', 'cs']])
    print(f"{player_name} Stats:")
    print(merged_container[['name', 'play', 'win', 'lose', 'winrate', 'kda', 'kill', 'death', 'assist', 'cs', 'csm', 'gold', 'gpm', 'game_length']])
    
    #print(merged_container[['image_url']])
    #print(type(merged_container.at[0, 'death']))
    
    #get_summoner_name()

# Get Summoner Name
def get_summoner_name():
    #summoner_name = input("Enter Summoner Name: ")
    #get_summoner_stats(summoner_name)
    names_input = input("Enter Summoner Name: ").split(",")
    for summoner_name in names_input:
        # Remove Leading/Trailing Whitespace and Replace # with -
        summoner_name = summoner_name.lstrip().rstrip().replace("#", "-")
        get_summoner_stats(summoner_name)
    # Loop Program
    # Ctrl + C to Exit
    get_summoner_name()

# Main
if __name__ == '__main__':
    get_summoner_name()
