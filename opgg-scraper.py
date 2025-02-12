import math
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from calc import *

# Get Summoner Stats
def get_summoner_stats(player_name):
    #player_name = 'Budwolf-NA1'
    #url = 'https://www.op.gg/summoners/na/Budwolf-NA1/champions'
    url = f'https://www.op.gg/summoners/na/{player_name}/champions'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')

    # Get Data Keys
    data = soup.select_one('#__NEXT_DATA__').text
    data = json.loads(data)
    # Look at Data Keys - Debugging
    #print(data['props']['pageProps']['data'].keys())

    # Get Champion Stats
    champion_stats = data['props']['pageProps']['data']['most_champions']['champion_stats']
    #print(champion_stats)

    # Champion-Stats Data Frame
    cs_selected_columns = ['id', 'play', 'win', 'lose', 'kill', 'death', 'assist']
    cs_df = pd.DataFrame(champion_stats)
    #print(cs_df[selected_columns])

    cs_df_container = cs_df[cs_selected_columns]
    #cs_df_container.insert(len(cs_df_container.columns), 'cs', (cs_df['minion_kill'] + cs_df['neutral_minion_kill']) / cs_df['play'] )
    cs_df_container.insert( len(cs_df_container.columns), 'cs', average_cs(cs_df['minion_kill'], cs_df['neutral_minion_kill'], cs_df['play']) )
    cs_df_container.insert( len(cs_df_container.columns), 'kda', kda_ratio(cs_df['kill'], cs_df['death'], cs_df['assist']) )
    cs_df_container.insert( len(cs_df_container.columns), 'gold', average_gold(cs_df['gold_earned'], cs_df['play']) )
    cs_df_container.insert( len(cs_df_container.columns), 'game_length', average_game_length(cs_df['game_length_second'], cs_df['play']) )
    cs_df_container.insert( len(cs_df_container.columns), 'csm', cs_per_minute(cs_df_container['cs'], cs_df_container['game_length']) )
    cs_df_container.insert( len(cs_df_container.columns), 'gpm', gold_per_minute(cs_df_container['gold'], cs_df_container['game_length']) )
    cs_df_container.insert( len(cs_df_container.columns), 'winrate', win_rate(cs_df_container['win'], cs_df_container['play']) )
    #cs_df_container.insert(len(cs_df_container.columns), 'name', '' )
    #print(cs_df_container)

    # Champion-Data Data Frame
    champion_data = data['props']['pageProps']['data']['champions']
    #cd_selected_columns = ['id', 'name']
    cd_df_container = pd.DataFrame(champion_data)[['id', 'name']]
    #print(cd_df_container)

    # Merge Data Frames
    merged_container = cs_df_container.merge(cd_df_container, on='id', how='left')
    #print(merged_container[['name', 'play', 'win', 'lose', 'kill', 'death', 'assist', 'cs']])
    print(f"{player_name} Stats:")
    print(merged_container[['name', 'play', 'win', 'lose', 'winrate', 'kda', 'kill', 'death', 'assist', 'cs', 'csm', 'gold', 'gpm', 'game_length']])

    # Loop Program
    # Ctrl + C to Exit
    get_summoner_name()

# Get Summoner Name
def get_summoner_name():
    #summoner_name = input("Enter Summoner Name: ")
    #get_summoner_stats(summoner_name)
    names_input = input("Enter Summoner Name: ").split(",")
    for summoner_name in names_input:
        # Remove Leading/Trailing Whitespace and Replace # with -
        summoner_name = summoner_name.lstrip().rstrip().replace("#", "-")
        get_summoner_stats(summoner_name)

# Main
if __name__ == '__main__':
    get_summoner_name()
